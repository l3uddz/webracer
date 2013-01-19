owebunit - a comprehensive web application testing library for Python
=====================================================================

owebunit is intended for applications that are written without a framework,
using a framework that does not provide a testing module or where the
provided testing module is lacking in functionality.

owebunit is a general-purpose library not tied to any specific framework.
Its goals are:

- Testing complete target application stack via HTTP
- Faster testing of WSGI-compliant target applications via WSGI
- Support for multiple concurrent sessions
- Easy to use API
- Complete documentation
- Possibly twill-like form handling in the future

Note: API is not yet stable.

Tests
-----

Execute the test suite by running ``nosetests``.

The test suite uses some nose features and will not work with unittest alone.

.. image:: https://api.travis-ci.org/p/owebunit.png
  :target: https://travis-ci.org/p/owebunit

License
-------

Released under the 2 clause BSD license.
