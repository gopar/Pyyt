"""
Refactor to use a class and rough draft of basic web framework life cycle
"""
from typing import Dict, List, Callable

DEFAULT_CONTENT_TYPES = ["application/json", "text/html"]


class Pyyt:
    def __init__(
        routes: Dict, middleware: List = None, allowed_content_types: List[str] = None
    ):
        self.routes = routes
        self.middleware = middleware or []
        self.allowed_content_types = allowed_content_types or DEFAULT_CONTENT_TYPES

    def __call__(self, environ: Dict, start_response: Callable):
        request = Request(environ)
        if request.CONTENT_TYPE not in self.allowed_content_types:
            raise Error(f"{request.CONTENT_TYPE} not allowed")

        for middleware in self.middleware:
            request = middleware.preprocess_request(request)

        route = self.routes.get(request.PATH_INFO)
        if route is None:
            return 404

        route_method = getattr(route, request.REQUEST_METHOD.lower(), None)
        if route_method is None:
            return 405

        response = route_method()
        status, headers, body = response.wsgi_response()

        for middleware in self.middlewares:
            status, headers, body = middleware.postprocess_request(
                status, headers, body
            )

        start_response(status, headers)
        return [body]


app = Pyyt()
