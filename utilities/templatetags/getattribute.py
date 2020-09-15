from django import template
from django.conf import settings

register = template.Library()

def getattribute(instance, attr_name):
	if hasattr(instance, attr_name):
		return getattr(instance, attr_name)
	return settings.TEMPLATE_STRING_IF_INVALID

def get_value_from_dict(dictionary,key):
	if key in dictionary.keys():
		return dictionary[key]
	return settings.TEMPLATE_STRING_IF_INVALID

def has_group(user,group_name):
	return user.groups.filter(name=group_name).exists()

register.filter('getattribute',getattribute)
register.filter('get_value_from_dict',get_value_from_dict)
register.filter('has_group',has_group)
