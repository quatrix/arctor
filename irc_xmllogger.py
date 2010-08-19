from irc_logger import IRCLogger
import time

class IRCXMLLoggerException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class IRCXMLLogger(IRCLogger):
    def xml_time(self):
        return time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime())

    def log_filename(self, channel):
        log_dir     = self.irc.factory.bot_config["logdir"]
        return "%s/%s-%s.xml" % (log_dir, self.xml_time(), channel) 

        
    def logfile_open(self, channel):
        try:
            self.logged_channels[channel] = open(self.log_filename(channel), "w")
        except IOError as (errno, strerror):
            raise IRCXMLLoggerException("error starting log: %s" % strerror)

    def logfile_close(self, channel):
        try:
            self.logged_channels[channel].close()
            del self.logged_channels[channel]
        except KeyError:
            raise IRCXMLLoggerException("channel isn't being logged")
        

    def log_channel(self, channel, msg):
        if channel in self.logged_channels:
            try:
                self.logged_channels[channel].write(msg)
            except IOError as (errno, strerror):
                self.stop_logger(channel)
                raise IRCXMLLoggerException("failed to write to log: %s" % strerror)
        

    def log_header(self, channel, user):
        return "<arcbot>\n<details><date>%s</date><operator>%s<operator></details>\n<body>\n" % (self.xml_time(), user.nick)

    def log_footer(self):
        return "</body></arcbot>\n"

    def msg_to_xml(self, user, msg):
        return "<log><sender>%s</sender><time>%s</time><msg>%s</msg></log>\n" % (user.nick, self.xml_time(), msg)

    def log_start(self, channel, user):
        if channel in self.logged_channels:
            raise IRCXMLLoggerException("logging already started for this channel")

        self.logfile_open(channel)
        self.log_channel(channel, self.log_header(channel, user))
            

    def log_stop(self, channel):
        self.log_channel(channel, self.log_footer())
        self.logfile_close(channel)

    def log(self, user, channel, msg):
        self.log_channel(channel, self.msg_to_xml(user, msg))
            
