from django import template

register = template.Library()

@register.filter(name='split')
def split(str, key):
    cleaned_string = str.replace("[", "").replace("]", "").replace("'","")
    return cleaned_string.split(key)
