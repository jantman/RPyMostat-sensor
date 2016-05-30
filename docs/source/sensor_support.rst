Sensor Support
==============

Built-In Sensor Support
-----------------------

* `one-wire file system (OWFS) <http://owfs.org/>`_ via the :py:class:`~.OWFS`
  class.

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

``rpymostat-sensor`` uses Setuptools entrypoints `setuptools entrypoints <https
://pythonhosted.org/setuptools/setuptools.html#extensible-applications-and-
frameworks>`_ for dynamic discovery of sensor classes. While it's preferred that
new sensors be merged into this repository, it's possible to implement them as
standalone packages as long as they have the required entrypoints.
