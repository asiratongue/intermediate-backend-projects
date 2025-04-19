import threading

_request_context = threading.local()

def set_request_context(request):
    _request_context.request = request 

def get_request_context():
    return getattr(_request_context, 'request', None)