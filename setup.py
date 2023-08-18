from setuptools import setup
from setuptools import find_packages


def find_packages_without_tests():
    return [package for package in find_packages() if not package.startswith("tests")]


def get_version():
    with open("VERSION") as f:
        return f.read().strip()


def get_long_description():
    with open("README.md") as f:
        return f.read().strip()


setup(
    name="bb_change_broker",
    version=get_version(),
    description="A module to publish changes to buildbot via a message broker",
    author="Fabian Stadler",
    author_email="mail@fabianstadler.com",
    packages=find_packages_without_tests(),
    install_requires=["wheel", "pika"],  # external packages as dependencies
    scripts=["bin/bb_change_broker"],  # executable scripts,
    long_description=get_long_description(),
)
