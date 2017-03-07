from six import print_

MAJOR = 0
MINOR = 27
PATCH = 9


def get_version(suffix=''):  # pragma: no cover
    return '.'.join([str(v) for v in (MAJOR, MINOR, PATCH)]) + suffix


if __name__ == '__main__':
    print_(get_version())  # pragma: no cover
