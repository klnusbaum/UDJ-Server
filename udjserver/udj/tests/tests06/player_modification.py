import udj


class OwnerModificationTests(udj.testhelpers.tests06.testclasses.BasicPlayerModificationTests):
  username = "kurtis"
  userpass = "testkurtis"

class AdminModificationTests(udj.testhelpers.tests06.testclasses.BasicPlayerModificationTests):
  username = "lucas"
  userpass = "testlucas"

class OwnerPasswordModificationTests(udj.testhelpers.tests06.testclasses.PasswordModificationTests):
  username = 'alejandro'
  userpass = 'testalejandro'

class AdminPasswordModificationTests(udj.testhelpers.tests06.testclasses.PasswordModificationTests):
  username = 'kurtis'
  userpass = 'testkurtis'
