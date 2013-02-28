from django.http import HttpResponse

class HttpJSONResponse(HttpResponse):

  def __init__(self, content, status=200):
    super(HttpJSONResponse, self).__init__(content,
                                           status=status,
                                           content_type="text/json; charset=utf-8")
