from irc_constants import IRCConstants

class IRCMsgType(object):
    regular = 0x0
    command = 0x1
    private = 0x2

class IRCMsg(object):
    def __init__(self, user = '', channel = '', msg = '', msg_type = 0):
        self.user       = user
        self.channel    = channel
        self.msg        = msg
        self.msg_type   = msg_type      

    def _is_cmd(self):
        return self.msg_type & IRCMsgType.command

    def _is_private(self):
        return self.msg_type & IRCMsgType.private

    is_cmd      = property(_is_cmd)
    is_private  = property(_is_private)
    

class IRCMsgParser(object):
    def __init__(self,irc):
        self.irc = irc

    def parser(self, user, channel, msg):
        pm = IRCMsg(
            user     = user,                                        \
            channel  = channel,                                     \
            msg      = msg,                                         \
            msg_type = self.is_cmd(msg) | self.is_private(channel)  \
        )
    
        return pm


    def is_cmd(self, msg):
        if msg[0] == IRCConstants.command_prefix:
            return IRCMsgType.command
        return 0

    def is_private(self,channel):
        if channel == self.irc.nickname:
            return IRCMsgType.private
        return 0


