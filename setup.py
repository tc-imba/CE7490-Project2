from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

setup(
    setup_requires=['pbr'],
    ext_modules=cythonize(['raid6/cpp/pyrscode.pyx']),
    pbr=True,
)
