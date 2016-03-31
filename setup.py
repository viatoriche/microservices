import os
from setuptools import find_packages, setup

package = 'microservices'

version = __import__(package).get_version()
packages = find_packages()

def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}

setup(
    name=package,
    version=version,
    url='',
    packages=packages,
    package_data=get_package_data(package),
    license='',
    author='viatoriche',
    author_email='maxim@via-net.org',
    description='',
    install_requires=[x for x in open('requirements.txt').read().split('\n')],
)
