import json
import bottle

app = bottle.Bottle()

@app.route('/one_form')
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

@app.route('/no_attribute_form')
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

@app.route('/form_with_two_submits')
def form_with_two_submits():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form action='/dump_params'>
        <input type='submit' name='submit-first' value='first' />
        <input type='submit' name='submit-second' value='second' />
    </form>
</body>
</html>
'''

@app.route('/first_radio_selected')
def first_radio_selected():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form action='/dump_params'>
        <input type='radio' name='field' value='first' checked='checked' />
        <input type='radio' name='field' value='second' />
        <input type='submit' />
    </form>
</body>
</html>
'''

@app.route('/second_radio_selected')
def second_radio_selected():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form action='/dump_params'>
        <input type='radio' name='field' value='first' />
        <input type='radio' name='field' value='second' checked='checked' />
        <input type='submit' />
    </form>
</body>
</html>
'''

@app.route('/checkboxes')
def checkboxes():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form action='/dump_params'>
        <input type='checkbox' name='field' value='first' />
        <input type='checkbox' name='field' value='second' checked='checked' />
        <input type='submit' />
    </form>
</body>
</html>
'''

@app.route('/empty_textarea')
def empty_textarea():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form action='/dump_params'>
        <textarea name='field'></textarea>
        <input type='submit' />
    </form>
</body>
</html>
'''

@app.route('/textarea')
def textarea():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form action='/dump_params'>
        <textarea name='field'>hello world</textarea>
        <input type='submit' />
    </form>
</body>
</html>
'''

@app.route('/form_retrieval')
def form_retrieval():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form action='by-class' class='testclass'>
    </form>
    <form action='by-id' id='formid'>
    </form>
    <form action='by-name' name='testname'>
    </form>
    <form action='by-class-and-id' class='testclass' id='formid2'>
    </form>
    <form action='by-name-and-id' name='testname3' id='testid3'>
</body>
</html>
'''

@app.route('/dump_params')
def dump_params():
    return json.dumps(dict(bottle.request.forms))
