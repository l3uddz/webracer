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

Full access
-----------

Applications using owebunit should be able to access all data related to
the data that owebunit provides. For example, if owebunit exposes form
objects it should be possible to access all attributes of respective
form elements.

Any use case
------------

owebunit should support any application within its scope of abstraction
levels.

For example, Symfony's DomCrawler has a selectButton method for selecting
buttons and subsequently forms (forms are identified as parents of
the buttons). The selection is possible by the button's value attribute
only. This is convenient for some applications but creates problems for
internationalized applications (they have to exercise translation
machinery to locate forms) or for crawlers that may encounter multiple
buttons with the same label on a page. owebunit decouples element selection
from element operations and provides a wide range of selection options.

Convenient API
--------------

All functionality exposed by owebunit should be convenient to use. At some
point this is going to require compromises, but generally speaking there
should be no "obscure" functionality. The API should be nice everywhere.

Code using owebunit should be easily readable and understandable. Boilerplate
should be kept to minimum.
