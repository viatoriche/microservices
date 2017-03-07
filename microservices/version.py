import sys

MAJOR = 0
MINOR = 28
PATCH = 1


def get_version(suffix=''):  # pragma: no cover
    return '.'.join([str(v) for v in (MAJOR, MINOR, PATCH)]) + suffix


if __name__ == '__main__':
    sys.stdout.write(get_version())
