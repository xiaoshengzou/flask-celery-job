from . import main
from flask import render_template, request, url_for, redirect, flash
from flask import jsonify
from ..tasks.job import mysqlTomongoDB
from .forms import ConfigForm
from ..job.jobconfig import JobConfig
from ..models import JobInfo
from .. import db
import json

@main.route('/', methods=['GET', 'POST'])
def index():
    form = ConfigForm()
    if form.validate_on_submit():
        job = JobInfo(name=form.job_name.data,
                    job_type=form.get_name(form.job_type.data),
                    plugin=form.get_name(form.db_source_type.data),
                    plugin_name=form.db_source_name.data,
                    host=form.db_host.data,
                    port=form.db_port.data,
                    db_name=form.db_name.data,
                    table_name=form.table_name.data,
                    rule=form.rule.data,
                    export_file=form.export_filename.data
                    )
        db.session.add(job)
        db.session.commit()
        flash('You have successfully created a task')
        return redirect(url_for('.jobs'))
    return render_template('index.html', form=form)

@main.route('/jobs')
def jobs():
    jobs = JobInfo.query.all()
    return render_template('jobs.html', jobs=jobs)


@main.route('/job/<int:id>')
def job(id):
    job = JobInfo.query.get_or_404(id)
    return render_template('job_detail.html', job=job)

@main.route('/run', methods=['POST'])
def run():
    data = json.loads(request.form.get('data'))
    id = data.get('id', 0)
    job = JobInfo.query.get_or_404(id)
    if job is not None:
        job.job_dones += 1
        db.session.add(job)
        db.session.commit()
    try:
        task = mysqlTomongoDB.delay(id)
        job.job_id = task.id
        job.is_run = True
        db.session.add(job)
        db.session.commit()
    except Exception, e:
        print '%s'  % e
        raise e

    return jsonify({}), 202, {'Location': url_for('main.taskstatus',task_id=task.id)}


@main.route('/job/status/<task_id>')
def taskstatus(task_id):
    task = mysqlTomongoDB.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state':task.state,
            'current':0,
            'total':1,
            'status':'pending.....',
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': task.info,  # this is the exception raised
        }
    return jsonify(response)

@main.route('/delete', methods=['POST'])
def del_job():
    id = request.values.get('id', 0)
    job = JobInfo.query.get_or_404(id)
    try:
        db.session.delete(job)
        db.session.commit()
        return 'ok'
    except Exception, e:
        return 'fail'
