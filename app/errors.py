#-*- coding:utf-8 -*-

class DBExitError(Exception):
    pass


class NoConnectExitError(Exception):
    pass


class ConnectExitError(Exception):
    pass


class EngineExitError(Exception):
    pass