Philosophy
==========

Both low and high level
-----------------------

It should be possible to access any data in its original form.
For example, this means that response headers must be accessible as
a list, to allow an application to handle repeated headers of which
owebunit is unaware.

At the same time it should be easy to consume the data for common tasks.
Continuing the header example, most headers are not duplicated and
therefore it should be possible to access the headers as a dictionary
using case-insensitive header name as the key.
