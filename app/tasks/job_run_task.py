# from .. import celery
import time
import logging
from ..models import JobInfo
from .. import db
from .. import celery

LOGGER = logging.getLogger(__name__)

@celery.task(bind=True)
def mysqlTomongoDB(self, id):
    # job = JobInfo.query.filter_by(id=id).first()
    # config = job.to_josn()
    # LOGGER.info("%s task start run" % config.get('job_name',"None"))
    # LOGGER.info("task version %s ......" % config.get('version',"1.0"))
    # LOGGER.info("task type %s .........." % config.get('type',"NoneType"))
    # LOGGER.info("task jobid %s ............" % config.get('job_celery_id',"NoneId"))
    self.update_state(state='PROGRESS', meta={'current':10, 'total':100, 'status':'load config successful!'})
    time.sleep(1)
    self.update_state(state='PROGRESS',  meta={'current':20, 'total':100, 'status':'open read database successful!'})
    time.sleep(1)
    self.update_state(state='PROGRESS',  meta={'current':30, 'total':100, 'status':'open write database successful!'})
    for i in range(30,100):
        self.update_state(state='PROGRESS', meta={'current':i, 'total':100, 'status':'reade data.....'})
        time.sleep(1)
    print("task over")
    time.sleep(1)
    # job.is_run = False
    # db.session.add(job)
    # db.session.commit()
    return {'current':100, 'total':100, 'status':'task compleated!', 'result':'over'}
