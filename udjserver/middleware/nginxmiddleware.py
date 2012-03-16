class RemoteAddrMiddleware(object):
  def process_request(self, request):
    request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
