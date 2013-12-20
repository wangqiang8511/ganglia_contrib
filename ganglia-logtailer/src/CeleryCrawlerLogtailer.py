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
from PythonLogtailer import PythonLogtailer

class CeleryCrawlerLogtailer(PythonLogtailer):
    # period must be defined and indicates how often the gmetric thread should call get_state() (in seconds) (in daemon mode only)
    # note that if period is shorter than it takes to run get_state() (if there's lots of complex calculation), the calling thread will automatically double period.
    # period must be >15.  It should probably be >=60 (to avoid excessive load).  120 to 300 is a good range (2-5 minutes).  Take into account the need for time resolution, as well as the number of hosts reporting (6000 hosts * 15s == lots of data).
    def __init__(self):
        super(CeleryCrawlerLogtailer, self).__init__(".*finished: (?P<url>.*)")
        pass

    def message_init(self):
        self.message_dict = {}
        self.message_dict["url"] = ""
        self.message_dict["num_lines"] = 0
        pass

    def parse_message(self, parsed_dict):
        """
        Parse the infomration from message. Return an state dict.
        """
        if parsed_dict['level'] == "INFO":
            self.message_dict["url"] += "%%" + parsed_dict['url']
            self.message_dict["num_lines"] += 1

    def generate_state_func(self, message_dict, check_time):
        """ Return metrics according to message_dict and check_time.
        """
        url_per_second = message_dict["num_lines"] / check_time
        url_metric = GangliaMetricObject('crawl_url', url_per_second,
                                         units='urlps')
        return [url_metric]

    def message_reset(self):
        """ Reset parsed data.
        """
        self.message_dict = {}
        self.message_dict["url"] = ""
        self.message_dict["num_lines"] = 0
