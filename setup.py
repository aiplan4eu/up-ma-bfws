#!/usr/bin/env python3
import subprocess
import platform
from setuptools import setup, Distribution

long_description = \
"""============================================================
    UP_MA_BFWS
 ============================================================
"""

arch = (platform.system(), platform.machine())

EXECUTABLES = {
    ("Linux", "x86_64"): "maBFWS",
    # ("Windows", "x86_64"): "maBFWS",
    # ("Windows", "AMD64"): "maBFWS",
}

executable = EXECUTABLES[arch]

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False

except ImportError:
    bdist_wheel = None

class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(self):
        return True

    def is_pure(self):
        return False

setup(
    name="up_ma_bfws",
    version="0.0.1",
    description="up_ma_bfws",
    long_description_content_type='text/markdown',
    author="Alfonso E. Gerevini, Nir Lipovetzky, Francesco Percassi, Alessandro Saetti and Ivan Serina",
    author_email="ivan.serina@unibs.it",
    packages=["up_ma_bfws"],
    package_data={"up_ma_bfws": [executable]},
    distclass=BinaryDistribution,
    include_package_data=True,
    cmdclass={'bdist_wheel': bdist_wheel},
    license="APACHE",
)
