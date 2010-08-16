from twisted.words.protocols import irc
from twisted.internet import protocol

class IRCMsgType:
    command = 1
    regular = 2

class IRCMsg:
    def __init__(self, user, channel, msg):
        self.user       = self.short_username(user)
        self.msg_type   = self.parse_msg(msg)         
        self.channel    = channel
        self.msg        = msg

    def short_username(self, user):
        return user.split('!',1)[0]

    def get_cmd(self):
        return self.msg[1:].split(' ',1)[0]
    
    def parse_msg(self, msg):
        if msg[0] == '!':
            return IRCMsgType.command
        else:
            return IRCMsgType.regular


class IRCCommandHandler:
    def handle(self, pm):
        try:
            return getattr(self, "cmd_" + pm.get_cmd())(pm)
        except AttributeError:
            return "no such command"

    def cmd_echo(self, pm):
        return pm.user + " said " + pm.msg

    def cmd_rand(self, pm):
        return "random number: 5"

        
    

class Arctor(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def privmsg(self, user, channel, msg):
        pm = IRCMsg(user, channel, msg)

        if pm.msg_type == IRCMsgType.command:
            response = self.factory.handle_command.handle(pm)
    
            if response:
                self.msg(channel, response)

class ArctorFactory(protocol.ClientFactory):
    protocol = Arctor

    def __init__(self, channel, nickname):
        self.channel = channel
        self.nickname = nickname
        self.handle_command = IRCCommandHandler()

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
    reactor.connectTCP('irc.freenode.net', 6667, ArctorFactory('#' + chan, nick))
    reactor.run()

