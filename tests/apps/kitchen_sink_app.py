import bottle

app = bottle.Bottle()

@app.route('/ok')
def ok():
    return 'ok'

@app.route('/internal_server_error')
def internal_error():
    bottle.abort(500, 'internal server error')

@app.route('/unhandled_exception')
def unhandled_exception():
    raise ValueError('This is an unhandled exception')

@app.route('/redirect')
def redirect():
    bottle.redirect('/found', 302)

@app.route('/found')
def found():
    return 'found'

@app.route('/redirect_to')
def redirect():
    bottle.redirect(bottle.request.query.target, 302)

@app.route('/set_cookie')
def set_cookie():
    bottle.response.set_cookie('visited', 'yes')
    return 'ok'

@app.route('/set_cookie_value')
def set_cookie_value():
    bottle.response.set_cookie('sink', bottle.request.query.v)
    return bottle.request.query.v

@app.route('/set_multiple_cookies')
def set_multiple_cookies():
    bottle.response.set_cookie('foo_a', 'a_value', expires=1)
    bottle.response.set_cookie('foo_b', 'b_value', httponly=True)
    bottle.response.set_cookie('foo_c', 'c_value', secure=True)

@app.route('/read_cookie')
def read_cookie():
    return bottle.request.get_cookie('visited')

@app.route('/read_cookie_value/:name')
def read_cookie_value(name):
    return bottle.request.get_cookie(name)

@app.route('/get_param')
def get_param():
    return bottle.request.query.p

@app.route('/param', method='POST')
def param():
    return bottle.request.forms.p

@app.route('/get_content_length', method='POST')
def get_content_length():
    return bottle.request.headers.get('content-length')

@app.route('/get_user_agent')
def get_user_agent():
    return bottle.request.headers.get('user-agent')

@app.route('/json/empty')
def get_json_empty():
    return '{}'

@app.route('/json/hash')
def get_json_empty():
    return '{"a": "b"}'
