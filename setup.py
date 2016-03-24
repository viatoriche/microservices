from setuptools import find_packages, setup

version = __import__('microservices').get_version()
packages = find_packages()

setup(
    name='microservices',
    version=version,
    url='',
    packages=packages,
    package_data={'templates': ("templates/*.*")},
    license='',
    author='viatoriche',
    author_email='mpanfilov@npoprogress.com',
    description='',
    install_requires=[x for x in open('requirements.txt').read().split('\n')],
)
