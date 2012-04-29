class LocationNotFoundError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class AlreadyExistsError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class ForbiddenError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)
