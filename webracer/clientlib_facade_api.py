class Response(object):
    '''Response facade.
    
    This class provides a common interface to response classes provided by
    various HTTP client libraries.
    
    It should not perform any caching; webracer's own Response will take
    care of that.
    
    Instances of this class are meant to be constructed by Request facade.
    '''
    
    @property
    def code(self):
        '''Returns the HTTP status code of the response, as an int.
        '''
        pass
    
    @property
    def raw_body(self):
        '''Returns raw body of the response.
        
        On Python 3, this should return bytes. On Python 2, str.
        '''
        pass
    
    @property
    def raw_cookies(self):
        '''Returns a list of cookies in the response.
        
        Return value should be a sequence of ocookie.Cookie objects.
        '''
        pass
    
    @property
    def raw_headers(self):
        '''Returns a list of headers in the response.
        
        Return value should be a sequence of (name, value) pairs.
        '''
        pass
