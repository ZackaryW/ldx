
class PluginMeta(type):
    _type_registry = {}

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if name != "LDXPlugin":
            cls._type_registry[new_class.__env_key__] = new_class
        return new_class


class LDXPlugin(metaclass=PluginMeta):
    __env_key__ :  str = None


    def onEnvLoad(self, env : dict):
        pass

    def onStartup(self, cfg : dict, instance):
        pass

    def canRun(self, cfg : dict, instance) -> bool:
        return True
    
    def shouldStop(self, cfg : dict, instance) -> bool:
        return False
    
    def onShutdown(self, cfg : dict, instance):
        pass
    
    def getSchedule(self) -> dict | None:
        # exclusive method for schedule to return 

        return None

    

    