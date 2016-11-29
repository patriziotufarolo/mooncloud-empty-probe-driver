from driver import Driver
import logging

class EmptyDriver(Driver):
    def action(self, inputs):
        logging.info(self.testinstances)
        logging.info("Information")
        logging.error("Error")
        return True
    def rollback(self, inputs):
        return True
    def appendAtomics(self):
        self.appendAtomic(self.action, self.rollback)

