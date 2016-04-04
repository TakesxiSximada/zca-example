#! /usr/bin/env python
import sys
import enum
import datetime
from zope.interface import (
    Interface,
    Attribute,
    implementer,
    )
from zope.interface.verify import verifyObject
from zope.component import (
    IFactory,
    getMultiAdapter,
    createObject,
    getGlobalSiteManager,
    )


class IPerson(Interface):
    name = Attribute(u'')
    born_at = Attribute(u'')
    dead_at = Attribute(u'')


class IPersonContext(Interface):
    pass


@implementer(IPersonContext)
class UserContext(object):
    pass


@implementer(IPerson)
class User(object):
    def __init__(self, name):
        self.name = name
        self.born_at = None
        self.dead_at = None


@implementer(IFactory)
class UserFactory(object):
    def __init__(self, get_birth_day=None):
        self._get_birth_day = get_birth_day or datetime.datetime.now

    def __call__(self, name):
        user = User(name)
        user.born_at = self._get_birth_day()
        return user


class IPersonContextFactory(IFactory):
    pass


@implementer(IPersonContextFactory)
class UserContextFactory(object):
    def __init__(self):
        pass

    def __call__(self):
        return UserContext()


class IKiller(Interface):
    get_anniversary = Attribute(u'')

    def kill():
        return bool()


@implementer(IKiller)
class Daemon(object):
    def __init__(self, user, context):
        self._user = user
        self.get_anniversary = datetime.datetime.now

    def kill(self):
        self._user.dead_at = self.get_anniversary()
        return True


class PersonType(enum.Enum):
    user = 'user'


def main():
    registry = getGlobalSiteManager()
    person_type = PersonType.user.value
    registry.registerUtility(
        UserFactory(), IFactory, person_type)  # factory settings
    registry.registerUtility(
        UserContextFactory(), IPersonContextFactory, person_type)  # factory settings
    registry.registerAdapter(
        Daemon, [IPerson, IPersonContext], IKiller, person_type)  # adapter settings
    user = createObject(person_type, 'test')
    user_context = registry.queryUtility(IPersonContextFactory, person_type)()
    killer = getMultiAdapter([user, user_context], IKiller, person_type)
    assert registry.adapters.lookup([IPerson, IPersonContext], IKiller, person_type) is Daemon
    assert verifyObject(IKiller, killer)
    assert IKiller.providedBy(killer)
    assert verifyObject(IPerson, user)
    assert IPerson.providedBy(user)
    assert verifyObject(IPersonContext, user_context)
    assert IPersonContext.providedBy(user_context)
    killer.kill()
    print(user.dead_at)

if __name__ == '__main__':
    sys.exit(main())
