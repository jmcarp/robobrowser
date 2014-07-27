"""
HTML form fields.
"""

import abc
import six

from robobrowser.compat import string_types
from robobrowser import helpers
from robobrowser import exceptions


class ValueMeta(type):
    """Metaclass that creates a value property on class creation. Classes
    with this metaclass should define _get_value and optionally _set_value
    methods.

    """
    def __init__(cls, name, bases, dct):
        cls.value = property(
            getattr(cls, '_get_value'),
            getattr(cls, '_set_value', None),
        )
        super(ValueMeta, cls).__init__(name, bases, dct)


class FieldMeta(ValueMeta, abc.ABCMeta):
    """Multiply inherit from ValueMeta and ABCMeta; classes with this metaclass
    are automatically assigned a value property and can use methods from
    ABCMeta (e.g. abstractmethod).

    """
    pass


@six.add_metaclass(FieldMeta)
class BaseField(object):
    """Abstract base class for form fields.

    :param parsed: String or BeautifulSoup tag

    """
    def __init__(self, parsed):
        self._parsed = helpers.ensure_soup(parsed)
        self._value = None
        self.name = self._get_name(self._parsed)

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

    # Property methods
    def _get_value(self):
        return self._value if self._value else ''

    def _set_value(self, value):
        self._value = value


class Input(BaseField):

    def __init__(self, parsed):
        super(Input, self).__init__(parsed)
        self.value = self._parsed.get('value')


class Submit(Input):
    pass


class FileInput(BaseField):

    def _set_value(self, value):
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

    @abc.abstractproperty
    def default_value(self):
        """When the "value" attribute is not defined for a multi-option form
        field, some default must be used instead.

        """
        return None

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
            index = self.labels.index(value)
            if index not in self.labels[index:]:
                return index
        raise ValueError

    # Property methods
    def _get_value(self):
        if self._value is None:
            return ''
        return self.options[self._value]

    def _set_value(self, value):
        self._value = self._value_to_index(value)


class MultiValueField(MultiOptionField):

    def _set_initial(self, initial):
        self.value = initial

    # Property methods
    def _get_value(self):
        return [
            self.options[idx]
            for idx in self._value
        ]

    def _set_value(self, value):
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
            raise ValueError
        self._value.append(index)
        self._value.sort()

    def remove(self, value):
        index = self._value_to_index(value)
        self._value.remove(index)


class FlatOptionField(MultiOptionField):

    def _get_name(self, parsed):
        name = parsed[0].get('name')
        if name is not None:
            return name
        raise exceptions.InvalidNameError

    def _get_options(self, parsed):
        options, labels, initial = [], [], []
        for option in parsed:
            value = option.get('value', self.default_value)
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

    def _get_options(self, parsed):
        options, labels, initial = [], [], []
        for option in parsed.find_all('option'):
            value = option.get('value', self.default_value)
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

    @property
    def default_value(self):
        return 'on'


class Radio(FlatOptionField, MultiOptionField):

    @property
    def default_value(self):
        return 'on'


class Select(NestedOptionField, MultiOptionField):

    @property
    def default_value(self):
        return 'sel'

    def _set_initial(self, initial):
        """If no option is selected initially, select the first option.

        """
        super(Select, self)._set_initial(initial)
        if not self._value:
            self.value = self.options[0]


class MultiSelect(NestedOptionField, MultiValueField):

    @property
    def default_value(self):
        return 'sel'
