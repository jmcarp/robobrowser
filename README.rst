RoboBrowser: Your friendly neighborhood web scraper
===============================================

.. image:: https://badge.fury.io/py/robobrowser.png
    :target: http://badge.fury.io/py/robobrowser

.. image:: https://travis-ci.org/jmcarp/robobrowser.png?branch=master
        :target: https://travis-ci.org/jmcarp/robobrowser

.. image:: https://coveralls.io/repos/jmcarp/robobrowser/badge.png?branch=master
        :target: https://coveralls.io/r/jmcarp/robobrowser

Homepage: `http://robobrowser.readthedocs.org/ <http://robobrowser.readthedocs.org/>`_

RoboBrowser is a simple, Pythonic library for browsing the web without a standalone web browser. RoboBrowser
can fetch a page, click on links and buttons, and fill out and submit forms. If you need to interact with web services
that don't have APIs, RoboBrowser can help.

.. code-block:: python

    import re
    from robobrowser import RoboBrowser

    # Browse to Genius
    browser = RoboBrowser(history=True)
    browser.open('http://genius.com/')

    # Search for Porcupine Tree
    form = browser.get_form(action='/search')
    form                # <RoboForm q=>
    form['q'].value = 'porcupine tree'
    browser.submit_form(form)

    # Look up the first song
    songs = browser.select('.song_link')
    browser.follow_link(songs[0])
    lyrics = browser.select('.lyrics')
    lyrics[0].text      # \nHear the sound of music ...

    # Back to results page
    browser.back()

    # Look up my favorite song
    song_link = browser.get_link('trains')
    browser.follow_link(song_link)

    # Can also search HTML using regex patterns
    lyrics = browser.find(class_=re.compile(r'\blyrics\b'))
    lyrics.text         # \nTrain set and match spied under the blind...

RoboBrowser combines the best of two excellent Python libraries:
`Requests <http://docs.python-requests.org/en/latest/>`_ and
`BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/>`_.
RoboBrowser represents browser sessions using Requests and HTML responses
using BeautifulSoup, transparently exposing methods of both libraries:

.. code-block:: python

    import re
    from robobrowser import RoboBrowser

    browser = RoboBrowser(user_agent='a python robot')
    browser.open('https://github.com/')

    # Inspect the browser session
    browser.session.cookies['_gh_sess']         # BAh7Bzo...
    browser.session.headers['User-Agent']       # a python robot

    # Search the parsed HTML
    browser.select('div.teaser-icon')       # [<div class="teaser-icon">
                                            # <span class="mega-octicon octicon-checklist"></span>
                                            # </div>,
                                            # ...
    browser.find(class_=re.compile(r'column', re.I))    # <div class="one-third column">
                                                        # <div class="teaser-icon">
                                                        # <span class="mega-octicon octicon-checklist"></span>
                                                        # ...

You can also pass a custom `Session` instance for lower-level configuration:

.. code-block:: python

    from requests import Session
    from robobrowser import RoboBrowser

    session = Session()
    session.verify = False  # Skip SSL verification
    session.proxies = {'http': 'http://custom.proxy.com/'}  # Set default proxies
    browser = RoboBrowser(session=session)

RoboBrowser also includes tools for working with forms, inspired by
`WebTest <https://github.com/Pylons/webtest>`_ and `Mechanize <http://wwwsearch.sourceforge.net/mechanize/>`_.

.. code-block:: python

    from robobrowser import RoboBrowser

    browser = RoboBrowser()
    browser.open('http://twitter.com')

    # Get the signup form
    signup_form = browser.get_form(class_='signup')
    signup_form         # <RoboForm user[name]=, user[email]=, ...

    # Inspect its values
    signup_form['authenticity_token'].value     # 6d03597 ...

    # Fill it out
    signup_form['user[name]'].value = 'python-robot'
    signup_form['user[user_password]'].value = 'secret'

    # Submit the form
    browser.submit_form(signup_form)

Checkboxes:

.. code-block:: python

    from robobrowser import RoboBrowser

    # Browse to a page with checkbox inputs
    browser = RoboBrowser()
    browser.open('http://www.w3schools.com/html/html_forms.asp')

    # Find the form
    form = browser.get_forms()[3]
    form                            # <RoboForm vehicle=[]>
    form['vehicle']                 # <robobrowser.forms.fields.Checkbox...>

    # Checked values can be get and set like lists
    form['vehicle'].options         # [u'Bike', u'Car']
    form['vehicle'].value           # []
    form['vehicle'].value = ['Bike']
    form['vehicle'].value = ['Bike', 'Car']

    # Values can also be set using input labels
    form['vehicle'].labels          # [u'I have a bike', u'I have a car \r\n']
    form['vehicle'].value = ['I have a bike']
    form['vehicle'].value           # [u'Bike']

    # Only values that correspond to checkbox values or labels can be set;
    # this will raise a `ValueError`
    form['vehicle'].value = ['Hot Dogs']

Uploading files:

.. code-block:: python

    from robobrowser import RoboBrowser

    # Browse to a page with an upload form
    browser = RoboBrowser()
    browser.open('http://cgi-lib.berkeley.edu/ex/fup.html')

    # Find the form
    upload_form = browser.get_form()
    upload_form                     # <RoboForm upfile=, note=>

    # Choose a file to upload
    upload_form['upfile']           # <robobrowser.forms.fields.FileInput...>
    upload_form['upfile'].value = open('path/to/file.txt', 'r')

    # Submit
    browser.submit(upload_form)

By default, creating a browser instantiates a new requests `Session`. 

Requirements
------------

- Python >= 2.6 or >= 3.3

License
-------

MIT licensed. See the bundled `LICENSE <https://github.com/jmcarp/robobrowser/blob/master/LICENSE>`_ file for more details.

