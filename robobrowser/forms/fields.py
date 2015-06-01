"""
HTML form fields.
"""

import abc
import six

from robobrowser.compat import string_types
from robobrowser import helpers
from robobrowser import exceptions


class BaseField(six.with_metaclass(abc.ABCMeta, object)):
    """Abstract base class for form fields.

    :param parsed: String or BeautifulSoup tag
    """
    def __init__(self, parsed):
        self._parsed = helpers.ensure_soup(parsed, parser='html.parser')
        self._value = None
        self.name = self._get_name(self._parsed)

    @property
    def disabled(self):
        return 'disabled' in self._parsed.attrs

    def _get_name(self, parsed):
        name = parsed.get('name')
        if name is not None:
            return name
        raise exceptions.InvalidNameError

    # Different form fields may serialize their values under different keys.
    # See `FormData` for details.
    payload_key = None

    def serialize(self):
        return {self.name: self.value}

    @property
    def value(self):
        return self._value if self._value else ''

    @value.setter
    def value(self, value):
        self._value = value


class Input(BaseField):

    def __init__(self, parsed):
        super(Input, self).__init__(parsed)
        self.value = self._parsed.get('value')


class Submit(Input):
    pass


class FileInput(BaseField):

    @BaseField.value.setter
    def value(self, value):
        if hasattr(value, 'read'):
            self._value = value
        elif isinstance(value, string_types):
            self._value = open(value)
        else:
            raise ValueError('Value must be a file object or file path')

    # Serialize value to 'files' key for compatibility with file attachments
    # in requests.
    payload_key = 'files'


class MultiOptionField(BaseField):

    def __init__(self, parsed):
        super(MultiOptionField, self).__init__(parsed)
        self.options, self.labels, initial = self._get_options(parsed)
        self._set_initial(initial)

    @abc.abstractmethod
    def _get_options(self, parsed):
        return [], [], []

    def _set_initial(self, initial):
        self._value = None
        try:
            self.value = initial[0]
        except IndexError:
            pass

    def _value_to_index(self, value):
        if value in self.options:
            return self.options.index(value)
        if value in self.labels:
            return self.labels.index(value)
        raise ValueError('Option {0} not found in field {1!r}'.format(value, self))

    @property
    def value(self):
        if self._value is None:
            return ''
        return self.options[self._value]

    @value.setter
    def value(self, value):
        self._value = self._value_to_index(value)


class MultiValueField(MultiOptionField):

    def _set_initial(self, initial):
        self.value = initial

    @property
    def value(self):
        return [
            self.options[idx]
            for idx in self._value
        ]

    @value.setter
    def value(self, value):
        if not isinstance(value, list):
            value = [value]
        self._value = [
            self._value_to_index(item)
            for item in value
        ]

    # List-like methods
    def append(self, value):
        index = self._value_to_index(value)
        if index in self._value:
            raise ValueError('Option {0} already in field {1!r}'.format(value, self))
        self._value.append(index)
        self._value.sort()

    def remove(self, value):
        index = self._value_to_index(value)
        self._value.remove(index)


class FlatOptionField(MultiOptionField):

    @property
    def disabled(self):
        return all('disabled' in each.attrs for each in self._parsed)

    def _get_name(self, parsed):
        return super(FlatOptionField, self)._get_name(parsed[0])

    def _get_options(self, parsed):
        options, labels, initial = [], [], []
        for option in parsed:
            value = option.get('value', 'on')
            checked = option.get('checked')
            options.append(value)
            labels.append(
                option.next.string
                if isinstance(option.next, string_types)
                else None
            )
            if checked is not None:
                initial.append(value)
        return options, labels, initial


class NestedOptionField(MultiOptionField):

    @property
    def disabled(self):
        return (
            super(NestedOptionField, self).disabled or
            all('disabled' in each.attrs for each in self._parsed.find_all('option'))
        )

    def _get_options(self, parsed):
        options, labels, initial = [], [], []
        for option in parsed.find_all('option'):
            value = option.get('value', option.text)
            selected = option.get('selected')
            options.append(value)
            labels.append(option.text)
            if selected is not None:
                initial.append(value)
        return options, labels, initial


class Textarea(Input):

    def __init__(self, parsed):
        super(Textarea, self).__init__(parsed)
        self.value = self._parsed.text.rstrip('\r').rstrip('\n')


class Checkbox(FlatOptionField, MultiValueField):
    pass


class Radio(FlatOptionField, MultiOptionField):
    pass


class Select(NestedOptionField, MultiOptionField):

    def _set_initial(self, initial):
        """If no option is selected initially, select the first option.
        """
        super(Select, self)._set_initial(initial)
        if not self._value and self.options:
            self.value = self.options[0]


class MultiSelect(NestedOptionField, MultiValueField):
    pass
