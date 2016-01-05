import sys

from .base import *  # NOQA


if 'DYNO' in os.environ:
    from .heroku import *  # NOQA
else:
    try:
        from .local import *  # NOQA
    except ImportError, exc:
        exc.args = tuple(['%s (did you rename settings/local.py-dist?)' % exc.args[0]])
        raise exc

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    from .test import *  # NOQA
