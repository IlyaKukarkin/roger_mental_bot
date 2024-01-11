from singleton import SingletonClass


class App_Settings(object):
    def __init__(self):
        settings = SingletonClass().collection_name["app_settings"]

        self.settings = settings

    def get_app_settings(self):
        return self.settings.find_one()
