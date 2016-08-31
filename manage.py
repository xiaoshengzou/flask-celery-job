#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
from app import create_app
from flask_script import Manager, Shell
from app import db
from app.models import JobInfo


# app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app = create_app('default')
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, JobInfo=JobInfo)

manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def deploy():
    """Run deployment tasks."""
    from app import db

    db.drop_all()
    db.create_all()




if __name__ == '__main__':
    manager.run()
    #app.run(debug=False)
