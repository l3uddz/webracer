# Various utility methods

def xpath_first(doc, expr):
    '''Performs a doc.xpath(expr) call and returns the first item of the result
    or None if no elements matched.
    '''
    
    nodes = doc.xpath(expr)
    if len(nodes) > 0:
        return nodes[0]
    else:
        return None

def xpath_first_check(doc, expr):
    '''Performs a doc.xpath(expr) call, asserts that the result has
    a non-zero length, and returns the first item of the result.
    '''
    
    nodes = doc.xpath(expr)
    assert len(nodes) > 0, 'No elements matching xpath: %s' % expr
    return nodes[0]
