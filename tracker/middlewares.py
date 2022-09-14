from threading import current_thread
from django.utils.deprecation import MiddlewareMixin


_requests = {}

def get_request():
    '''
    Returns the current thread for the response object.
    '''
    t = current_thread()
    if t not in _requests:
         return None
    return _requests[t]

class RequestMiddleware(MiddlewareMixin):
    '''
    RequestMiddleware is a middleware that is used to get the current request object.
    '''
    def process_request(self, request):
        _requests[current_thread()] = request