from driver import Driver

class EmptyDriver(Driver):
    def action(self, inputs):
        print(self.testinstances)
        return True
    def rollback(self, inputs):
        return True
    def appendAtomics(self):
        self.appendAtomic(self.action, self.rollback)

