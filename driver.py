import six
import traceback
import imp
import logging
import pkgutil

class AtomicOperation(object):
    action = None
    rollback = None
    def __init__(self, action, rollback):
        self.action = action
        self.rollback = rollback

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
                logging.warning("could not load the driver '%s':%s", pathname, e.message)
            if fid:
                fid.close()


    def __init__(self, testinstances):
        self.testinstances = testinstances
        self.atomic_operations = []

    def appendAtomic(self, action, rollback):
        self.atomic_operations.append(AtomicOperation(action, rollback))

    def appendAtomics(self):
        pass

    def run(self):
        prev_out = None
        ctr = 0
        try:
            total_operations = len(self.atomic_operations)
            for operation in self.atomic_operations:
                out = operation.action(prev_out)
                prev_out = out
                ctr += 1
            print("Test execution finished")
            final_result = prev_out
        except Exception as e:
            print("Phase {} returned an exception. Reverting operations. Stepping back to {}".format(str(ctr), str(ctr-1)))
            print("Exception:")
            print(traceback.format_exc())
            ctr -= 1
            try:
                rollback_prev_out = prev_out
                for rollback in six.range(ctr, -1, -1):
                    rollback_prev_out = self.atomic_operations(ctr).rollback()
                    ctr -= 1
            except Exception as e:
                print("Exception during rollback at phase {}").format(str(ctr))
                print(traceback.format_exc())
            final_result = 'error'
        return final_result

