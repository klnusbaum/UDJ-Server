import json

from udj.views.views06.decorators import NeedsJSON
from udj.views.views06.decorators import AcceptsMethods
from udj.headers import CONFLICT_RESOURCE_HEADER

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User

@NeedsJSON
@AcceptsMethods(['PUT'])
def createUser(request):
  try:
    desiredUser = json.loads(request.content)
    username = desiredUser['username']
    email = desiredUser['email']
    password = desiredUser['password']
  except ValueError, KeyError:
    return HttpResponseBadRequest("Malformed JSON")

  if User.objects.filter(email=email).exists():
    toReturn = HttpResponse(status=409)
    toReturn[CONFLICT_RESOURCE_HEADER] = 'email'
    return toReturn

  if User.objects.filter(username=username).exists()
    toReturn = HttpResponse(status=409)
    toReturn[CONFLICT_RESOURCE_HEADER] = 'username'
    return toReturn

  if len(password) < 8:
    return HttpResponse(status=406)

  try:
    validate_email(email)
  except ValidationError:
    return HttpResponse(status=406)

  newUser = User.objects.create_user(
      username,
      email,
      password
  )

  newUser.save()
  return HttpResponse(status=201)
