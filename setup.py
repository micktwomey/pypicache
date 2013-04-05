from distutils.core import setup

setup(
    name='pypicache',
    version='0.1',
    description='PyPI caching and proxying server',
    author='Michael Twomey',
    author_email='mick@twomeylee.name',
    url='http://readthedocs.org/projects/pypicache/',
    packages=['pypicache'],
    package_data={
        'pypicache': [
            'static/*/*',
            'templates/*.html',
        ]
    }
)
