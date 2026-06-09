from urllib.parse import urlparse


class SameOriginCsrfHeaderMiddleware:
    """Supply CSRF header from the cookie when same-origin form posts omit it."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.method == 'POST'
            and 'HTTP_X_CSRFTOKEN' not in request.META
            and request.COOKIES.get('csrftoken')
            and self._is_same_origin(request)
        ):
            request.META['HTTP_X_CSRFTOKEN'] = request.COOKIES['csrftoken']

        return self.get_response(request)

    def _is_same_origin(self, request):
        host = request.get_host()
        origin = request.META.get('HTTP_ORIGIN')
        referer = request.META.get('HTTP_REFERER')

        if origin:
            return urlparse(origin).netloc == host
        if referer:
            return urlparse(referer).netloc == host

        return False
