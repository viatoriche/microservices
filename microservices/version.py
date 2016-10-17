MAJOR = 0
MINOR = 23
PATCH = 0


def get_version(suffix=''):
    return '.'.join([str(v) for v in (MAJOR, MINOR, PATCH)]) + suffix


if __name__ == '__main__':
    print(get_version())
