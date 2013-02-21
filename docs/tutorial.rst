WebRacer Tutorial
=================

Agent
-----

Issuing requests with a WebRacer agent is pretty simple:

    import webracer
    agent = webracer.Agent()
    response = agent.get('http://localhost')
    # do something with the body
    body = response.body

Response objects have the expected assortment of useful methods:

    # case-insensitive header dictionary
    headers = response.header_dict

Test Case
---------

Same example done in a test case:

    import webracer
    
    class Test(webracer.WebTestCase):
        def test_index(self):
            self.get('http://localhost')
            self.assert_status(200)
            assert 'hello world' in self.response.body
