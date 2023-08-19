"""
Add:
- Response class
- Endpoint class
- Handle method not allowed (405)
- Example of handling requests

Terminal:
http -v -j POST 127.0.0.1:8000/cars car="nani"
http -v -j DELETE 127.0.0.1:8000/cars car="nani"
"""
import json
from typing import Dict, List, Optional
from http import HTTPStatus

DEFAULT_CONTENT_TYPES = ["application/json", "text/html"]


class Pyyt:
    """
    A minimalistic web framework
    """

    def __init__(
        self,
        routes: Dict,
        middlewares: List = None,
        allowed_content_types: List[str] = None,
    ):
        self.routes = routes
        self.middlewares = middlewares or []
        self.allowed_content_types = allowed_content_types or DEFAULT_CONTENT_TYPES

    def __call__(self, environ, start_response):
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

            # Correct way is to handle the content type sent and answer in the same content type
            response_headers = [("Content-Type", "text/html")]
            start_response(status, response_headers)
            return []

        route_method = getattr(route, request.REQUEST_METHOD.lower(), None)
        if route_method is None:
            status = HTTPStatus.METHOD_NOT_ALLOWED
            status = f"{int(status)} {status.phrase}"
            response_headers = [("Content-Type", "text/html")]
            start_response(status, response_headers)
            return []

        response = route_method(request)
        status, headers, body = response.wsgi_response()

        for middleware in self.middlewares:
            status, headers, body = middleware.postprocess_request(
                status, headers, body
            )

        start_response(status, headers)
        return body


class Request:
    def __init__(self, environ):
        for key, value in environ.items():
            setattr(self, key.replace(".", "_"), value)


class Response:
    def __init__(
        self, content_type=None, body=None, status: Optional[HTTPStatus] = None
    ):
        self.content_type = content_type or "application/json"
        self.body = body
        self.status = status or HTTPStatus.OK
        self.status = f"{int(self.status)} {self.status.phrase}"

    def as_bytes(self):
        if self.content_type not in ["application/json", "text/html"]:
            raise Error("Invalid content type")

        conversion = {
            "application/json": json.dumps,
            "text/html": lambda body: body,
        }

        body = conversion[self.content_type](self.body).encode("utf-8")
        return [body]

    def wsgi_response(self):
        body = self.as_bytes()
        length = sum(len(b) for b in body)
        headers = [
            ("Content-Type", self.content_type),
            ("Content-Length", str(length)),
        ]
        return (self.status, headers, body)


class CarsEndpoint:
    def get(self, request: Request):
        return Response(
            body={"cars": ["Dodge", "Honda", "Kia", "Toyota"]},
            status=HTTPStatus.OK,
        )

    def post(self, request: Request):
        payload = json.loads(request.wsgi_input.read())
        new_car = payload["car"]
        return Response(
            body={"cars": [new_car, "Dodge", "Honda", "Kia", "Toyota"]},
            status=HTTPStatus.CREATED,
        )


app = Pyyt(routes={"/cars": CarsEndpoint()})
