from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "lz77_codec", 
        ["lz77_codec.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3", "-march=native", "-ffast-math"],
    ),
]

setup(
    name="lz77_compression",
    ext_modules=cythonize(extensions, annotate=True),
    zip_safe=False,
) 