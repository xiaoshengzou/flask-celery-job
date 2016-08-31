#-*- coding:utf-8 -*-


class DBPlugin(object):
    """
        数据库配置的基类
    """
    def __init__(self, dbconfig):
        self.dbconfig = dbconfig
        self.plugin = dbconfig.get('plugin', None)
        self.param = dbconfig.get('param', None)
        self.db = None
        self.init_db()

    def init_db(self):
        if self.plugin == 'msql':
            if self.db is None:
                kwargs = self.param
                print('init %s database') % self.plugin

