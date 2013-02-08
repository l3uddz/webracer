import nose
import webracer

def test_repr_with_no_params():
    params = webracer.FormParams([])
    r = repr(params)
    nose.tools.assert_equal('<webracer.FormParams: []>', r)

def test_repr_with_one_element():
    yield check_repr_with_one_element_sequence, [['name', 'value']]
    yield check_repr_with_one_element_sequence, (('name', 'value'),)

def check_repr_with_one_element_sequence(seq):
    params = webracer.FormParams(seq)
    r = repr(params)
    nose.tools.assert_equal('<webracer.FormParams: [name=value]>', r)

def test_repr_with_two_elements():
    yield check_repr_with_two_element_sequence, [['name1', 'value1'], ['name2', 'value2']]
    yield check_repr_with_two_element_sequence, (('name1', 'value1'), ('name2', 'value2'))

def check_repr_with_two_element_sequence(seq):
    params = webracer.FormParams(seq)
    r = repr(params)
    nose.tools.assert_equal('<webracer.FormParams: [name1=value1, name2=value2]>', r)
