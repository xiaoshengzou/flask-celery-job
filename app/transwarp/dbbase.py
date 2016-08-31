# # -*- coding: utf-8 -*-

# import mysql.connector
# import logging
# import time
# import functools
# import threading
# #from ..errors import NoConnectExitError, ConnectExitError, EngineExitError

# class DBExitError(Exception):
#     pass

# class NoConnectExitError(Exception):
#     pass

# class ConnectExitError(Exception):
#     pass

# class EngineExitError(Exception):
#     pass

# class _Engine(object):
#     """
#     数据库引擎对象
#     用于保存 db模块的核心函数：create_engine 创建出来的数据库连接
#     """
#     def __init__(self, connect):
#         self._connect = connect

#     def connect(self):
#         return self._connect()

# class _LasyConnection(object):
#     """
#     惰性连接对象
#     仅当需要cursor对象时，才连接数据库，获取连接
#     """
#     def __init__(self, engine):
#         self.connection = None
#         self._engine = engine

#     def cursor(self, engine):
#         if self.connection is None:
#             _connection = self._engine.connect()
#             logging.info('[CONNECTION] [OPEN] connection <%s>...' % hex(id(_connection)))
#             self.connection = _connection
#         return self.connection.cursor()

#     def commit(self):
#         self.connection.commit()

#     def rollback(self):
#         self.connection.rollback()

#     def cleanup(self):
#         if self.connection:
#             _connection = self.connection
#             self.connection = None
#             logging.info('[CONNECTION] [CLOSE] connection <%s>...' % hex(id(connection)))
#             _connection.close()

# class _DbCtx(threading.local):
#     """
#     db模块的核心对象, 数据库连接的上下文对象，负责从数据库获取和释放连接
#     取得的连接是惰性连接对象，因此只有调用cursor对象时，才会真正获取数据库连接
#     该对象是一个 Thread local对象，因此绑定在此对象上的数据 仅对本线程可见
#     """
#     def __init__(self, engine):
#         self._engine = engine
#         self.connection = None
#         self.transactions = 0

#     def is_init(self):
#         """
#         返回一个布尔值，用于判断 此对象的初始化状态
#         """
#         return self.connection is not None

#     def init(self):
#         """
#         初始化连接的上下文对象，获得一个惰性连接对象
#         """
#         logging.info('open lazy connection...')
#         self.connection = _LasyConnection(self._engine)
#         self.transactions = 0

#     def cleanup(self):
#         """
#         清理连接对象，关闭连接
#         """
#         self.connection.cleanup()
#         self.connection = None

#     def cursor(self):
#         """
#         获取cursor对象， 真正取得数据库连接
#         """
#         return self.connection.cursor()

# class _ConnectionCtx(object):
#     """
#     因为_DbCtx实现了连接的 获取和释放，但是并没有实现连接
#     的自动获取和释放，_ConnectCtx在 _DbCtx基础上实现了该功能，
#     因此可以对 _ConnectCtx 使用with 语法，比如：
#     with connection():
#         pass
#         with connection():
#             pass
#     """
#     def __init__(self, db_ctx):
#         self._db_ctx = db_ctx

#     def __enter__(self):
#         """
#         获取一个惰性连接对象
#         """
#         self.should_cleanup = False
#         if not self._db_ctx.is_init():
#             self._db_ctx.init()
#             self.should_cleanup = True
#         return self

#     def __exit__(self, exctype, excvalue, traceback):
#         """
#         释放连接
#         """
#         if self.should_cleanup:
#             self._db_ctx.cleanup()

# class _TransactionCtx(object):
#     """
#     事务嵌套比Connection嵌套复杂一点，因为事务嵌套需要计数，
#     每遇到一层嵌套就+1，离开一层嵌套就-1，最后到0时提交事务
#     """
#     def __init__(self, db_ctx):
#         self._db_ctx = db_ctx

#     def __enter__(self):
#         self.should_close_conn = False
#         if not self._db_ctx.is_init():
#             # needs open a connection first:
#             self._db_ctx.init()
#             self.should_close_conn = True
#         self._db_ctx.transactions += 1
#         logging.info('begin transaction...' if self._db_ctx.transactions == 1 else 'join current transaction...')
#         return self

#     def __exit__(self, exctype, excvalue, traceback):
#         self._db_ctx.transactions -= 1
#         try:
#             if self._db_ctx.transactions == 0:
#                 if exctype is None:
#                     self.commit()
#                 else:
#                     self.rollback()
#         finally:
#             if self.should_close_conn:
#                 self._db_ctx.cleanup()

#     def commit(self):
#         logging.info('commit transaction...')
#         try:
#             self._db_ctx.connection.commit()
#             logging.info('commit ok.')
#         except:
#             logging.warning('commit failed. try rollback...')
#             self._db_ctx.connection.rollback()
#             logging.warning('rollback ok.')
#             raise

#     def rollback(self):
#         logging.warning('rollback transaction...')
#         self._db_ctx.connection.rollback()
#         logging.info('rollback ok.')

# class DBBase(object):
#     '''
#         封装数据的连接和操作
#         1. 更简单的操作数据库
#              一次数据访问：   数据库连接 => 游标对象 => 执行SQL => 处理异常 => 清理资源。
#              db模块对这些过程进行封装，使得用户仅需关注SQL执行。
#          2. 数据安全
#              用户请求以多线程处理时，为了避免多线程下的数据共享引起的数据混乱，
#              需要将数据连接以ThreadLocal对象传入。
#     '''
#     def __init__(self, user, password, database, host, port, **kw):
#         self._engine = None
#         self._db_ctx = None
#         self._params = dict(user=user, password=password, database=database, host=host, port=port)
#         self.init(**kw)


#     def init(self, **kw):
#         self.load_default_config(**kw)
#         self.create_engine()
#         self.create_db_ctx()

#     def load_default_config(self, **kw):
#         ''' 加载数据库初始化配置
#             并根据用户设置更新系统默认配置
#         '''
#         defaults = dict(use_unicode=True, charset='utf8', collation='utf8_general_ci', autocommit=False)
#         for k, v in defaults.iteritems():
#             self._params[k] = kw.pop(k, v)
#         self._params.update(kw)
#         self._params['buffered'] = True

#     def create_engine(self):
#         '''
#             用于连接数据库, 生成对象engine，
#             engine对象持有数据库连接
#         '''
#         if self._engine is not None:
#             raise EngineExitError('Engine is exited!')
#         params = self._params
#         self._engine = _Engine(lambda: mysql.connector.connect(**params))
#         logging.info('Init mysql engine ok.')

#     def create_db_ctx(self):
#         '''
#         创建数据库连接的上下文对象
#         '''
#         if self._db_ctx is not None:
#             raise DBCtxExitError('db contentx is exited!')
#         self._db_ctx = _DbCtx(self._engine)

#     def connection(self):
#         return _ConnectionCtx(self._db_ctx)

#     def transaction(self):
#         return _TransactionCtx(self._db_ctx)

#     def with_connection(self, func):
#         @functools.wraps(func)
#         def _wrapper(*args, **kw):
#             with _ConnectionCtx():
#                 return func(*args, **kw)
#         return _wrapper

#     @with_connection
#     def _select(self, sql, first, *args):
#         """
#         执行SQL，返回一个结果 或者多个结果组成的列表
#         """
#         global _db_ctx
#         cursor = None
#         sql = sql.replace('?', '%s')
#         logging.info('SQL: %s, ARGS: %s' % (sql, args))
#         try:
#             cursor = _db_ctx.connection.cursor()
#             cursor.execute(sql, args)
#             if cursor.description:
#                 names = [x[0] for x in cursor.description]
#             if first:
#                 values = cursor.fetchone()
#                 if not values:
#                     return None
#                 return Dict(names, values)
#             return [Dict(names, x) for x in cursor.fetchall()]
#         finally:
#             if cursor:
#                 cursor.close()


