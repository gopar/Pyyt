'''
Reference
- Pep 3333: https://peps.python.org/pep-3333/

- Advance Python Series
  - Knowledge of Python and data structures (eg, classes, decorators, magic methods, etc)
- Have worked with web frameworks before (django/flask/etc)
'''

HELLO_WORLD = b"Hello world!\n"

def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [HELLO_WORLD]


class Pyyt:
    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [HELLO_YOUTUBE]
