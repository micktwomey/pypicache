from setuptools import setup

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
    },
    install_requires=[
        'certifi==0.0.8',
        'chardet==2.1.1',
        'distribute==0.6.34',
        'Flask==0.9',
        'Jinja2==2.6',
        'requests==1.1.0',
        'Werkzeug==0.8.3',
    ]
    
)
