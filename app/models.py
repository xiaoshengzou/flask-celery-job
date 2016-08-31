#-*- coding:utf-8 -*-

from . import db

class JobInfo(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))                    # 任务名称
    job_id = db.Column(db.String(128), unique=True)     # 关联celery的jobid
    job_type = db.Column(db.String(50))                 # 任务类型
    user_id = db.Column(db.Integer)                     # 操作用户
    export_file = db.Column(db.String(255))             # 导入的文件名称，或导出的文件名称
    result = db.Column(db.String(32))                   # 任务结果
    version = db.Column(db.String(16), default='1.0')   # 任务版本号
    plugin = db.Column(db.String(64))                   # 源数据类型
    plugin_name = db.Column(db.String(128))             # 源数据名称
    host = db.Column(db.String(32))                     # 数据库主机
    port = db.Column(db.Integer)                        # 数据库端口
    db_name = db.Column(db.String(128))                 # 数据库名称
    table_name = db.Column(db.String(128))              # 数据库表名
    rule = db.Column(db.Text)                           # 提取规则
    job_dones = db.Column(db.Integer, default=0)        # 任务运行次数
    is_run = db.Column(db.Boolean, default=False)       # 任务是否在运行

    def to_json(self):
        json_config = {
            "id":self.id,
            "type":self.job_type,
            "version":self.version,
            "job_celery_id":self.job_id,
            "job_name":self.name,
            "plugin":self.plugin,
            "plugin_name":self.plugin_name,
            "host":self.host,
            "port":self.port,
            "db":self.db_name,
            "table_name":self.table_name,
            "rule":self.rule,
            "job_dones":self.job_dones,
        }
        return json_config