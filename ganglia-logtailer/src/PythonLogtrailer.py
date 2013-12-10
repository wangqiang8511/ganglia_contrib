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

class PythonLogtailer(object):
    # period must be defined and indicates how often the gmetric thread should call get_state() (in seconds) (in daemon mode only)
    # note that if period is shorter than it takes to run get_state() (if there's lots of complex calculation), the calling thread will automatically double period.
    # period must be >15.  It should probably be >=60 (to avoid excessive load).  120 to 300 is a good range (2-5 minutes).  Take into account the need for time resolution, as well as the number of hosts reporting (6000 hosts * 15s == lots of data).
    period = 5
    def __init__(self, message_reg):
        '''This function should initialize any data structures or variables
        needed for the internal state of the line parser.'''
        self.dur_override = False
        self.reset_state()
        self.reg = re.compile('^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) (?P<time>[^ ]*) - (?P<module>[^ ]*) - (?P<level>[^ ]*) - %s' % message_reg)
        self.lock = threading.RLock()
        self.message = ""

    # example function for parse line
    # takes one argument (text) line to be parsed
    # returns nothing
    def parse_line(self, line):
        '''This function should digest the contents of one line at a time,
        updating the internal state variables.'''
        self.lock.acquire()
        regMatch = self.reg.match(line)
        if regMatch:
            self.message_dict = self.parse_message(regMatch.groupdict())
        self.lock.release()
    # example function for deep copy
    # takes no arguments
    # returns one object
    def deep_copy(self):
        '''This function should return a copy of the data structure used to
        maintain state.  This copy should different from the object that is
        currently being modified so that the other thread can deal with it
        without fear of it changing out from under it.  The format of this
        object is internal to the plugin.'''
        return [ self.message_dict ]
    # example function for reset_state
    # takes no arguments
    # returns nothing
    def reset_state(self):
        '''This function resets the internal data structure to 0 (saving
        whatever state it needs).  This function should be called
        immediately after deep copy with a lock in place so the internal
        data structures can't be modified in between the two calls.  If the
        time between calls to get_state is necessary to calculate metrics,
        reset_state should store now() each time it's called, and get_state
        will use the time since that now() to do its calculations'''
        self.message_reset()
        self.last_reset_time = time.time()
    # example for keeping track of runtimes
    # takes no arguments
    # returns float number of seconds for this run
    def set_check_duration(self, dur):
        '''This function only used if logtailer is in cron mode.  If it is
        invoked, get_check_duration should use this value instead of calculating
        it.'''
        self.duration = dur
        self.dur_override = True
    def get_check_duration(self):
        '''This function should return the time since the last check.  If called
        from cron mode, this must be set using set_check_duration().  If in
        daemon mode, it should be calculated internally.'''
        if( self.dur_override ):
            duration = self.duration
        else:
            cur_time = time.time()
            duration = cur_time - self.last_reset_time
            # the duration should be within 10% of period
            acceptable_duration_min = self.period - (self.period / 10.0)
            acceptable_duration_max = self.period + (self.period / 10.0)
            if (duration < acceptable_duration_min or duration > acceptable_duration_max):
                raise LogtailerStateException, "time calculation problem - duration (%s) > 10%% away from period (%s)" % (duration, self.period)
        return duration
    # example function for get_state
    # takes no arguments
    # returns a dictionary of (metric => metric_object) pairs
    def get_state(self):
        '''This function should acquire a lock, call deep copy, get the
        current time if necessary, call reset_state, then do its
        calculations.  It should return a list of metric objects.'''
        # get the data to work with
        self.lock.acquire()
        try:
            messages_dict = self.deep_copy()
            check_time = self.get_check_duration()
            self.reset_state()
            self.lock.release()
        except LogtailerStateException, e:
            # if something went wrong with deep_copy or the duration, reset and continue
            self.reset_state()
            self.lock.release()
            raise e

        # crunch data to how you want to report it

        # package up the data you want to submit
        metrics = self.generate_state_func(message_dict, check_time)
        # return a list of metric objects
        return metrics

    def parse_message(self, message_dict):
        """
        Parse the infomration from message. Return an state dict.
        """
        pass

    def generate_state_func(self, message_dict, check_time):
        """ Return metrics according to message_dict and check_time
        """
        pass

    def message_reset(self):
        """ Reset parsed data.
        """
        pass
