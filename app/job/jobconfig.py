
# from .config import Config
from dbplugin import DBPlugin

class JobConfig(object):
    """ Load user configuration of the operation """

    def __init__(self, jobconfig=None):
        self.jobconfig = jobconfig.get('config')
        self._version = jobconfig.get('version')
        self._type = jobconfig.get('type')
        self._jobid = jobconfig.get('jobid')

    @property
    def version(self):
        """Get the job version """
        return self._version

    @property
    def type(self):
        """ Get the job type """
        return self._type

    @property
    def job_id(self):
        """ Get the job Id """
        return self._jobid


    def getReader(self):
        """ return Reader object """
        reader = self.jobconfig.get('reader')
        return DBPlugin(reader)

    def getWriter(self):
        """ return Writer object """
        writer = self.jobconfig.get('writer')
        return DBPlugin(writer)
