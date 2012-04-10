def getDjangoTicketHeader():
  return "HTTP_X_UDJ_TICKET_HASH"

def getTicketHeader():
  return "X-Udj-Ticket-Hash"

def getUserIdHeader():
  return "X-Udj-User-Id"

def getGoneResourceHeader():
  return "X-Udj-Gone-Resource"

def getUUIDHeader():
  return "X-UDJ-Machine-UUID"

def getDjangoUUIDHeader():
  return "HTTP_X_UDJ_MACHINE_UUID"

def getEventPasswordHeader():
  return "X-Udj-Event-Password";

def getDjangoEventPasswordHeader():
  return "HTTP_X_UDJ_EVENT_PASSWORD";
