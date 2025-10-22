"""
Flask-integrated runner - thin wrapper around SchedulerService.

This module provides Flask integration for the LDX scheduler service.
It integrates with LDXRunner to auto-load configs from ~/.ldx/runner/configs/
and schedule them based on their schedule section.
"""

from flask import Flask
from ldx.ldx_server.scheduler import SchedulerService
from ldx.ldx_server.registry import JobRegistry
from ldx.ldx_runner.core.runner import LDXRunner
from ldx.ldx_runner.core.schedule import ScheduleConfig
from pathlib import Path
import logging


class FlaskLDXRunner:
    """
    Flask-integrated runner with APScheduler support.
    
    This wrapper:
    - Provides Flask app integration
    - Manages scheduler lifecycle
    - Auto-loads configs from ~/.ldx/runner/configs/ on startup
    - Schedules configs that have a schedule section
    - Exposes scheduler service for routes (dynamic scheduling)
    """
    
    def __init__(self, app: Flask, max_workers: int = 10):
        """
        Initialize Flask runner with scheduler service.
        
        Args:
            app: Flask application instance
            max_workers: Maximum number of concurrent job workers
        """
        self.app = app
        self.registry = JobRegistry()
        self.scheduler_service = SchedulerService(max_workers=max_workers, registry=self.registry)
        self.ldx_runner = LDXRunner()
        
        # Store reference in app context for routes
        app.config['SCHEDULER_SERVICE'] = self.scheduler_service
    
    def load_configs_from_directory(self):
        """
        Load all .toml configs from ~/.ldx/runner/configs/ and register them.
        
        This method:
        1. Finds all .toml files (excluding global.toml and *.template.toml)
        2. Creates LDXInstance for each via LDXRunner
        3. Checks if config has a 'schedule' section
        4. If schedule exists: Scheduled automatically
        5. If no schedule: Registered as on-demand job (trigger via API)
        """
        config_dir = self.ldx_runner._LDXRunner__ldx_dir
        
        # Find all config files (exclude global and templates)
        config_files = [
            f for f in config_dir.glob("*.toml")
            if f.name != "global.toml" and not f.name.endswith(".template.toml")
        ]
        
        logging.info(f"Loading {len(config_files)} config files from {config_dir}")
        
        for config_file in config_files:
            try:
                # Create instance using LDXRunner (handles global config, templates, etc)
                instance = self.ldx_runner.create_instance(config_file.name)
                
                # Load plugins into the instance
                instance.load_plugins()
                
                # Extract schedule using LDXRunner utility method
                schedule_config = LDXRunner.extract_schedule(instance.config)
                
                # Use filename (without .toml) as job_id
                job_id = config_file.stem
                
                # Register the job (with or without schedule)
                result = self.scheduler_service.schedule_job(
                    job_id=job_id,
                    instance_or_config=instance,
                    schedule_config=schedule_config,
                    replace_existing=True  # Allow server restarts to replace jobs
                )
                
                # Update registry source to indicate config file origin
                if self.registry.exists(job_id):
                    entry = self.registry.get(job_id)
                    entry.source = f"config:{config_file.name}"
                
                if schedule_config:
                    logging.info(f"Scheduled job '{job_id}' from {config_file.name}: {result}")
                else:
                    logging.info(f"Registered on-demand job '{job_id}' from {config_file.name}: {result}")
                
            except Exception as e:
                logging.error(f"Failed to load config {config_file.name}: {e}", exc_info=True)
    
    def schedule_config_job(self, job_id: str, config: dict) -> dict:
        """
        Schedule a job from a complete configuration dict.
        
        This is a convenience method for scheduling jobs that include
        both plugins and an optional schedule component.
        
        Args:
            job_id: Unique identifier for the job
            config: Full configuration dict (may include 'schedule' key)
            
        Returns:
            Job info dict
        """
        # Extract schedule using LDXRunner utility method
        schedule_config = LDXRunner.extract_schedule(config)
        
        # Schedule the job
        return self.scheduler_service.schedule_job(
            job_id=job_id,
            config=config,
            schedule_config=schedule_config
        )
    
    def start(self):
        """Start the scheduler and load configs from directory"""
        self.load_configs_from_directory()
        self.scheduler_service.start()
        logging.info("Flask runner started")
    
    def stop(self):
        """Stop the scheduler and wait for jobs to complete"""
        self.scheduler_service.stop()
        logging.info("Flask runner stopped")
