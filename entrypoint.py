#!/usr/bin/env python
import sys
import six
import json
from EmptyDriver import EmptyDriver

try:
    testcase = json.load(sys.stdin)
except ValueError:
    print("Invalid JSON provided in STDIN")
    sys.exit(-1)

this_driver = EmptyDriver(testcase)
this_driver.appendAtomics()
print(this_driver.run())
