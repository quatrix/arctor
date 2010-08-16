from twisted.words.protocols import irc
from twisted.internet import protocol

class IRCMsgType:
    command = 1
    regular = 2

class IRCConstants:
    command_delimiter   = '!'
    username_delimiter  = '!'

class IRCMsg:
    def __init__(self, user, channel, msg):
        self.user       = self.short_username(user)
        self.msg_type   = self.parse_msg(msg)         
        self.channel    = channel
        self.msg        = msg

    def short_username(self, user):
        return user.split(IRCConstants.username_delimiter,1)[0]

    def get_cmd(self):
        return self.msg[1:].split(' ',1)[0]
    
    def parse_msg(self, msg):
        if msg[0] == IRCConstants.command_delimiter:
            return IRCMsgType.command
        else:
            return IRCMsgType.regular


class IRCCommandHandler:
    def __init__(self, irc):
        self.irc = irc

    def handle(self, pm):
        try:
            self.pm = pm
            return getattr(self, "cmd_" + pm.get_cmd())(pm)
        except AttributeError:
            return "no such command"

    def msg_channel(self, msg):
        self.irc.msg(self.pm.channel, msg)

    def cmd_echo(self, pm):
        self.msg_channel(pm.user + " said " + pm.msg)

    def cmd_rand(self, pm):
        self.msg_channel("random number: 5")

    

class IRCBot(irc.IRCClient):
    def __init__(self):
        self.handle_command = IRCCommandHandler(self)

    def privmsg(self, user, channel, msg):
        pm = IRCMsg(user, channel, msg)

        if pm.msg_type == IRCMsgType.command:
           self.handle_command.handle(pm)

class IRCBotFactory(protocol.ClientFactory):
    protocol = IRCBot

    def __init__(self, channel, nickname):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)


import sys
from twisted.internet import reactor

if __name__ == "__main__":
    chan = sys.argv[1]
    nick = sys.argv[2]
    reactor.connectTCP('irc.freenode.net', 6667, IRCBotFactory('#' + chan, nick))
    reactor.run()

