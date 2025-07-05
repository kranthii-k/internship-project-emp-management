from django import template

register = template.Library()

@register.filter
def is_in_role(user, roles):
    roles_list = roles.split(',')  
    return user.role in roles_list
