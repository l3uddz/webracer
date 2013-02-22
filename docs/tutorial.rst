WebRacer Tutorial
=================

Agent
-----

Issuing requests with a WebRacer agent is pretty simple::

    import webracer
    agent = webracer.Agent()
    response = agent.get('http://localhost')
    # do something with the body
    body = response.body

Response objects have the expected assortment of useful methods::

    # case-insensitive header dictionary
    headers = response.headers

Test Case
---------

Same example done in a test case::

    import webracer
    
    class Test(webracer.WebTestCase):
        def test_index(self):
            self.get('http://localhost')
            self.assert_status(200)
            assert 'hello world' in self.response.body

Low Level Access
----------------

One of WebRacer's features is that it exposes data as it was received from
the network, with minimal processing.

For example, to access response body two properties are provided::

    # Body decoded to a string type
    body = response.body
    assert type(body) == string         # Python 3
    
    # Raw body as bytes
    raw_body = response.body
    assert type(body) == bytes          # Python 3

Similarly, for header access there are two properties as well::

    # Case-insensitive dictionary
    headers = response.headers
    # => {'Content-Type': 'text/html'}
    assert 'Content-Type' in headers == 'content-type' in headers
    
    # List of name-value pairs exactly as received
    raw_headers = response.raw_headers
    # => [('Content-Type', 'text/html')]
