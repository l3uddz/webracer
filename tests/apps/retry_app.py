import bottle

app = bottle.Bottle()

status_codes = []

@app.route('/')
def index():
    bottle.response.content_type = 'text/plain'
    if len(status_codes) == 0:
        bottle.response.status = 999
        return 'No status code found in status codes list'
    status_code = status_codes.pop(0)
    bottle.response.status = status_code
    return '%d as requested' % status_code
