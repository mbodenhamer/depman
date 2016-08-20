import re
from setuptools import setup, find_packages

def read(fpath):
    with open(fpath, 'r') as f:
        return f.read()

def requirements(fpath):
    return list(filter(bool, read(fpath).split('\n')))

def metadata(fpath, meta):
    txt = read(fpath)
    m = re.search("(?m)^{}:\s+['\"]?(.+?)['\"]?$".format(meta), txt)
    if m:
        return m.groups()[0]
    raise RuntimeError('Cannot find value for {}'.format(meta))

def version(fpath):
    return metadata(fpath, 'version')

setup(
    name = 'depman',
    version = version('depman/metadata.yml'),
    author = 'Matt Bodenhamer',
    author_email = 'mbodenhamer@mbodenhamer.com',
    description = 'A lightweight dependency manager',
    long_description = read('README.rst'),
    url = 'https://github.com/mbodenhamer/depman',
    packages = find_packages(),
    include_package_data = True,
    install_requires = requirements('requirements.in'),
    entry_points = {
        'console_scripts': [
            'depman = depman.main:main',
        ]
    },
    license = 'MIT',
    keywords = ['dependencies', 'dependency management'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities'
    ]
)
