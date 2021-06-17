from django.template import Library


register = Library()

def length_gt(value, arg):
    return len(value) > int(arg)
    
register.filter('length_gt', length_gt)