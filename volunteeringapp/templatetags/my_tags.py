import datetime
from django import template

register = template.Library()

@register.simple_tag
def todays_date():
    return datetime.datetime.now().strftime("%d %b, %Y")


@register.filter
def is_teacher_or_admin(user):
    return user.is_authenticated and user.groups.filter(name__in=['teacher', 'admin']).exists()