"""
Flask application server for LDX scheduler.

This module creates and configures the Flask application with
the scheduler service and routes.

Example usage:
    python -m ldx.ldx_server.server
    
Or programmatically:
    from ldx.ldx_server.server import create_app
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
"""

from flask import Flask
from ldx.ldx_server.flask_runner import FlaskLDXRunner
from ldx.ldx_server.routes import scheduler_bp
import logging


def create_app(config: dict = None, max_workers: int = 10) -> Flask:
    """
    Create and configure Flask application with scheduler service.
    
    Args:
        config: Optional initial configuration dict (not commonly used - 
                jobs are typically scheduled via API)
        max_workers: Maximum number of concurrent job workers
        
    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize Flask runner (which creates scheduler service)
    runner = FlaskLDXRunner(app, max_workers=max_workers)
    
    # Register routes
    app.register_blueprint(scheduler_bp)
    
    # Store runner in app context
    app.config['FLASK_RUNNER'] = runner
    
    # Start scheduler on app startup (loads configs from ~/.ldx/runner/configs/)
    @app.before_request
    def start_scheduler():
        """Start scheduler and load configs on first request"""
        if not hasattr(app, '_scheduler_started'):
            logging.info("Starting scheduler and loading configs from ~/.ldx/runner/configs/")
            runner.start()  # This calls load_configs_from_directory() then starts scheduler
            app._scheduler_started = True
    
    # Register shutdown handler for when Flask process terminates
    import atexit
    atexit.register(lambda: runner.stop() if hasattr(app, '_scheduler_started') and app._scheduler_started else None)
    
    logging.info("Flask application created and configured")
    return app


def main():
    """
    Main entry point for running the server.
    
    Environment variables:
        FLASK_HOST: Host to bind to (default: 0.0.0.0)
        FLASK_PORT: Port to bind to (default: 5000)
        FLASK_DEBUG: Enable debug mode (default: False)
        MAX_WORKERS: Maximum concurrent job workers (default: 10)
    """
    import os
    
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    max_workers = int(os.environ.get('MAX_WORKERS', 10))
    
    app = create_app(max_workers=max_workers)
    
    logging.info(f"Starting LDX scheduler server on {host}:{port}")
    logging.info(f"Debug mode: {debug}")
    logging.info(f"Max workers: {max_workers}")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
