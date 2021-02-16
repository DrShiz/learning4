from django import template


register = template.Library()


@register.filter()
def inc(val, arg):
    return int(val) + int(arg)


@register.simple_tag()
def division(a, b, to_int=False):
    result = int(a) / int(b)
    if to_int:
        return int(result)
    else:
        return result
