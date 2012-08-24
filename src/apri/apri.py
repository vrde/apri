"""Apri is a single file module that helps you managing your static assets.

Apri provides a smart alternative to the buildin `open` function and has some
pretty interesting properties :)

Some use cases follow.

"""


import sys
import os
from zipfile import ZipFile
import logging

log = logging.getLogger(__name__)

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


def apri(filename, *args, **kwargs):

    module = kwargs.pop('module', None)

    if module:
        try:
            loader = module.__loader__
            name = module.__name__

            filelike = StringIO(loader.get_data(os.path.join(name, filename)))
            log.debug(u'Loading from module loader '
                       '{0}/{1}'.format(name, filename))
            return filelike

        except AttributeError:
            base = module.__file__

    else:
        base = __file__
        if not os.path.isfile(base):
            zipreader = ZipFile(os.path.dirname(base))
            filelike = StringIO(zipreader.read(filename))

            log.debug(u'Loading from zipfile '
                       '{0}/{1}'.format(os.path.dirname(base), filename))

            return filelike

    basedir = os.path.realpath(os.path.dirname(base))

    filelike = open(os.path.join(basedir, filename), *args, **kwargs)
    log.debug(u'Loading from filesystem '
                '{0}/{1}'.format(basedir, filename))

    return filelike


def stat(filename, module=None):
    if module:
        try:
            loader = module.__loader__
            return os.stat(loader.archive)
        except AttributeError:
            base = module.__file__

    else:
        base = __file__
        if not os.path.isfile(base):
            return os.stat(os.path.dirname(base))

    basedir = os.path.realpath(os.path.dirname(base))
    return os.stat(os.path.join(basedir, filename))


if __name__ == '__main__':
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.setLevel(logging.DEBUG)

    what = sys.argv[1]

    try:
        module_name = sys.argv[2]
        module = __import__(module_name, globals(), locals(), [], -1)
    except IndexError:
        module = None

    print stat(what, module=module)
    print apri(what, module=module).read()

