.. :changelog:

History
-------

0.5.2
++++++++++++++++++
* Remove requirements parsing from `setup.py`.
* Don't pin to exact requirements versions. Thanks StuntsPT!
* Don't install tests along with package. Thanks voyageur!
* Handle empty select fields. Thanks pratyushmittal!
* Parse partial document correctly when lxml is installed. Thanks again pratyushmittal!
* Lint code with flake8.

0.5.0
++++++++++++++++++
* Add optional `session` argument to `RoboBrowser::__init__`
* Add optional `timeout` and `allow_redirects` options to `RoboBrowser::__init__`
* Allow `RoboBrowser::open`, `RoboBrowser::follow_link`, and `RoboBrowser::submit_form` to accept optional keyword arguments to requests (`timeout`, `verify`, etc.)
* *Backwards-incompatible*: Remove `auth`, `headers`,  and `verify` arguments `from RoboBrowser::__init__`; session configuration should instead be passed in `session`
* *Backwards-incompatible*: Restrict `RoboBrowser::follow_link` to `link` argument; text strings and BeautifulSoup arguments no longer accepted

0.4.1
++++++++++++++++++
* Handle multi-option fields without "value" attributes

0.4.0
++++++++++++++++++
* Fix modeling of form fields to handle non-unique field names.
* Allow selection of submit button if multiple submits are present.

0.1.0
++++++++++++++++++

* First release on PyPI.
