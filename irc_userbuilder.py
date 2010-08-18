from irc_constants import IRCConstants

class IRCUserType(object):
    regular = 0x0
    admin   = 0x1
    oper    = 0x2
    owner   = 0x4


class IRCUser(object):
    def __init__(self, user_builder, nick, hostname):
        self.user_builder   = user_builder
        self.nick           = nick
        self.hostname       = hostname
        self.user_type      = IRCUserType.regular

    def validate_password(self, password):
        return self.user_builder.validate_password(self, password)


class IRCUserBuilder(object):
    def __init__(self, irc):
        self.irc    = irc
        self.users  = {}

    def get_user(self, user):
        nick        = self.short_username(user)
        hostname    = self.hostname(user)

        if nick in self.users:
            if self.users[nick].hostname == hostname:
                return self.users[nick]

        self.users[nick] = IRCUser(self, nick, hostname)
        return self.users[nick]


    def short_username(self, user):
        return user.split(IRCConstants.username_delimiter)[0]

    def hostname(self, user):
        return user.split(IRCConstants.username_delimiter)[1:]

    def validate_password(self, irc_user, password):
        print "%s %s" % (irc_user.nick, password)
        try:
            user_auth = self.irc.factory.bot_config["auth"][irc_user.nick]

            if user_auth["password"] == password:
                irc_user.user_type = user_auth["type"]
                return irc_user.user_type

        except KeyError:
            pass

        return 0

    def invalidate_user(self, user):
        try:
            del self.users[user]
        except KeyError:
            pass

    def rename_user(self, oldnick, newnick):
        try:
            self.users[newnick] = self.users[oldnick]
            self.users[newnick].nick = newnick
            del self.users[oldnick]
        except KeyError:
            pass
