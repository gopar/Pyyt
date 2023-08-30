"""
Add:
- Request class
- Invalid content type handling
- Handle 404

Terminal:
https://github.com/httpie/cli
http -v GET 127.0.0.1:8000 -f
http -v GET 127.0.0.1:8000/hello -j
"""
from typing import Dict, List, Callable
from http import HTTPStatus

DEFAULT_CONTENT_TYPES = ["application/json", "text/html"]


class Pyyt:
    def __init__(
        self,
        routes: Dict,
        middleware: List = None,
        allowed_content_types: List[str] = None,
    ):
        self.routes = routes
        self.middlewares = middleware or []
        self.allowed_content_types = allowed_content_types or DEFAULT_CONTENT_TYPES

    def __call__(self, environ: Dict, start_response: Callable):
        request = Request(environ)
        if (
            not hasattr(request, "CONTENT_TYPE")
            or request.CONTENT_TYPE not in self.allowed_content_types
        ):
            status = HTTPStatus.UNSUPPORTED_MEDIA_TYPE
            status = f"{int(status)} {status.phrase}"
            response_headers = [
                ("Content-Type", "text/html"),
                ("Accept", ", ".join(self.allowed_content_types)),
            ]
            start_response(status, response_headers)
            return []

        for middleware in self.middlewares:
            request = middleware.preprocess_request(request)

        route = self.routes.get(request.PATH_INFO)
        if route is None:
            status = HTTPStatus.NOT_FOUND
            status = f"{int(status)} {status.phrase}"
            response_headers = [("Content-Type", "text/html")]
            start_response(status, response_headers)
            return []

        route_method = getattr(route, request.REQUEST_METHOD.lower(), None)
        if route_method is None:
            return 405

        response = route_method()
        status, headers, body = response.wsgi_responsea()

        for middleware in self.middlewares:
            status, headers, body = middleware.postprocess_request(
                status, headers, body, request
            )

        start_response(status, headers)
        return [body]


class Request:
    def __init__(self, environ: Dict):
        for key, value in environ.items():
            setattr(self, key.replace(".", "_"), value)


app = Pyyt({})
