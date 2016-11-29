import six
import traceback
import imp
import logging
import pkgutil
import json


class AtomicOperation(object):
    action = None
    rollback = None

    def __init__(self, action, rollback):
        self.action = action
        self.rollback = rollback


class DriverResult(object):
    result = None
    data = {}

    def __repr__(self):
        return json.dumps(self.__dict__)


class Driver(object):
    class __metaclass__(type):
        def __init__(cls, name, base, attrs):
            if not hasattr(cls, 'registered'):
                cls.registered = []
            else:
                cls.registered.append(cls)

    @classmethod
    def load(cls, *paths):
        paths = list(paths)
        cls.registered = []
        for _, name, _ in pkgutil.iter_modules(paths):
            fid, pathname, desc = imp.find_module(name, paths)
            try:
                imp.load_module(name, fid, pathname, desc)
            except Exception as e:
                logging.warning("could not load \
                                the driver '%s':%s", pathname, e.message)
            if fid:
                fid.close()

    def __init__(self, testinstances):
        self.testinstances = testinstances
        self.atomic_operations = []
        self.result = DriverResult()

    def appendAtomic(self, action, rollback):
        self.atomic_operations.append(AtomicOperation(action, rollback))

    def appendAtomics(self):
        pass

    def run(self):
        prev_out = None
        ctr = 0
        try:
            for operation in self.atomic_operations:
                out = operation.action(prev_out)
                prev_out = out
                ctr += 1
            logging.info("Test execution finished")
            self.result.result = prev_out
        except Exception:
            logging.error("Phase {} returned an exception.\
                          Reverting operations. Stepping back to {}"
                          .format(str(ctr), str(ctr-1)))
            logging.error("Exception:")
            logging.error(traceback.format_exc())
            ctr -= 1
            try:
                rollback_prev_out = prev_out
                for rollback in six.range(ctr, -1, -1):
                    rollback_prev_out = self.atomic_operations(ctr).\
                        rollback(rollback_prev_out)
                    ctr -= 1
            except Exception:
                logging.critical("Exception during rollback \
                                 at phase {}").format(str(ctr))
                logging.critical(traceback.format_exc())
            self.result.result = "ERROR"
        return self.result
