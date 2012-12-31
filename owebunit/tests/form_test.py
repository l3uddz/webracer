import owebunit
import bottle
from owebunit.tests import utils

app = bottle.Bottle()

@app.route('/one-form')
def one_form():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form action='/there' method='post'>
        <input type='text' name='textf' value='textv' />
        <input type='submit' value='Go' />
        <button name='foo' />
    </form>
</body>
</html>
'''

@app.route('/subdir/relative_action_form')
def relative_action_form():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form action='in_subdir' method='post'>
        <input type='text' name='textf' value='textv' />
        <input type='submit' value='Go' />
        <button name='foo' />
    </form>
</body>
</html>
'''

@app.route('/no-attribute-form')
def no_attribute_form():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form>
        <input type='text' name='textf' value='textv' />
        <input type='submit' value='Go' />
        <button name='foo' />
    </form>
</body>
</html>
'''

@app.route('/form_with_select_not_selected')
def form_with_select_not_selected():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form>
        <select name='selectf'>
            <option value='first'>First</option>
            <option value='second'>Second</option>
            <option value='third'>Third</option>
        </select>
    </form>
</body>
</html>
'''

@app.route('/form_with_select_selected')
def form_with_select_selected():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form>
        <select name='selectf'>
            <option value='first'>First</option>
            <option value='second' selected='selected'>Second</option>
            <option value='third'>Third</option>
        </select>
    </form>
</body>
</html>
'''

utils.start_bottle_server(app, 8043)

@owebunit.config(host='localhost', port=8043)
class FormTestCase(owebunit.WebTestCase):
    def test_with_specified_attributes(self):
        self.get('/one-form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertEqual('/there', form.action)
        # always a full url
        self.assertEqual('http://localhost:8043/there', form.computed_action)
        self.assertEqual('post', form.method)
        self.assertEqual('post', form.computed_method)
    
    def test_without_specified_attributes(self):
        self.get('/no-attribute-form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertIs(form.action, None)
        self.assertEqual('http://localhost:8043/no-attribute-form', form.computed_action)
        self.assertIs(form.method, None)
        self.assertEqual('get', form.computed_method)
    
    def test_computed_action_relative(self):
        self.get('/subdir/relative_action_form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertEqual('in_subdir', form.action)
        self.assertEqual('http://localhost:8043/subdir/in_subdir', form.computed_action)
    
    def test_params(self):
        self.get('/no-attribute-form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        params = form.params_list
        if isinstance(params, list):
            params = tuple(params)
        expected = (('textf', 'textv'),)
        self.assertEqual(expected, params)
    
    def test_params_select_not_selected(self):
        self.get('/form_with_select_not_selected')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        params = form.params_list
        if isinstance(params, list):
            params = tuple(params)
        expected = (('selectf', 'first'),)
        self.assertEqual(expected, params)
    
    def test_params_select_selected(self):
        self.get('/form_with_select_selected')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        params = form.params_list
        if isinstance(params, list):
            params = tuple(params)
        expected = (('selectf', 'second'),)
        self.assertEqual(expected, params)

if __name__ == '__main__':
    import unittest
    unittest.main()
