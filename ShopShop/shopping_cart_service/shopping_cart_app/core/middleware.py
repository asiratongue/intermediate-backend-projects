from django.utils.deprecation import MiddlewareMixin
from shopping_cart_app.core.context import set_request_context

class EndpointContextMiddleware(MiddlewareMixin):
    """Attaches the request path to thread-local storage."""
    def process_request(self, request):
        set_request_context(request)  # Store the request path
        return None
    
#ASK DEEPSEEK TO EXPLAIN DIS AT A DEEP LEVEL