###
### This logtailer plugin for ganglia-logtailer parses logs from Unbound and
### produces the following metrics:
###   * queries per second
###   * recursion requests per second
###   * cache hits per second
###

import time
import threading

# local dependencies
from ganglia_logtailer_helper import GangliaMetricObject
from ganglia_logtailer_helper import LogtailerParsingException, LogtailerStateException

class PythonErrorLogtailer(PythonLogtailer):
    # period must be defined and indicates how often the gmetric thread should call get_state() (in seconds) (in daemon mode only)
    # note that if period is shorter than it takes to run get_state() (if there's lots of complex calculation), the calling thread will automatically double period.
    # period must be >15.  It should probably be >=60 (to avoid excessive load).  120 to 300 is a good range (2-5 minutes).  Take into account the need for time resolution, as well as the number of hosts reporting (6000 hosts * 15s == lots of data).
    def __init__(self):
        super(PythonErrorLogtailer, self).__init__("(?P<message>.*)")
        pass

    def parse_message(self, message_dict):
        """
        Parse the infomration from message. Return an state dict.
        """
        if message_dict['level'] == "ERROR":
            message_dict = regMatch.groupdict()
            tmpDict = {}
            tmpDict["message"] = self.message_dict["message"] + "%%" + message_dict['message']
            tmpDict["num_lines"] = self.message_dict["num_lines"] + 1
            return tmpDict

    def generate_state_func(self, message_dict, check_time):
        """ Return metrics according to message_dict and check_time
        """
        error_lines_per_second = message_dict["num_lines"] / check_time
        error_metric = GangliaMetricObject('error', error_lines_per_second, units='qps')
        return [error_metric]

    def message_reset(self):
        """ Reset parsed data.
        """
        self.message_dict = {}
        self.message_dict["message"] = ""
        self.message_dict["num_lines"] = 0
        pass
