=======
History
=======

0.5.5 (2017-07-11)
------------------

Changed
~~~~~~~
* Update mypy from 0.511 to 0.520

Fixed
~~~~~
* Ensure we act on selected device in sample client.
* Fix mypy errors.
* Fix message size calculation.
* Add configurable grace period for unregister.


0.5.4 (2017-07-07)
------------------

Fixed
~~~~~
* Fix failure to re-register a light that went off-line.


0.5.3 (2017-07-03)
------------------

Fixed
~~~~~
* Fixed FD resource leak in discovery of existing lights.


0.5.2 (2017-07-02)
------------------

Changed
~~~~~~~
* Significant changes. Improvements to the API. Type hints, doc strings, etc.


0.5.1 (2017-06-26)
------------------

* Initial version after fork from https://github.com/frawau/aiolifx
