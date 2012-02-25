from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.forms import UserCreationForm
# Create your views here.

def home(request):
  return render_to_response('home.html', {'page' : 'home'}, context_instance=RequestContext(request))

def register(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      new_user = form.save()
      return HttpResponseRedirect("/registration/thanks/")
  else:
    form = UserCreationForm()
  return render_to_response("registration/register.html", { 'page' : 'login', 'form': form, },
      context_instance=RequestContext(request))

def thanks(request):
  return render_to_response("registration/thanks.html", {},
      context_instance=RequestContext(request))

