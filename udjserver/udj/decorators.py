from udj.auth import hasValidTicket
from udj.auth import ticketMatchesUser
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden

def NeedsAuth(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    if not hasValidTicket(request):
      return HttpResponseForbidden()
    else:
      return function(*args, **kwargs)
  return wrapper
      

def TicketUserMatch(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    user_id = kwargs['user_id']
    
    if not hasValidTicket(request):
      return HttpResponseForbidden()
    if not ticketMatchesUser(request, user_id):
      return HttpResponseForbidden()
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
        return HttpResponseNotAllowed(acceptedMethods)
    return wrapper
  return decorator
      
def NeedsJSON(function):
  def wrapper(*args, **kwargs):
    request = args[0]
    if not request.META.has_key('CONTENT_TYPE'):
      return HttpResponseBadRequest("must specify content type")
    elif request.META['CONTENT_TYPE'] != 'text/json':
      return HttpResponseBadRequest("must send json")
    elif request.raw_post_data == '':
      return HttpResponseBadRequest("didn't send anything. empty payload")
    else:
      return function(*args, **kwargs)
  return wrapper
    
    
