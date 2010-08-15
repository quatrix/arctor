from twisted.words.protocols import irc
from twisted.internet import protocol

class Arctor(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def short_username(self, user):
        return user.split('!',1)[0]

    def privmsg(self, user, channel, msg):
		m = self.short_username(user) + " said " + msg
		self.msg(channel, m)

class ArctorFactory(protocol.ClientFactory):
    protocol = Arctor

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
    reactor.connectTCP('irc.freenode.net', 6667, ArctorFactory('#' + chan, nick))
    reactor.run()

