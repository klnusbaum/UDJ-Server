import json
import udj
from udj.headers import MISSING_RESOURCE_HEADER

class OwnerLibTestCases(udj.testhelpers.tests06.testclasses.LibTestCases):
  username='kurtis'
  userpass='testkurtis'

class AdminLibTestCases(udj.testhelpers.tests06.testclasses.LibTestCases):
  username='lucas'
  userpass='testlucas'
