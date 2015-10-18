from django import template

register = template.Library()


@register.assignment_tag
def pagination(plist, num):
    current, count = plist.number, plist.paginator.num_pages
    result = {}
    if current >= num + 2:
        result['left_end'] = 1
    if current > num + 2:
        result['left_ellipsis'] = True
    result['left_items'] = list(range(max(1, current - num), current))
    result['right_items'] = list(range(current + 1, min(count, current + num) + 1))
    if current < count - 2:
        result['right_ellipsis'] = True
    if current <= count - 2:
        result['right_end'] = count
    return result
