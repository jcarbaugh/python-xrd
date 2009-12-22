from distutils.core import setup
from xrd import __version__

long_description = open('README.rst').read()

setup(name="python-xrd",
    version=__version__,
    py_modules=["xrd"],
    description="Package for serializing and deserializing of XRD documents",
    author="Jeremy Carbaugh",
    author_email = "jcarbaugh@gmail.com",
    license='BSD',
    url="http://github.com/jcarbaugh/python-xrd/",
    long_description=long_description,
    platforms=["any"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)