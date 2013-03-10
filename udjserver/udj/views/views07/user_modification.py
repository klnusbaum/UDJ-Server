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
from django.db import transaction

@NeedsJSON
@AcceptsMethods(['PUT', 'POST'])
@HasNZJSONParams(['username', 'email', 'password'])
def userMod(request, json_params):

  #Validate inputs
  username = json_params['username']
  email = json_params['email']
  password = json_params['password']
  first_name = json_params.get('first_name', '')
  last_name = json_params.get('last_name', '')

  if User.objects.filter(email=email).exists():
    toReturn = HttpResponse(status=409)
    toReturn[CONFLICT_RESOURCE_HEADER] = 'email'
    return toReturn

  if len(password) < 8:
    return HttpResponse("Invalid password", status=406)

  try:
    validate_email(email)
  except ValidationError:
    return HttpResponse("Invalid email", status=406)

  #actuall do stuff
  if request.method == 'PUT':
    return createUser(request, username, email, password, first_name, last_name)
  else:
    return modifyUser(request, username, email, password, first_name, last_name)

@transaction.commit_on_success
def modifyUser(request, username, email, first_name, last_name):
  if username != request.user.username:
    return HttpResponse("Can't change username", status=406)

  request.user.email = json_param['email']
  request.user.first_name = json_param['first_name']
  request.user.last_name = json_param['last_name']
  request.user.set_password(password)
  return HttpResponse()

@transaction.commit_on_success
def createUser(request, username, email, password, first_name, last_name):

  if User.objects.filter(username=username).exists():
    toReturn = HttpResponse(status=409)
    toReturn[CONFLICT_RESOURCE_HEADER] = 'username'
    return toReturn

  if not re.compile(r'^[\w.@+-]+$').match(username):
    return HttpResponse("Invalid username", status=406)

  newUser = User.objects.create_user(
      username,
      email,
      password
  )

  newUser.first_name = first_name
  newUser.last_name = last_name
  newUser.save()

  return HttpResponse(status=201)
