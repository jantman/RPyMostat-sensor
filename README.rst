RPyMostat-sensor
========================

.. image:: http://www.repostatus.org/badges/latest/abandoned.svg
   :alt: Project Status: Abandoned – Initial development has started, but there has not yet been a stable, usable release; the project has been abandoned and the author(s) do not intend on continuing development.
   :target: http://www.repostatus.org/#abandoned

**This Project is Abandoned.** I started work on it and decided not to continue. I doubt I ever will, but I'm leaving the code up nonetheless.

This package/repo implements the Python sensor component of `RPyMostat <http://github.com/jantman/RPyMostat>`_. It
discovers and reads local temperature sensors, and POSTs that information to the
RPyMostat Engine API.

Requirements
------------

* Python 2.7+ (currently tested with 2.7, 3.2, 3.3, 3.4)
* Python `VirtualEnv <http://www.virtualenv.org/>`_ and ``pip`` (recommended installation method; your OS/distribution should have packages for these)

Documentation
-------------

See the online documentation at: `http://rpymostat-sensor.readthedocs.org/ <http://rpymostat-sensor.readthedocs.org/>`_

Installation
------------

It's recommended that you install into a virtual environment (virtualenv /
venv). See the `virtualenv usage documentation <http://www.virtualenv.org/en/latest/>`_
for information on how to create a venv. If you really want to install
system-wide, you can (using sudo).

.. code-block:: bash

    pip install rpymostat-sensor

Configuration
-------------

Something here.

Usage
-----

Something else here.

Bugs and Feature Requests
-------------------------

Bug reports and feature requests are happily accepted via the `GitHub Issue Tracker <https://github.com/jantman/RPyMostat-sensor/issues>`_. Pull requests are
welcome. Issues that don't have an accompanying pull request will be worked on
as my time and priority allows.

License
-------

RPyMostat is licensed under the `GNU Affero General Public License, version 3 or later <http://www.gnu.org/licenses/agpl.html>`_.
