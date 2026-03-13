"""
Widgets for report form: text input with datalist for autocomplete (breed, color).
"""
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class DatalistInput(forms.TextInput):
    """
    Renders an <input type="text"> with a <datalist> so the browser suggests
    options as the user types. User can still enter any value (free text).
    """
    datalist_id = None
    datalist_options = ()  # list of (value, label) or just values

    def __init__(self, attrs=None, datalist_id=None, datalist_options=None):
        super().__init__(attrs)
        if datalist_id is not None:
            self.datalist_id = datalist_id
        if datalist_options is not None:
            self.datalist_options = datalist_options

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs = {**attrs}
        # Build options: (value, label); skip empty
        options = []
        for item in self.datalist_options:
            if isinstance(item, (list, tuple)):
                opt_value, opt_label = str(item[0]), str(item[1])
            else:
                opt_value = opt_label = str(item)
            if opt_value.strip():
                options.append((opt_value, opt_label))
        datalist_id = (attrs.get('id') or 'id_' + name) + '_list'
        attrs['list'] = datalist_id
        input_html = super().render(name, value, attrs, renderer)
        # Append datalist (browser will suggest as user types)
        opts_html = ''.join(
            format_html('<option value="{}">', v)
            for v, _ in options
        )
        datalist_html = format_html(
            '<datalist id="{}">{}</datalist>',
            datalist_id,
            mark_safe(opts_html)
        )
        return input_html + datalist_html
