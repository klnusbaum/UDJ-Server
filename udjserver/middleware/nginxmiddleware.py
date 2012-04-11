class RemoteAddrMiddleware(object):
  def process_request(self, request):
    if 'HTTP_X_REAL_IP' in request.META:
      request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
