import json
import re

from udj.views.views07.decorators import NeedsJSON
from udj.views.views07.decorators import AcceptsMethods
from udj.views.views07.decorators import HasNZJSONParams
from udj.views.views07.authdecorators import NeedsAuth
from udj.views.views07.responses import HttpResponseConflictingResource
from udj.views.views07.responses import HttpResponseNotAcceptable

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

  if len(password) < 8:
    return HttpResponseNotAcceptable("password")

  try:
    validate_email(email)
  except ValidationError:
    return HttpResponseNotAcceptable("email")

  #actuall do stuff
  if request.method == 'PUT':
    return createUser(request, username, email, password, first_name, last_name)
  else:
    return modifyUser(request, username, email, password, first_name, last_name)

@NeedsAuth
@transaction.commit_on_success
def modifyUser(request, username, email, first_name, last_name):
  if request.user.email != email and User.objects.filter(email=email).exists():
    return HttpResponseConflictingResource('email')

  if username != request.user.username:
    return HttpResponseNotAcceptable("username")

  request.user.email = json_param['email']
  request.user.first_name = json_param['first_name']
  request.user.last_name = json_param['last_name']
  request.user.set_password(password)
  return HttpResponse()

@transaction.commit_on_success
def createUser(request, username, email, password, first_name, last_name):

  if User.objects.filter(username=username).exists():
    return HttpResponseConflictingResource('username')

  if User.objects.filter(email=email).exists():
    return HttpResponseConflictingResource('email')

  if not re.compile(r'^[\w.@+-]+$').match(username):
    return HttpResponseNotAcceptable("username")

  newUser = User.objects.create_user(
      username,
      email,
      password
  )

  newUser.first_name = first_name
  newUser.last_name = last_name
  newUser.save()

  return HttpResponse(status=201)
