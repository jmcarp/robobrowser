"""
HTML forms
"""

import re
from robobrowser.compat import OrderedDict

from . import fields
from .. import helpers

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
    name = tag.get('name').lower()
    while tags and tags[0].get('name').lower() == name:
        grouped.append(tags.pop(0))
    return grouped

def _parse_fields(parsed):
    """Parse form fields from HTML.

    :param BeautifulSoup parsed: Parsed HTML
    :return OrderedDict: Collection of field objects

    """
    # Note: Call this `rv` to avoid name conflict with `fields` module
    rv = OrderedDict()

    # Prepare field tags
    tags = parsed.find_all(_tag_ptn)
    for tag in tags:
        helpers.lowercase_attr_names(tag)

    while tags:

        tag = tags.pop(0)
        tag_type = tag.name.lower()

        # Get name attribute, skipping if undefined
        name = tag.get('name')
        if name is None:
            continue
        name = name.lower()

        field = None

        # Create form field
        if tag_type == 'input':
            tag_type = tag.get('type', '').lower()
            if tag_type == 'file':
                field = fields.FileInput(tag)
            elif tag_type == 'radio':
                radios = _group_flat_tags(tag, tags)
                field = fields.Radio(radios)
            elif tag_type == 'checkbox':
                checkboxes = _group_flat_tags(tag, tags)
                field = fields.Checkbox(checkboxes)
            else:
                field = fields.Input(tag)
        elif tag_type == 'textarea':
            field = fields.Textarea(tag)
        elif tag_type == 'select':
            if tag.get('multiple') is not None:
                field = fields.MultiSelect(tag)
            else:
                field = fields.Select(tag)

        # Add field
        if field is not None:
            rv[name] = field

    return rv

class Form(object):
    """Representation of an HTML form."""

    def __init__(self, parsed):
        parsed = helpers.ensure_soup(parsed)
        if parsed.name != 'form':
            parsed = parsed.find('form')
        self.parsed = parsed
        self.action = self.parsed.get('action')
        self.method = self.parsed.get('method', 'get')
        self.fields = _parse_fields(self.parsed)

    def __repr__(self):
        state = ', '.join(
            [
                '{0}={1}'.format(name, field.value)
                for name, field in self.fields.iteritems()
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
        """Serialize each form field and collect the results in a dictionary
        of dictionaries. Different fields may serialize their contents to
        different sub-dictionaries: most serialize to data, but file inputs
        serialize to files. Sub-dictionary keys should correspond to
        parameters of requests.Request.

        :return dict: Dict-of-dicts of serialized data

        """
        rv = {}
        for field in self.fields.values():
            key = field._serialize_key
            if key not in rv:
                rv[key] = {}
            rv[key].update(field.serialize())
        return rv
