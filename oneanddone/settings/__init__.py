from .base import *

if 'STACKATO_APP_NAME' in os.environ:
    from .stackato import *
else:
    try:
        from .local import *
    except ImportError, exc:
        exc.args = tuple(['%s (did you rename settings/local.py-dist?)' % exc.args[0]])
        raise exc
