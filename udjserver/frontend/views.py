from django.template import Context, RequestContext, loader
from django.http import HttpResponse
from django.shortcuts import render_to_response
# Create your views here.

def home(request):
  """
  if request.method == 'POST':
    form = ApplicationForm(request.POST)
    if form.is_valid():
      #process form here!
      return HttpResponseRedirect('/thanks/')
  else:
    form = ApplicationForm()
  """
  return render_to_response('home.html', {'page' : 'home'}, context_instance=RequestContext(request))

def signup(request):
  return render_to_response('signup.html', {'page' : 'signup'}, context_instance=RequestContext(request))
