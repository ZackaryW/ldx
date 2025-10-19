from dataclasses import dataclass


@dataclass
class ScheduleConfig:
    """
    Independent scheduling configuration component.
    Not a plugin - just metadata for the runner to interpret.
    """
    trigger: str = None  # "cron" or "interval"
    
    # Cron-style scheduling
    hour: int = None
    minute: int = 0
    second: int = 0
    day_of_week: str = "*"
    day: int = "*"
    
    # Interval-style scheduling
    interval_seconds: int = None
    
    def __post_init__(self):
        if not self.trigger:
            raise ValueError("trigger must be specified for Schedule configuration.")
        
        if self.trigger == "cron" and self.hour is None:
            raise ValueError("hour must be specified for cron trigger.")
        
        if self.trigger == "interval" and not self.interval_seconds:
            raise ValueError("interval_seconds must be specified for interval trigger.")
    
    def to_apscheduler_config(self) -> dict:
        """Convert to APScheduler job configuration"""
        if self.trigger == "cron":
            schedule_config = {
                'trigger': 'cron',
                'hour': self.hour,
                'minute': self.minute,
                'second': self.second,
                'day_of_week': self.day_of_week
            }
            if self.day != "*":
                schedule_config['day'] = self.day
            return schedule_config
        else:
            return {
                'trigger': 'interval',
                'seconds': self.interval_seconds
            }
