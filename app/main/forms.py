#-*- coding:utf-8 -*-

from flask_wtf import Form
from wtforms import (IntegerField, StringField, TextAreaField, BooleanField, SelectField,
    SubmitField)
from wtforms.validators import Required


class ConfigForm(Form):
    job_name = StringField(u'任务名称', validators=[Required()])
    job_type = SelectField(u'任务类型', coerce=int)
    db_source_type = SelectField(u'源数据类型', coerce=int)
    db_source_name = StringField(u'源数据名称', validators=[Required()])
    db_host = StringField(u'主机地址', validators=[Required()])
    db_port = IntegerField(u'端口', validators=[Required()])
    db_name = StringField(u'数据库名称', validators=[Required()])
    #user_name = StringField(u'用户名', validators=[Required()])
    #user_pwd = StringField(u'密码', validators=[Required()])
    table_name = StringField(u'表名', validators=[Required()])
    rule = TextAreaField(u'提取规则')
    export_filename = StringField(u'导出文件名', validators=[Required()])
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)
        self.job_dict = {'1':u'即时输出日志任务',
                        '10':'MongoDB',
                        '20':'MySql',
                        '30':'SQLServer'}
        self.job_type.choices = [(1,u'即时输出日志任务')]
        self.db_source_type.choices = [(10,'MongoDB'),(20,'MySql'),(30,'SQLServer')]

    def get_name(self, value):
        return self.job_dict[str(value)]

