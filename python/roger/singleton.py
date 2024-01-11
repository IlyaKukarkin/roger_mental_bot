# From https://python-patterns.guide/gang-of-four/singleton/
"Singleton for app_settings"


class SingletonClass():
    "it's just a singleton class for app_settings"
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonClass, cls).__new__(cls)
        return cls.instance
