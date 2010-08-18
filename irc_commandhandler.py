from irc_msgparser import IRCMsg
from irc_userbuilder import IRCUserType
from irc_logger         import IRCXMLLogger, IRCXMLLoggerException

class IRCCmd(IRCMsg):
    def get_cmd(self):
        return self.msg[1:].split()[0]

    def get_cmd_args(self):
        return self.msg[1:].split()[1:]

    def get_cmd_args_str(self):
        return " ".join(self.get_cmd_args())


class IRCCommandDispacher(object):
    def __init__(self, irc):
        self.irc = irc

    def handle(self, pm):
        pm.__class__    = IRCCmd
        self.pm         = pm

        try:
            cmd_ptr = getattr(self, "cmd_" + pm.get_cmd())
        except AttributeError:
            self.send_reply("no such command")
            return 

        return cmd_ptr(pm)

    def send_reply(self, msg):
        if self.pm.is_private:
            self.irc.msg(self.pm.user.nick, msg)
        else:
            self.irc.msg(self.pm.channel, msg)

    def user_type_above(self, user_type):
        if self.pm.user.user_type >= user_type:
           return 1
        return 0
           
        

class IRCCommandHandler(IRCCommandDispacher):
    def cmd_echo(self, pm):
        self.send_reply("%s said %s" % (pm.user.nick, pm.get_cmd_args_str()))

    def cmd_rand(self, pm):
        self.send_reply("random number: 5")

    def cmd_login(self, pm):
        if pm.user.validate_password(pm.get_cmd_args()[0]):
            self.send_reply("login successful, your type is %d" % pm.user.user_type)
        else:
            self.send_reply("login failed")
        
    def cmd_topic(self, pm):
        if self.user_type_above(IRCUserType.admin):
            self.irc.topic(pm.channel, pm.get_cmd_args_str())

    def cmd_mytype(self, pm):
        self.send_reply("%s is type: %d" % (pm.user.nick, pm.user.user_type))
            
    def cmd_log_start(self, pm):
        try:
            self.irc.xml_logger.start_logger(pm.channel, pm.user)
            self.send_reply("logging of %s started" % pm.channel)
        except IRCXMLLoggerException as e:
            self.send_reply(e.value)

    def cmd_log_stop(self, pm):
        try:
            self.irc.xml_logger.stop_logger(pm.channel)
            self.send_reply("logging of %s stopped" % pm.channel)
        except IRCXMLLoggerException as e:
            self.send_reply(e.value)

