import sys

MAJOR = 0
MINOR = 33
PATCH = 0


def get_version(suffix=''):  # pragma: no cover
    return '.'.join([str(v) for v in (MAJOR, MINOR, PATCH)]) + suffix


if __name__ == '__main__':
    sys.stdout.write(get_version())  # pragma: no cover
