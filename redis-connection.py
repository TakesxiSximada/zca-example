# -*- coding: utf-8 -*-
import sys
import argparse
import configparser
from zope.interface import (
    Interface,
    implementer,
    )
from zope.interface.registry import Components
from zope.component.interfaces import IFactory
from redis import StrictRedis


class IRedisConnection(Interface):
    pass


@implementer(IRedisConnection)
class RedisConnection(object):
    def __init__(self, conn):
        self._conn = conn

    def input_data(self):
        self._conn.setex('test', 10, 'aaa')


@implementer(IFactory)
class RedisConnectionFactory(object):
    def __init__(self, config):
        self._config = config
        self._conn = None

    def __call__(self, *args, **kwds):
        if self._conn is None:
            core = StrictRedis()
            self._conn = RedisConnection(core)
        return self._conn


def includeme(config):
    registry = config.registry
    registry.registerUtility(RedisConnectionFactory({}), IFactory, 'redis')


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)  # noqa
    from unittest import mock
    config = mock.Mock()
    config.registry = Components()
    includeme(config)
    factory = config.registry.queryUtility(IFactory, 'redis')
    conn = factory()  # noqa
    conn.input_data()

if __name__ == '__main__':
    sys.exit(main())
