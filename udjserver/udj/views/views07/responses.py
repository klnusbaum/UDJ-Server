from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from udj.headers import MISSING_RESOURCE_HEADER, FORBIDDEN_REASON_HEADER, CONFLICT_RESOURCE_HEADER, NOT_ACCEPTABLE_REASON_HEADER

class HttpJSONResponse(HttpResponse):

  def __init__(self, content, status=200):
    super(HttpJSONResponse, self).__init__(content,
                                           status=status,
                                           content_type="text/json; charset=utf-8")

class HttpResponseMissingResource(HttpResponseNotFound):

  def __init__(self, missing_resource):
    super(HttpResponseMissingResource, self).__init__()
    self[MISSING_RESOURCE_HEADER] = missing_resource

class HttpResponseConflictingResource(HttpResponse):

  def __init__(self, resource):
    super(HttpResponseConflictingResource, self).__init__(status=409)
    self[CONFLICT_RESOURCE_HEADER] = resource

class HttpResponseForbiddenWithReason(HttpResponseForbidden):

  def __init__(self, reason):
    super(HttpResponseForbiddenWithReason, self).__init__()
    self[FORBIDDEN_REASON_HEADER] = reason

class HttpResponseNotAcceptable(HttpResponse):

  def __init__(self, reason):
    super(HttpResponseNotAcceptable, self).__init__(status=406)
    self[NOT_ACCEPTABLE_REASON_HEADER] = reason

