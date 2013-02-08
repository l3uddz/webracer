import bottle

app = bottle.Bottle()

@app.route('/xml')
def xml():
    bottle.response.content_type = 'application/xml'
    return '<rootelement><element><subelement>text</subelement></element></rootelement>'

@app.route('/html')
def html():
    bottle.response.content_type = 'text/html'
    return '<!doctype html><html><head><meta name=foo value=bar></head><body></body></html>'
