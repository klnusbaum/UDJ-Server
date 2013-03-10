import json
import re

from udj.views.views07.decorators import NeedsJSON
from udj.views.views07.decorators import AcceptsMethods
from udj.views.views07.decorators import HasNZJSONParams
from udj.headers import CONFLICT_RESOURCE_HEADER

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User

@NeedsJSON
@AcceptsMethods(['PUT'])
@HasNZJSONParams(['username', 'email', 'password'])
def createUser(request, json_params):
  username = json_params['username']
  email = json_params['email']
  password = json_params['password']

  if User.objects.filter(email=email).exists():
    toReturn = HttpResponse(status=409)
    toReturn[CONFLICT_RESOURCE_HEADER] = 'email'
    return toReturn

  if User.objects.filter(username=username).exists():
    toReturn = HttpResponse(status=409)
    toReturn[CONFLICT_RESOURCE_HEADER] = 'username'
    return toReturn

  if len(password) < 8:
    return HttpResponse("Invalid password", status=406)

  try:
    validate_email(email)
  except ValidationError:
    return HttpResponse("Invalid email", status=406)


  if not re.compile(r'^[\w.@+-]+$').match(username):
    return HttpResponse("Invalid username", status=406)

  newUser = User.objects.create_user(
      username,
      email,
      password
  )

  newUser.save()
  return HttpResponse(status=201)
