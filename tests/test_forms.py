import mock
import unittest
from nose.tools import *

import tempfile
from bs4 import BeautifulSoup

from robobrowser.compat import builtin_name
from robobrowser.forms.form import Form, FormData, fields, _parse_fields


class TestFormData(unittest.TestCase):

    def setUp(self):
        self.form_data = FormData()
        self.form_data.add({'red': 'special'})

    def test_add_payload(self):
        self.form_data.add({'lazing': 'sunday'})
        assert_true('lazing' in self.form_data.payload)
        assert_equal(self.form_data.payload['lazing'], 'sunday')

    def test_add_by_key(self):
        self.form_data.add({'lazing': 'sunday'}, 'afternoon')
        assert_false('lazing' in self.form_data.payload)
        assert_true('afternoon' in self.form_data.options)
        assert_true('lazing' in self.form_data.options['afternoon'])
        assert_equal(
            self.form_data.options['afternoon']['lazing'],
            'sunday'
        )

    def test_requests_get(self):
        out = self.form_data.to_requests('get')
        assert_true('params' in out)
        assert_equal(out['params'], {'red': 'special'})

    def test_requests_post(self):
        out = self.form_data.to_requests('post')
        assert_true('data' in out)
        assert_equal(out['data'], {'red': 'special'})


class TestForm(unittest.TestCase):

    def setUp(self):
        self.html = '''
            <form>
                <input name="vocals" />
                <input name="guitar" type="file" />
                <select name="drums">
                    <option value="roger">Roger<br />
                    <option value="john">John<br />
                </select>
                <input type="radio" name="bass" value="Roger">Roger<br />
                <input type="radio" name="bass" value="John">John<br />
            </form>
        '''
        self.form = Form(self.html)

    def test_fields(self):
        keys = set(('vocals', 'guitar', 'drums', 'bass'))
        assert_equal(set(self.form.fields.keys()), keys)
        assert_equal(set(self.form.keys()), keys)

    def test_repr(self):
        assert_equal(
            repr(self.form),
            '<RoboForm vocals=, guitar=, drums=roger, bass=>'
        )

    def test_repr_empty(self):
        assert_equal(
            repr(Form('<form></form>')),
            '<RoboForm>'
        )


class TestParser(unittest.TestCase):

    def setUp(self):
        self.form = Form('<form></form>')

    def test_method_default(self):
        assert_equal(self.form.method, 'get')

    def test_method(self):
        form = Form('<form method="put"></form>')
        assert_equal(form.method, 'put')

    def test_action(self):
        form = Form('<form action="/"></form>')
        assert_equal(form.action, '/')

    def test_parse_input(self):
        html = '<input name="band" value="queen" />'
        _fields = _parse_fields(BeautifulSoup(html))
        assert_equal(len(_fields), 1)
        assert_true(isinstance(_fields['band'], fields.Input))

    def test_parse_file_input(self):
        html = '<input name="band" type="file" />'
        _fields = _parse_fields(BeautifulSoup(html))
        assert_equal(len(_fields), 1)
        assert_true(isinstance(_fields['band'], fields.FileInput))

    def test_parse_textarea(self):
        html = '<textarea name="band">queen</textarea>'
        _fields = _parse_fields(BeautifulSoup(html))
        assert_equal(len(_fields), 1)
        assert_true(isinstance(_fields['band'], fields.Textarea))

    def test_parse_radio(self):
        html = '''
            <input type="radio" name="favorite_member" />freddie<br />
            <input type="radio" name="favorite_member" />brian<br />
            <input type="radio" name="favorite_member" />roger<br />
            <input type="radio" name="favorite_member" />john<br />
            <input type="radio" name="favorite_song" />rhapsody<br />
            <input type="radio" name="favorite_song" />killer<br />
        '''
        _fields = _parse_fields(BeautifulSoup(html))
        assert_equal(len(_fields), 2)
        assert_true(isinstance(_fields['favorite_member'], fields.Radio))
        assert_true(isinstance(_fields['favorite_song'], fields.Radio))
        assert_equal(
            len(_fields['favorite_member']._parsed), 4
        )
        assert_equal(
            len(_fields['favorite_song']._parsed), 2
        )

    def test_parse_checkbox(self):
        html = '''
            <input type="checkbox" name="favorite_member" />freddie<br />
            <input type="checkbox" name="favorite_member" />brian<br />
            <input type="checkbox" name="favorite_member" />roger<br />
            <input type="checkbox" name="favorite_member" />john<br />
            <input type="checkbox" name="favorite_song" />rhapsody<br />
            <input type="checkbox" name="favorite_song" />killer<br />
        '''
        _fields = _parse_fields(BeautifulSoup(html))
        assert_equal(len(_fields), 2)
        assert_true(isinstance(_fields['favorite_member'], fields.Checkbox))
        assert_true(isinstance(_fields['favorite_song'], fields.Checkbox))
        assert_equal(
            len(_fields['favorite_member']._parsed), 4
        )
        assert_equal(
            len(_fields['favorite_song']._parsed), 2
        )

    def test_parse_select(self):
        html = '''
            <select name="instrument">
                <option value="vocals">vocals</option>
                <option value="guitar">guitar</option>
                <option value="drums">drums</option>
                <option value="bass">bass</option>
            </select>
        '''
        _fields = _parse_fields(BeautifulSoup(html))
        assert_equal(len(_fields), 1)
        assert_true(isinstance(_fields['instrument'], fields.Select))

    def test_parse_select_multi(self):
        html = '''
            <select name="instrument" multiple>
                <option value="vocals">vocals</option>
                <option value="guitar">guitar</option>
                <option value="drums">drums</option>
                <option value="bass">bass</option>
            </select>
        '''
        _fields = _parse_fields(BeautifulSoup(html))
        assert_equal(len(_fields), 1)
        assert_true(isinstance(_fields['instrument'], fields.MultiSelect))


class TestInput(unittest.TestCase):

    def setUp(self):
        self.html = '<input name="brian" value="may" />'
        self.input = fields.Input(BeautifulSoup(self.html).find('input'))

    def test_name(self):
        assert_equal(self.input.name, 'brian')

    def test_initial(self):
        assert_equal(self.input._value, 'may')
        assert_equal(self.input.value, 'may')

    def test_value(self):
        self.input.value = 'red special'
        assert_equal(self.input._value, 'red special')
        assert_equal(self.input.value, 'red special')

    def test_serialize(self):
        assert_equal(
            self.input.serialize(),
            {'brian': 'may'}
        )


class TestInputBlank(unittest.TestCase):

    def setUp(self):
        self.html = '<input name="blank" />'
        self.input = fields.Input(BeautifulSoup(self.html).find('input'))

    def test_initial(self):
        assert_equal(self.input._value, None)
        assert_equal(self.input.value, '')

    def test_serialize(self):
        assert_equal(
            self.input.serialize(),
            {'blank': ''}
        )


class TestTextarea(unittest.TestCase):

    def setUp(self):
        self.html = '<textarea name="roger">taylor</textarea>'
        self.input = fields.Textarea(BeautifulSoup(self.html).find('textarea'))

    def test_name(self):
        assert_equal(self.input.name, 'roger')

    def test_initial(self):
        assert_equal(self.input._value, 'taylor')
        assert_equal(self.input.value, 'taylor')

    def test_value(self):
        self.input.value = 'the drums'
        assert_equal(self.input._value, 'the drums')
        assert_equal(self.input.value, 'the drums')

    def test_serialize(self):
        assert_equal(
            self.input.serialize(),
            {'roger': 'taylor'}
        )


class TestTextareaBlank(unittest.TestCase):

    def setUp(self):
        self.html = '<textarea name="blank"></textarea>'
        self.input = fields.Textarea(BeautifulSoup(self.html).find('textarea'))

    def test_initial(self):
        assert_equal(self.input._value, '')
        assert_equal(self.input.value, '')

    def test_serialize(self):
        assert_equal(
            self.input.serialize(),
            {'blank': ''}
        )


class TestSelect(unittest.TestCase):

    def setUp(self):
        self.html = '''
            <select name="john">
                <option value="tie">your mother down</option>
                <option value="you're" selected>my best friend</option>
                <option value="the">millionaire waltz</option>
            </select>
        '''
        self.input = fields.Select(BeautifulSoup(self.html).find('select'))

    def test_name(self):
        assert_equal(self.input.name, 'john')

    def test_options(self):
        assert_equal(
            self.input.options,
            ['tie', "you're", 'the']
        )

    def test_initial(self):
        assert_equal(self.input._value, 1)
        assert_equal(self.input.value, "you're")

    def test_value(self):
        self.input.value = 'the'
        assert_equal(self.input._value, 2)
        assert_equal(self.input.value, 'the')

    def test_value_label(self):
        self.input.value = 'millionaire waltz'
        assert_equal(self.input._value, 2)
        assert_equal(self.input.value, 'the')

    def test_serialize(self):
        assert_equal(
            self.input.serialize(),
            {'john': "you're"}
        )


class TestSelectBlank(unittest.TestCase):

    def setUp(self):
        self.html = '''
            <select name="john">
                <option value="tie">your mother down</option>
                <option value="you're">my best friend</option>
                <option value="the">millionaire waltz</option>
            </select>
        '''
        self.input = fields.Select(BeautifulSoup(self.html).find('select'))

    def test_name(self):
        assert_equal(self.input.name, 'john')

    def test_initial(self):
        assert_equal(self.input._value, 0)
        assert_equal(self.input.value, 'tie')

    def test_serialize(self):
        assert_equal(
            self.input.serialize(),
            {'john': 'tie'}
        )


class TestMultiSelect(unittest.TestCase):

    def setUp(self):
        self.html = '''
            <select name="john" multiple>
                <option value="tie">your mother down</option>
                <option value="you're" selected>my best friend</option>
                <option value="the">millionaire waltz</option>
            </select>
        '''
        self.input = fields.MultiSelect(BeautifulSoup(self.html).find('select'))


class TestMixedCase(unittest.TestCase):

    def test_upper_type(self):
        html = '''
            <input type="RADIO" name="members" value="mercury" />vocals<br />
        '''
        input = fields.Radio(BeautifulSoup(html).find_all('input'))
        assert_equal(input.name, 'members')

    def test_upper_name(self):
        html = '''
            <input type="radio" NAME="members" value="mercury" />vocals<br />
        '''
        input = fields.Radio(BeautifulSoup(html).find_all('input'))
        assert_equal(input.name, 'members')

    def test_mixed_radio_names(self):
        html = '''
            <input type="radio" NAME="members" value="mercury" />vocals<br />
            <input type="radio" NAME="MEMBERS" value="may" />guitar<br />
        '''
        input = fields.Radio(BeautifulSoup(html).find_all('input'))
        assert_equal(input.name, 'members')
        assert_equal(
            input.options,
            ['mercury', 'may']
        )


class TestRadio(unittest.TestCase):

    def setUp(self):
        self.html = '''
            <input type="radio" name="members" value="mercury" checked />vocals<br />
            <input type="radio" name="members" value="may" />guitar<br />
            <input type="radio" name="members" value="taylor" />drums<br />
            <input type="radio" name="members" value="deacon" checked />bass<br />
        '''
        self.input = fields.Radio(BeautifulSoup(self.html).find_all('input'))

    def test_name(self):
        assert_equal(self.input.name, 'members')

    def test_options(self):
        assert_equal(
            self.input.options,
            ['mercury', 'may', 'taylor', 'deacon']
        )

    def test_initial(self):
        assert_equal(self.input.value, 'mercury')

    def test_value(self):
        self.input.value = 'taylor'
        assert_equal(self.input._value, 2)
        assert_equal(self.input.value, 'taylor')

    def test_value_label(self):
        self.input.value = 'drums'
        assert_equal(self.input._value, 2)
        assert_equal(self.input.value, 'taylor')

    def test_serialize(self):
        assert_equal(
            self.input.serialize(),
            {'members': 'mercury'}
        )


class TestRadioBlank(unittest.TestCase):

    def setUp(self):
        self.html = '''
            <input type="radio" name="member" value="mercury" />vocals<br />
            <input type="radio" name="member" value="may" />guitar<br />
            <input type="radio" name="member" value="taylor" />drums<br />
            <input type="radio" name="member" value="deacon" />bass<br />
        '''
        self.input = fields.Radio(BeautifulSoup(self.html).find_all('input'))

    def test_initial(self):
        assert_equal(self.input.value, '')

    def test_serialize(self):
        assert_equal(
            self.input.serialize(),
            {'member': ''}
        )


class TestCheckbox(unittest.TestCase):

    def setUp(self):
        self.html = '''
            <input type="checkbox" name="member" value="mercury" checked />vocals<br />
            <input type="checkbox" name="member" value="may" />guitar<br />
            <input type="checkbox" name="member" value="taylor" />drums<br />
            <input type="checkbox" name="member" value="deacon" checked />bass<br />
        '''
        self.input = fields.Checkbox(BeautifulSoup(self.html).find_all('input'))

    def test_name(self):
        assert_equal(self.input.name, 'member')

    def test_options(self):
        assert_equal(
            self.input.options,
            ['mercury', 'may', 'taylor', 'deacon']
        )

    def test_initial(self):
        assert_equal(
            self.input.value,
            ['mercury', 'deacon']
        )

    def test_value(self):
        self.input.value = 'taylor'
        assert_equal(self.input._value, [2])
        assert_equal(self.input.value, ['taylor'])

    def test_value(self):
        self.input.value = ['taylor', 'deacon']
        assert_equal(self.input._value, [2, 3])
        assert_equal(self.input.value, ['taylor', 'deacon'])

    def test_value_label(self):
        self.input.value = 'drums'
        assert_equal(self.input._value, [2])
        assert_equal(self.input.value, ['taylor'])

    def test_serialize(self):
        assert_equal(
            self.input.serialize(),
            {'member': ['mercury', 'deacon']}
        )


class TestCheckboxBlank(unittest.TestCase):

    def setUp(self):
        self.html = '''
            <input type="checkbox" name="member" value="mercury" />vocals<br />
            <input type="checkbox" name="member" value="may" />guitar<br />
            <input type="checkbox" name="member" value="taylor" />drums<br />
            <input type="checkbox" name="member" value="deacon" />bass<br />
        '''
        self.input = fields.Checkbox(BeautifulSoup(self.html).find_all('input'))

    def test_initial(self):
        assert_equal(
            self.input.value, []
        )

    def test_serialize(self):
        assert_equal(
            self.input.serialize(),
            {'member': []}
        )


class TestFileInput(unittest.TestCase):

    def setUp(self):
        self.html = '<input name="song" type="file" />'
        self.input = fields.FileInput(BeautifulSoup(self.html).find('input'))

    def test_name(self):
        assert_equal(self.input.name, 'song')

    def test_value_file(self):
        file = tempfile.TemporaryFile('r')
        self.input.value = file
        assert_equal(self.input._value, file)
        assert_equal(self.input.value, file)

    @mock.patch('{0}.open'.format(builtin_name))
    def test_value_name(self, mock_open):
        file = tempfile.TemporaryFile('r')
        mock_open.return_value = file
        self.input.value = 'temp'
        assert_equal(self.input._value, file)
        assert_equal(self.input.value, file)

    def test_serialize(self):
        file = tempfile.TemporaryFile('r')
        self.input.value = file
        assert_equal(
            self.input.serialize(),
            {'song': file}
        )
