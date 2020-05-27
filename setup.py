#!/usr/bin/env python
from __future__ import absolute_import

import os
import sys

if not os.environ.get("SENTRY_PYTHON3") and sys.version_info[:2] != (2, 7):
    sys.exit("Error: Sentry requires Python 2.7.")

from distutils.command.build import build as BuildCommand
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist as SDistCommand
from setuptools.command.develop import develop as DevelopCommand

ROOT = os.path.dirname(os.path.abspath(__file__))

# add sentry to path so we can import sentry.utils.distutils
sys.path.insert(0, os.path.join(ROOT, "src"))


from sentry.utils.distutils import (
    BuildAssetsCommand,
    BuildIntegrationDocsCommand,
    BuildJsSdkRegistryCommand,
)


VERSION = "10.1.0.dev2"
IS_LIGHT_BUILD = os.environ.get("SENTRY_LIGHT_BUILD") == "1"


def get_requirements(env):
    with open(u"requirements-{}.txt".format(env)) as fp:
        return [x.strip() for x in fp.read().split("\n") if not x.startswith("#")]


install_requires = get_requirements("base")
dev_requires = get_requirements("dev")

# override django version in requirements file if DJANGO_VERSION is set
DJANGO_VERSION = os.environ.get("DJANGO_VERSION")
if DJANGO_VERSION:
    install_requires = [
        u"Django{}".format(DJANGO_VERSION) if r.startswith("Django>=") else r
        for r in install_requires
    ]


class SentrySDistCommand(SDistCommand):
    # If we are not a light build we want to also execute build_assets as
    # part of our source build pipeline.
    if not IS_LIGHT_BUILD:
        sub_commands = SDistCommand.sub_commands + [
            ("build_integration_docs", None),
            ("build_assets", None),
            ("build_js_sdk_registry", None),
        ]


class SentryBuildCommand(BuildCommand):
    def run(self):
        from distutils import log as distutils_log

        distutils_log.set_threshold(distutils_log.WARN)

        if not IS_LIGHT_BUILD:
            self.run_command("build_integration_docs")
            self.run_command("build_assets")
            self.run_command("build_js_sdk_registry")
        BuildCommand.run(self)


class SentryDevelopCommand(DevelopCommand):
    def run(self):
        DevelopCommand.run(self)
        if not IS_LIGHT_BUILD:
            self.run_command("build_integration_docs")
            self.run_command("build_assets")
            self.run_command("build_js_sdk_registry")


cmdclass = {
    "sdist": SentrySDistCommand,
    "develop": SentryDevelopCommand,
    "build": SentryBuildCommand,
    "build_assets": BuildAssetsCommand,
    "build_integration_docs": BuildIntegrationDocsCommand,
    "build_js_sdk_registry": BuildJsSdkRegistryCommand,
}


setup(
    name="sentry-plugins-jira",
    version=VERSION,
    author="Sentry",
    author_email="hello@sentry.io",
    url="https://sentry.io",
    description="A realtime logging and aggregation server.",
    long_description=open(os.path.join(ROOT, "README.md")).read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages("src"),
    zip_safe=False,
    install_requires=install_requires,
    extras_require={"dev": dev_requires},
    cmdclass=cmdclass,
    license="BSL-1.1",
    include_package_data=True,
    entry_points={
        "sentry.apps": [
            "jira = sentry_plugins.jira",
        ],
        "sentry.plugins": [
            "jira = sentry_plugins.jira.plugin:JiraPlugin",
        ],
    },
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only",
        "Topic :: Software Development",
        "License :: Other/Proprietary License",
    ],
)
