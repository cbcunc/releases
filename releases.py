#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inspect all the release strings in PyPI.

See how many are not even minimally PEP-386 compliant.
"""

import xmlrpclib
import cPickle
import re

pypi = 'http://pypi.python.org/pypi'
mapping = 'releases.dict'
pattern = re.compile(r'^\d')
antipattern = re.compile(r'-\d')


def build_map(echo=False):
    client = xmlrpclib.ServerProxy(pypi)
    packages = client.list_packages()
    releases = {}
    for package in packages:
        releases[package] = client.package_releases(package)
        if echo:
            print package, releases[package]
    with open(mapping, 'w') as handle:
        cPickle.dump(releases, handle)
    return releases


def police_map(releases, echo=False):
    compliant = {}
    noncompliant = {}
    ambiguous = []
    for package, versions in releases.items():
        for version in versions:
            match = re.search(pattern, version)
            if match:
                compliant.setdefault(package, []).append(version)
            else:
                noncompliant.setdefault(package, []).append(version)
                if echo:
                    print "Noncompliant package: {} Version string: {}". \
                          format(package, version)
    for package in releases:
        match = re.search(antipattern, package)
        if match:
            ambiguous.append(package)
            if echo:
                print "Ambiguous package name: {}".format(package)
    return (compliant, noncompliant, ambiguous)

if __name__ == '__main__':
    try:
        with open(mapping) as handle:
            releases = cPickle.load(handle)
    except:
        releases = build_map(True)
    compliant, noncompliant, ambiguous = police_map(releases, True)
    print "Packages: {}".format(len(releases))
    print "Compliant: {}".format(len(compliant))
    print "Noncompliant: {}".format(len(noncompliant))
    print "Ambiguous: {}".format(len(ambiguous))
