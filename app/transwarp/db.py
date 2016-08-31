# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

# import time
# import functools
# import threading
# import logging


# """
# 设计db模块的原因：
#   1. 更简单的操作数据库
#       一次数据访问：   数据库连接 => 游标对象 => 执行SQL => 处理异常 => 清理资源。
#       db模块对这些过程进行封装，使得用户仅需关注SQL执行。
#   2. 数据安全
#       用户请求以多线程处理时，为了避免多线程下的数据共享引起的数据混乱，
#       需要将数据连接以ThreadLocal对象传入。
# 设计db接口：
#   1.设计原则：
#       根据上层调用者设计简单易用的API接口
#   2. 调用接口
#       1. 初始化数据库连接信息
#           create_engine封装了如下功能:
#               1. 为数据库连接 准备需要的配置信息
#               2. 创建数据库连接(由生成的全局对象engine的 connect方法提供)
#           from transwarp import db
#           db.create_engine(user='root',
#                            password='password',
#                            database='test',
#                            host='127.0.0.1',
#                            port=3306)
#       2. 执行SQL DML
#           select 函数封装了如下功能:
#               1.支持一个数据库连接里执行多个SQL语句
#               2.支持链接的自动获取和释放
#           使用样例:
#               users = db.select('select * from user')
#               # users =>
#               # [
#               #     { "id": 1, "name": "Michael"},
#               #     { "id": 2, "name": "Bob"},
#               #     { "id": 3, "name": "Adam"}
#               # ]
#       3. 支持事物
#          transaction 函数封装了如下功能:
#              1. 事务也可以嵌套，内层事务会自动合并到外层事务中，这种事务模型足够满足99%的需求
# """
# # global engine object:
# engine = None

# def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
#     """
#     db模型的核心函数，用于连接数据库, 生成全局对象engine，
#     engine对象持有数据库连接
#     """
#     import mysql.connector
#     global engine
#     if engine is not None:
#         raise DBExitError('Engine is already initialized.')
#     params = dict(user=user, password=password, database=database, host=host, port=port)
#     defaults = dict(use_unicode=True, charset='utf8', collation='utf8_general_ci', autocommit=False)
#     for k, v in defaults.iteritems():
#         params[k] = kw.pop(k, v)
#     params.update(kw)
#     params['buffered'] = True
#     engine = _Engine(lambda: mysql.connector.connect(**params))
#     # test connection...
#     logging.info('Init mysql engine <%s> ok.' % hex(id(engine)))

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
#     def __init__(self):
#         self.connection = None

#     def cursor(self):
#         if self.connection is None:
#             _connection = engine.connect()
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
#     def __init__(self):
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
#         self.connection = _LasyConnection()
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


# # thread-local db context:
# _db_ctx = _DbCtx()

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
#     def __enter__(self):
#         """
#         获取一个惰性连接对象
#         """
#         global _db_ctx
#         self.should_cleanup = False
#         if not _db_ctx.is_init():
#             _db_ctx.init()
#             self.should_cleanup = True
#         return self

#     def __exit__(self, exctype, excvalue, traceback):
#         """
#         释放连接
#         """
#         global _db_ctx
#         if self.should_cleanup:
#             _db_ctx.cleanup()

# class _TransactionCtx(object):
#     """
#     事务嵌套比Connection嵌套复杂一点，因为事务嵌套需要计数，
#     每遇到一层嵌套就+1，离开一层嵌套就-1，最后到0时提交事务
#     """

#     def __enter__(self):
#         global _db_ctx
#         self.should_close_conn = False
#         if not _db_ctx.is_init():
#             # needs open a connection first:
#             _db_ctx.init()
#             self.should_close_conn = True
#         _db_ctx.transactions += 1
#         logging.info('begin transaction...' if _db_ctx.transactions == 1 else 'join current transaction...')
#         return self

#     def __exit__(self, exctype, excvalue, traceback):
#         global _db_ctx
#         _db_ctx.transactions -= 1
#         try:
#             if _db_ctx.transactions == 0:
#                 if exctype is None:
#                     self.commit()
#                 else:
#                     self.rollback()
#         finally:
#             if self.should_close_conn:
#                 _db_ctx.cleanup()

#     def commit(self):
#         global _db_ctx
#         logging.info('commit transaction...')
#         try:
#             _db_ctx.connection.commit()
#             logging.info('commit ok.')
#         except:
#             logging.warning('commit failed. try rollback...')
#             _db_ctx.connection.rollback()
#             logging.warning('rollback ok.')
#             raise

#     def rollback(self):
#         global _db_ctx
#         logging.warning('rollback transaction...')
#         _db_ctx.connection.rollback()
#         logging.info('rollback ok.')



# def connection():
#     """
#     db模块核心函数，用于获取一个数据库连接
#     通过_ConnectionCtx对 _db_ctx封装，使得惰性连接可以自动获取和释放，
#     也就是可以使用 with语法来处理数据库连接
#     _ConnectionCtx    实现with语法
#     ^
#     |
#     _db_ctx           _DbCtx实例
#     ^
#     |
#     _DbCtx            获取和释放惰性连接
#     ^
#     |
#     _LasyConnection   实现惰性连接
#     """
#     return _ConnectionCtx()