default_content_types = ['application/json', 'text/html']

class Pyyt:
    '''
    A minimalistic web framework
    '''
    def __init__(
            self,
            routes,
            middleware=None,
            allowed_content_types=default_content_types
    ):
        self.routes = routes
        self.middleware = middleware or []
        self.allowed_content_types = allowed_content_types

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.CONTENT_TYPE not in self.allowed_content_types:
            raise Error('')

        for middleware in self.middlewares:
            request = middleware.preprocess_request(request)

        route = self.routes.get(request.PATH_INFO)
        if route is None:
            return 404

        route_method = getattr(route, request.REQUEST_METHOD.lower(), None)
        if response_method is None:
            return 405

        response = route_method()
        status, headers, body = response.wsgi_response()

        for middleware in self.middlewares:
            status, headers, body = middleware.postprocess_request(status, headers, body)

        start_response(status, response_headers)
        return [body]




class HumanEndpoint:
    def post(self, request):
        data = None
        return Response(content_type='application/json', body=data, status=201)

    def get(self, request):
        data = dict(a=1,b=2,c=3)
        return Response(content_type='application/json', body=data, status=200)


class Response:
    def __init__(self, content_type=None, body=None, status=None):
        self.content_type = content_type or 'application/json'
        self.body = body
        self.status =  status or 200

    def as_bytes(self):
        if self.content_type not in ['application/json', 'text/html']:
            raise Error('Invalid content type')

        conversion = {
            'application/json': json.dumps,
            'text/html': lambda body: body,
        }

        body = conversion[self.content_type](self.body).encode('utf-8')
        return body

    def wsgi_response(self):
        body = self.as_bytes()
        headers = [
            ('Content-Type', self.content_type),
            ('Content-Length', len(body))
        ]
        return (status, headers, body)


class Request:
    def __init__(self, environ):
        for key, value in environ.items():
            setattr(self, key.replace('.', '_'), value)
