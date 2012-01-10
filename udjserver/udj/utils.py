from django.http import HttpResponse
def getJSONResponse(jsonContent, status=200):
  return HttpResponse(jsonContent, status=status, content_type='text/json')
