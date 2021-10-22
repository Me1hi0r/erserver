from django import template

register = template.Library()

# def times(number):
    # return range(number)

@register.filter(name='range')
def filter_range(start, end):
  return range(start, end+1)
