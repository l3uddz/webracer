WebRacer - a web crawler and web application testing library in Python
======================================================================

WebRacer started as a high level web application testing library, similar
to twill but with a more comprehensive API. With time the client portion
became sufficiently useful standalone.

Agent module
--------------

The agent module provides a browser level HTTP client. Besides the standard
request/response functionality the agent module notably offers an easy
to use form API.

Test case module
----------------

WebRacer provides a test case class that offers more convenient integration
of the rest of WebRacer into unittest-based test suites.

Both intuitive to use and exhaustive
------------------------------------

The goal of WebRacer is to expose HTTP and web-related functions in
a manner that makes code for common tasks intuitive and concise, but
does not compromise completeness. Phrased differently, WebRacer is meant
to be suitable for all use cases involving driving or testing web applications
rather than a certain predetermined subset of them.

WebRacer does not require the use of a framework. In fact, assertions that
it provides are defined on the session class and may be used in web crawlers
that do not employ unittest at all.

Documented and tested
---------------------

WebRacer aims to eventually have 100% documentation and test coverage.

Scope
-----

Currently WebRacer tests HTTP applications via actual HTTP.

Support for testing WSGI applications without running an HTTP server
is planned.

The application being tested may be launched in another thread in
the test process or may be external to the test/driver process.

Features
--------

- Multiple concurrent test sessions
- Response assertions
- Comprehensive form handling

Note: API is not yet stable.

Examples
--------

The largest application using WebRacer at this time is Wolis_.

Tests
-----

Execute the test suite by running ``nosetests``.

The test suite uses some nose features and will not work with unittest alone.

.. image:: https://api.travis-ci.org/p/webracer.png
  :target: https://travis-ci.org/p/webracer

License
-------

Released under the 2 clause BSD license.

.. _Wolis: https://github.com/p/wolis
