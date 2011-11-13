from myauth import hasValidTicket
from myauth import ticketMatchesUser
from myauth import getInvalidTicketResponse
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseBadRequest

def TicketUserMatch(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user_id = kwargs['user_id']
    
    if not hasValidTicket(request):
      return getInvalidTicketResponse(request)
    if not ticketMatchesUser(request.META["udj_ticket_hash"], user_id):
      toReturn = HttpResponseForbidden("ticket didn't match user")
      return toReturn
    else:
      return function(*args, **kwargs)
  return wrapper

def AcceptsMethods(acceptedMethods):
  def decorator(target):
    def wrapper(*args, **kwargs):
      request = args[0]
      if request.method in acceptedMethods:
        return target(*args, **kwargs)
      else:
        return HttpResponseNotAllowed()
    return wrapper
  return decorator
      
def NeedsJSON(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    try:
      if request.META['CONTENT_TYPE'] != 'text/json':
        return HttpResponseBadRequest("must send json")
      elif request.raw_post_data == '':
        return HttpResponseBadRequest("didn't send anything. empty payload")
      else:
        return function(*args, **kwargs)
    except KeyError:
      return HttpResponseBadRequest("Must speicfy a conent type of text/json")
  return wrapper
    
    
