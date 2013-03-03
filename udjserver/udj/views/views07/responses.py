from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from udj.headers import MISSING_RESOURCE_HEADER, FORBIDDEN_REASON_HEADER

class HttpJSONResponse(HttpResponse):

  def __init__(self, content, status=200):
    super(HttpJSONResponse, self).__init__(content,
                                           status=status,
                                           content_type="text/json; charset=utf-8")

class HttpResponseMissingResource(HttpResponseNotFound):

  def __init__(self, missing_resource):
    super(HttpResponseMissingResource, self).__init__()
    self[MISSING_RESOURCE_HEADER] = missing_resource

class HttpResponseForbiddenWithReason(HttpResponseForbidden):

  def __init__(self, reason):
    super(HttpMissingResponse, self).__init__()
    self[FORBIDDEN_REASON_HEADER] = reason
