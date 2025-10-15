from ldx.generic.config_init import CONFIG_DIR
from ldx.utils.json import touch_json


LD_CONFIG_DIR = CONFIG_DIR / "ld" 

LD_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

LD_CONFIG_FILE = LD_CONFIG_DIR / "config.json"

LD_CONFIG = touch_json(LD_CONFIG_FILE, default_data={"path" : []})