from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from ldx.ldx_runner.core.plugin import PluginMeta
from ldx.ldx_runner.core.schedule import ScheduleConfig
import logging


class FlaskLDXRunner:
    """
    Flask-integrated runner with APScheduler support.
    Plugins with schedules are executed by APScheduler.
    Plugins without schedules are ignored in server mode.
    """
    
    def __init__(self, app: Flask, config: dict):
        self.app = app
        self.config = config
        self.scheduler = BackgroundScheduler(
            executors={'default': ThreadPoolExecutor(max_workers=10)},
            job_defaults={
                'coalesce': True,      # Combine missed runs
                'max_instances': 1     # Only one instance per job
            }
        )
        self.plugins = []
    
    def load_plugins(self):
        """Load plugins and check if config has a schedule"""
        # First, check if there's a schedule in the config (as independent component)
        schedule_data = self.config.get("schedule")
        schedule_config = None
        
        if schedule_data:
            schedule_config = ScheduleConfig(**schedule_data)
        
        # Load all plugins (excluding schedule since it's not a plugin anymore)
        for env_key, plugin_config in self.config.items():
            if env_key == "schedule":
                continue  # Skip - it's a component, not a plugin
                
            plugin_cls = PluginMeta._type_registry.get(env_key)
            if not plugin_cls:
                continue
            
            plugin = plugin_cls()
            plugin.onEnvLoad(plugin_config)
            self.plugins.append(plugin)
        
        # If there's a schedule, register the entire config execution with APScheduler
        if schedule_config:
            schedule = schedule_config.to_apscheduler_config()
            logging.info(f"Registering scheduled execution: {schedule}")
            
            # Schedule execution of ALL plugins
            self.scheduler.add_job(
                func=self._execute_all_plugins,
                **schedule,
                id="scheduled_execution",
                name="Scheduled Plugin Execution"
            )
    
    def _execute_all_plugins(self):
        """Execute all plugins in the config as a single atomic unit"""
        if not self.plugins:
            logging.info("No plugins to execute")
            return
        
        # Check if ALL plugins can run - if any fails, abort execution
        if not all(p.canRun(self.config) for p in self.plugins):
            logging.warning("Not all plugins can run - aborting scheduled execution")
            return
        
        logging.info(f"Starting scheduled execution of {len(self.plugins)} plugins")
        
        try:
            # Startup phase - start ALL plugins
            for plugin in self.plugins:
                plugin.onStartup(self.config)
            
            # Event loop - run until any plugin says stop
            import time
            while True:
                if any(p.shouldStop(self.config) for p in self.plugins):
                    break
                time.sleep(1)
                
        finally:
            # Shutdown phase - shutdown ALL plugins
            for plugin in self.plugins:
                plugin.onShutdown(self.config)
        
        logging.info("Scheduled execution completed")
    
    def start(self):
        """Start the scheduler"""
        self.load_plugins()
        self.scheduler.start()
        logging.info(f"Scheduler started with {len(self.scheduler.get_jobs())} jobs")
    
    def stop(self):
        """Stop the scheduler and wait for jobs to complete"""
        self.scheduler.shutdown(wait=True)
        logging.info("Scheduler stopped")
