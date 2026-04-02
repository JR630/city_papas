from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Obtiene un valor de un diccionario usando una clave.
    Uso en template: {{ dict|get_item:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []
