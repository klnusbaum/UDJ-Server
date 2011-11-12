from myauth import hasValidTicket
from myauth import ticketMatchesUser
from myauth import getInvalidTicketResponse
from django.http import HttpResponseNotAllowed

def TicketUserMatch(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user_id = kwargs['user_id']
    
    if not hasValidTicket(request):
      return getInvalidTicketResponse(request)
    if not ticketMatchesUser(request.META["udj_ticket_hash"], user_id):
      toReturn = HttpResponseForbidden()
      toReturn['error'] = "ticket didn't match user"
      return toReturn
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
      
