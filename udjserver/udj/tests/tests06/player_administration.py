import udj


class OwnerAdministrationTests(udj.testhelpers.tests06.testclasses.BasicPlayerAdministrationTests):
  username = "kurtis"
  userpass = "testkurtis"

class AdminAdministrationTests(udj.testhelpers.tests06.testclasses.BasicPlayerAdministrationTests):
  username = "lucas"
  userpass = "testlucas"

class OwnerPasswordAdministrationTests(udj.testhelpers.tests06.testclasses.PasswordAdministrationTests):
  username = 'alejandro'
  userpass = 'testalejandro'

class AdminPasswordAdministrationTests(udj.testhelpers.tests06.testclasses.PasswordAdministrationTests):
  username = 'kurtis'
  userpass = 'testkurtis'
