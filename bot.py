from twisted.words.protocols import irc
from twisted.internet import protocol
import yaml

from irc_userbuilder    import IRCUserBuilder
from irc_commandhandler import IRCCommandHandler
from irc_msgparser      import IRCMsgParser
from irc_constants      import IRCConstants
from irc_logger         import IRCXMLLogger, IRCXMLLoggerException


class IRCBot(irc.IRCClient):
    def __init__(self):
        self.handle_command = IRCCommandHandler(self)
        self.user_builder   = IRCUserBuilder(self)
        self.msg_parser     = IRCMsgParser(self)
        self.xml_logger     = IRCXMLLogger(self)

    def _get_nickname(self):
        return self.factory.bot_config["nickname"]
    nickname = property(_get_nickname)

    def signedOn(self):
        for channel in self.factory.bot_config["channels"]:
            self.join("#" + channel)
    
    def privmsg(self, user, channel, msg):
        pm = self.msg_parser.parser(self.user_builder.get_user(user), channel, msg)

        print "user: %s channel: %s msg: %s is_private: %d is_cmd: %d" \
                % (pm.user.nick, pm.channel, pm.msg, pm.is_private, pm.is_cmd) 

        if pm.is_cmd:
            self.handle_command.handle(pm)

        try:
            self.xml_logger.log(self.user_builder.get_user(user), channel, msg)
        except IRCXMLLoggerException as e:
            self.msg(channel, e.value)


    def userRenamed(self, oldnick, newnick):
        self.user_builder.rename_user(oldnick, newnick)

    def userQuit(self, nick, reason):
        self.user_builder.invalidate_user(nick)

    def userLeft(self, nick, channel):
        self.user_builder.invalidate_user(nick)
        
        


class IRCBotFactory(protocol.ClientFactory):
    protocol = IRCBot

    def __init__(self, bot_config):
        self.bot_config = bot_config

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)


import sys
from twisted.internet import reactor

if __name__ == "__main__":
    yaml_config = file(sys.argv[1], "r")
    bot_config = yaml.load(yaml_config)

    reactor.connectTCP(bot_config["server"], bot_config["port"], IRCBotFactory(bot_config))
    reactor.run()

