# From https://python-patterns.guide/gang-of-four/singleton/

class SingletonClass(object):
  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(SingletonClass, cls).__new__(cls)
    return cls.instance

class Bot(object):
    def __init__(self):
        bot = SingletonClass().bot
        dispatcher = SingletonClass().dispatcher

        self.bot = bot
        self.dispatcher = dispatcher

    def get_bot(self):
        return self.bot

    def get_dispatcher(self):
        return self.dispatcher
