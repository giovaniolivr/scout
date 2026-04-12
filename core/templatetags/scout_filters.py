from django import template

register = template.Library()


@register.filter
def format_cnpj(value):
    """
    Formats a 14-digit CNPJ string as XX.XXX.XXX/XXXX-XX.
    Returns the value unchanged if it doesn't have exactly 14 digits.
    """
    digits = ''.join(filter(str.isdigit, str(value or '')))
    if len(digits) != 14:
        return value
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


@register.filter
def format_cpf(value):
    """
    Formats an 11-digit CPF string as XXX.XXX.XXX-XX.
    Returns the value unchanged if it doesn't have exactly 11 digits.
    """
    digits = ''.join(filter(str.isdigit, str(value or '')))
    if len(digits) != 11:
        return value
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
