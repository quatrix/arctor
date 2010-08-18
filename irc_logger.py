import time

class IRCXMLLoggerException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class IRCXMLLogger(object):
    def __init__(self, irc):
        self.irc                = irc
        self.logged_channels    = {}
    
    def time_long(self):
        return time.strftime("%y%m%d_%H%M%S",time.localtime())

    def start_logger(self, channel, log_name):
        log_dir     = self.irc.factory.bot_config["logdir"]
        log_filename = "%s/%s-%s-%s.xml" % (log_dir, self.time_long(), channel, log_name) 

        if channel in self.logged_channels:
            raise IRCXMLLoggerException("logging already started for this channel")

        try:
            self.logged_channels[channel] = open(log_filename, "w")
        except IOError as (errno, strerror):
            raise IRCXMLLoggerException("error starting log: %s" % strerror)

    def stop_logger(self, channel):
        try:
            self.logged_channels[channel].close()
            del self.logged_channels[channel]
        except KeyError:
            raise IRCXMLLoggerException("channel isn't being logged")

    def msg_to_xml(self, user, msg):
        return "<ts>%s</ts><u>%s</u><m>%s</m>\n" % (str(time.time()), user.nick, msg)
        

    def log(self, user, channel, msg):
            if channel in self.logged_channels:
                try:
                    self.logged_channels[channel].write(self.msg_to_xml(user, msg))
                except IOError as (errno, strerror):
                    self.stop_logger(channel)
                    raise IRCXMLLoggerException("failed to write to log: %s" % strerror)
            
