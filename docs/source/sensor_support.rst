.. !!! DO NOT EXIT THIS FILE!!! sensor_support.rst is built during the
   'docs' tox task, from sensor_support.rst.template. Edit THAT File.

Sensor Support
==============

Built-In Sensor Support
-----------------------

* :py:class:`~rpymostat_sensor.sensors.owfs.OWFS` (Dallas Semi 1-Wire Sensors via OneWire FileSystem (OWFS))

Adding Hardware Support
------------------------

Adding hardware support is relatively straightforward:

1. Follow the instructions on installing for development (below).
2. Add a new class under ``sensors/`` that implements :py:class:`.BaseSensor`
   and any other methods you require. See the existing sensor classes as
   examples.
3. Ensure full test coverage for the class.
4. Add a new ``rpymostat.sensors`` entrypoint to ``setup.py`` that points to
   your new class.
5. Open a pull request for your changes.

``rpymostat-sensor`` uses Setuptools entrypoints `setuptools entrypoints
<https://setuptools.readthedocs.io/en/latest/pkg_resources.html#entry-points>`_
for dynamic discovery of sensor classes. While it's preferred that
new sensors be merged into this repository, it's possible to implement them as
standalone packages as long as they have the required entrypoints.
