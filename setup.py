"""
The latest version of this package is available at:
<http://github.com/jantman/RPyMostat-sensor>

##################################################################################
Copyright 2016 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of RPyMostat-sensor, also known as RPyMostat-sensor.

    RPyMostat-sensor is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RPyMostat-sensor is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with RPyMostat-sensor.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
##################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/RPyMostat-sensor> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
##################################################################################
"""

from setuptools import setup, find_packages
from sys import version_info
from rpymostat_sensor.version import VERSION, PROJECT_URL

entry_points = {
    'rpymostat.sensors': [
        'owfs = rpymostat_sensor.sensors.owfs:OWFS'
    ],
    'console_scripts': [
        'rpymostat-sensor = rpymostat_sensor.runner:console_entry_point'
    ]
}

with open('README.rst') as file:
    long_description = file.read()

requires = [
    'requests',
    'rpymostat-common'
]

classifiers = [
    'Development Status :: 1 - Planning',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
]

setup(
    name='rpymostat-sensor',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=find_packages(),
    url=PROJECT_URL,
    license='AGPLv3+',
    description='The temperature sensor component of RPyMostat.',
    long_description=long_description,
    install_requires=requires,
    keywords="temperature thermometer nest thermostat automation control home",
    classifiers=classifiers,
    entry_points=entry_points
)
