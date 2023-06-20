#!/usr/bin/env python3
import subprocess

from setuptools import setup  # type: ignore
from setuptools.command.build_py import build_py  # type: ignore
from setuptools.command.develop import develop  # type: ignore
import os
import urllib
import shutil


MA_BFWS_dst = "./ma_bfws/MA_BFWS"
MA_BFWS_PUBLIC = "ma_bfws"
# COMPILE_CMD = './compile'
MA_BFWS_TAG = "master"
MA_BFWS_REPO = "https://.../MA_BFWS"

long_description = """============================================================
    UP_MA_BFWS
 ============================================================
"""
isExist = os.path.exists("up_ma_bfws")
if not isExist:
    os.system("mkdir up_ma_bfws")


def install_MA_BFWS():
    subprocess.run(["git", "clone", "-b", MA_BFWS_TAG, MA_BFWS_REPO])
    shutil.move(MA_BFWS_PUBLIC, MA_BFWS_dst)
    curr_dir = os.getcwd()
    os.chdir(MA_BFWS_dst)
    # subprocess.run(COMPILE_CMD)
    os.system("rm -r out 2> /dev/null")
    os.system("rm -r ma_bfws-dist 2> /dev/null")
    os.system("mkdir ma_bfws-dist")
    #Examples:
    # os.system('cp -r libs/ enhsp-dist/')
    # os.system("cp FMAP.jar fmap-dist/")
    # Add MA_BFWS
    os.chdir(curr_dir)


class InstallMA_BFWS(build_py):
    """Custom install command."""

    def run(self):
        install_MA_BFWS()
        build_py.run(self)


class InstallMA_BFWSdevelop(develop):
    """Custom install command."""

    def run(self):
        install_MA_BFWS()
        develop.run(self)


setup(
    name="up_ma_bfws",
    version="0.0.1",
    description="up_ma_bfws",
    author="Alfonso E. Gerevini, Nir Lipovetzky, Francesco Percassi, Alessandro Saetti and Ivan Serina",
    author_email="ivan.serina@unibs.it",
    packages=["up_ma_bfws"],
    package_data={"": ["MA_BFWS/..."]},
    cmdclass={"build_py": InstallMA_BFWS, "develop": InstallMA_BFWSdevelop},
    license="APACHE",
)
