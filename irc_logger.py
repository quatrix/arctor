class IRCLogger(object):
    """ 
    abstract IRC Logger class
    subclass must implement:
    log_start, log_stop,log 
    """
    def __init__(self, irc):
        self.irc                = irc
        self.logged_channels    = {}
    
    def log_start(self, channel, user):
        raise NotImplementedError 

    def log_stop(self, channel):
        raise NotImplementedError 

    def log(self, user, channel, msg):
        raise NotImplementedError 


