from setuptools import setup

setup(
    name="pymmpz",
    version="0.0.0",
    packages=["pymmpz"],
    scripts=["scripts/mmpz2xml"],
    install_requires=["midiutil"]
)
