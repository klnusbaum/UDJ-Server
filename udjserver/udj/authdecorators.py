from udj.auth import isValidTicket
from udj.auth import ticketMatchesUser
from udj.headers import DJANGO_TICKET_HEADER
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden


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

def TicketUserMatch(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user_id = kwargs['user_id']
    if not ticketMatchesUser(request, user_id):
      return HttpResponseForbidden("The ticket doesn't match the given user\n" +
        "Give Ticket: \"" + request.META[getDjangoTicketHeader()] + "\"\n" +
        "Given User id: \"" + user_id + "\"")
    else:
      return function(*args, **kwargs)
  return wrapper
