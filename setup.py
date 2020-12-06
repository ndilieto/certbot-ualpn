import sys
from distutils.version import StrictVersion
from setuptools import __version__ as setuptools_version
from setuptools import find_packages
from setuptools import setup

version = '0.2.dev0'

install_requires=[
    'acme>=1.7.0',
    'certbot>=1.7.0',
    'setuptools',
    'zope.interface',
]

setuptools_known_environment_markers = (StrictVersion(setuptools_version) >= StrictVersion('36.2'))
if setuptools_known_environment_markers:
    install_requires.append('mock ; python_version < "3.3"')
elif sys.version_info < (3,3):
    install_requires.append('mock')

setup(
    name='ualpn',
    version=version,
    description="ualpn TLS-ALPN-01 Authenticator plugin for Certbot",
    url='https://github.com/ndilieto/certbot-ualpn',
    author="Nicola Di Lieto",
    author_email='nicola.dilieto@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'certbot.plugins': [
            'ualpn = ualpn.ualpn:Authenticator',
        ],
    },
)
