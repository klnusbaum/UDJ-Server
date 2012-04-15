from udj.auth import isValidTicket
from udj.headers import DJANGO_TICKET_HEADER

def NeedsAuth(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    if DJANGO_TICKET_HEADER not in request.META:
      responseString = "Must provide the " + getTicketHeader() + " header. "
      return HttpResponseBadRequest(responseString)
    elif not isValidTicket(
      request.META[DJANGO_TICKET_HEADER],
      request.META['REMOTE_ADDR'],
      request.META['REMOTE_PORT']):
      return HttpResponseForbidden("Invalid ticket: \"" + 
        request.META[getDjangoTicketHeader()] + "\"")
    else:
      return function(*args, **kwargs)
  return wrapper

