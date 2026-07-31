from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

MAD_SYMBOLS = {'en': 'MAD', 'fr': 'MAD', 'ar': 'د.م.'}
SEPARATORS = {'en': ',', 'fr': '\u202f', 'ar': ','}

@register.filter
def currency(value, arg=None):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    lang = arg or 'en'
    symbol = MAD_SYMBOLS.get(lang[:2], 'MAD')
    sep = SEPARATORS.get(lang[:2], ',')
    formatted = floatformat(value, 2)
    int_part, _, dec_part = formatted.partition('.')
    if len(int_part) > 3:
        groups = []
        while len(int_part) > 3:
            groups.insert(0, int_part[-3:])
            int_part = int_part[:-3]
        groups.insert(0, int_part)
        int_part = sep.join(groups)
    formatted = f'{int_part}.{dec_part}'
    if lang[:2] == 'ar':
        return f'{formatted}\u00a0{symbol}'
    return f'{formatted}\u00a0{symbol}'

@register.simple_tag(takes_context=True)
def current_currency(context):
    request = context.get('request')
    lang = request.LANGUAGE_CODE if request else 'fr'
    return currency(context['value'], lang)
