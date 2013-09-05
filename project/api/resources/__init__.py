from tastypie.resources import Resource
import inspect


def get_modules():
    from os import path, listdir
    import sys

    names = set()
    for f in listdir(path.dirname(__file__)):
        if f.startswith('.') or f.startswith('__'):
            continue
        names.add(f.split('.')[0])

    for name in names:
        try:
            module = __import__('%s.%s' % (__name__, name), {}, {}, [''])
        except Exception, e:
            msg = "Error importing test module %s.%s.py: %s"
            msg %= (__name__, name, str(e))
            import traceback
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)
        yield (name, module)


for name, module in get_modules():
    for name, value in module.__dict__.iteritems():
        is_resource = inspect.isclass(value) and issubclass(value, Resource)

        is_base_class = is_resource and value.__name__ == "KlooffModelResource"

        if not is_base_class and is_resource:
            globals()[name] = value
