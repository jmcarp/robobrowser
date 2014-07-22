"""
HTML forms.
"""

import re
import collections

from robobrowser.compat import OrderedDict, iteritems

from . import fields
from .. import helpers
from .. import exceptions


_tags = ['input', 'textarea', 'select']
_tag_ptn = re.compile(
    '|'.join(_tags),
    re.I
)


def _group_flat_tags(tag, tags):
    """Extract tags sharing the same name as the provided tag. Used to collect
    options for radio and checkbox inputs.

    :param Tag tag: BeautifulSoup tag
    :param list tags: List of tags
    :return: List of matching tags

    """
    grouped = [tag]
    name = tag.get('name', '').lower()
    while tags and tags[0].get('name', '').lower() == name:
        grouped.append(tags.pop(0))
    return grouped


def _parse_field(tag, tags):

    tag_type = tag.name.lower()

    if tag_type == 'input':
        tag_type = tag.get('type', '').lower()
        if tag_type == 'file':
            return fields.FileInput(tag)
        elif tag_type == 'radio':
            radios = _group_flat_tags(tag, tags)
            return fields.Radio(radios)
        elif tag_type == 'checkbox':
            checkboxes = _group_flat_tags(tag, tags)
            return fields.Checkbox(checkboxes)
        else:
            return fields.Input(tag)
    elif tag_type == 'textarea':
        return fields.Textarea(tag)
    elif tag_type == 'select':
        if tag.get('multiple') is not None:
            return fields.MultiSelect(tag)
        else:
            return fields.Select(tag)


def _parse_fields(parsed):
    """Parse form fields from HTML.

    :param BeautifulSoup parsed: Parsed HTML
    :return OrderedDict: Collection of field objects

    """
    # Note: Call this `out` to avoid name conflict with `fields` module
    out = []

    # Prepare field tags
    tags = parsed.find_all(_tag_ptn)
    for tag in tags:
        helpers.lowercase_attr_names(tag)

    while tags:
        tag = tags.pop(0)
        try:
            field = _parse_field(tag, tags)
        except exceptions.InvalidNameError:
            continue
        if field is not None:
            out.append(field)

    return out


class FormData(object):
    """Container for serialized form outputs that knows how to export to
    the format expected by Requests. By default, form values are stored in
    `payload`.

    """
    def __init__(self):
        self.payload = {}
        self.options = collections.defaultdict(dict)

    def add(self, data, key=None):
        """Add field values to container.

        :param dict data: Serialized values for field
        :param str key: Optional key; if not provided, values will be added
            to `self.payload`.

        """
        sink = self.options[key] if key is not None else self.payload
        sink.update(data)

    def to_requests(self, method='get'):
        """Export to Requests format.

        :param str method: Request method
        :return: Dict of keyword arguments formatted for `requests.request`

        """
        out = {}
        payload_key = 'params' if method.lower() == 'get' else 'data'
        out[payload_key] = self.payload
        out.update(self.options)
        return out


class Form(object):
    """Representation of an HTML form."""

    def __init__(self, parsed):
        parsed = helpers.ensure_soup(parsed)
        if parsed.name != 'form':
            parsed = parsed.find('form')
        self.parsed = parsed
        self.action = self.parsed.get('action')
        self.method = self.parsed.get('method', 'get')
        self.fields = OrderedDict()
        for field in _parse_fields(self.parsed):
            self.add_field(field)

    def add_field(self, field):
        """Add a field.

        :param field: Field to add
        :raise: ValueError if `field` is not an instance of `BaseField`.

        """
        if not isinstance(field, fields.BaseField):
            raise ValueError('Argument "field" must be an instance of '
                             'BaseField')
        self.fields[field.name] = field

    def __repr__(self):
        state = ', '.join(
            [
                '{0}={1}'.format(name, field.value)
                for name, field in iteritems(self.fields)
            ]
        )
        if state:
            return '<RoboForm {0}>'.format(state)
        return '<RoboForm>'

    def keys(self):
        return self.fields.keys()

    def __getitem__(self, item):
        return self.fields[item]

    def __setitem__(self, key, value):
        self.fields[key].value = value

    def serialize(self):
        """Serialize each form field to a FormData container.

        :return: FormData instance

        """
        form_data = FormData()
        for field in self.fields.values():
            form_data.add(field.serialize(), field.form_data_key)
        return form_data
