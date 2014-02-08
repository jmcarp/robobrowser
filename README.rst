PyRobot: Your friendly neighborhood web scraper
===============================================

.. image:: https://badge.fury.io/py/pyrobot.png
    :target: http://badge.fury.io/py/pyrobot
    
.. image:: https://travis-ci.org/jmcarp/pyrobot.png?branch=master
        :target: https://travis-ci.org/jmcarp/pyrobot

.. image:: https://coveralls.io/repos/jmcarp/pyrobot/badge.png?branch=master
        :target: https://coveralls.io/r/jmcarp/pyrobot

Homepage: `http://pyrobot.readthedocs.org/ <http://pyrobot.readthedocs.org/>`_

.. code-block:: python
    
    import re
    from pyrobot import RoboBrowser
    
    # Browse to Rap Genius
    browser = RoboBrowser(history=True)
    browser.open('http://rapgenius.com/')
    
    # Search for Queen
    form = browser.get_form(action=re.compile(r'search'))
    form['q'].value = 'queen'
    browser.submit_form(form)

    # Look up the first song
    songs = browser.select('.song_name')
    browser.follow_link(songs[0])
    lyrics = browser.find(class_=re.compile(r'\blyrics\b'))
    lyrics.text     # \n[Intro]\nIs this the real life...
    
    # Back to results page
    browser.back()

    # Look up my favorite song
    browser.follow_link('death on two legs')
    lyrics = browser.find(class_=re.compile(r'\blyrics\b'))
    lyrics.text     # \n[Verse 1]\nYou suck my blood like a leech...

PyRobot combines the best of two excellent Python libraries: 
`Requests <http://docs.python-requests.org/en/latest/>`_ and 
`BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/>`_. 
PyRobot represents browser sessions using Requests and HTML responses 
using BeautifulSoup, transparently exposing methods of both libraries:

.. code-block:: python

    import re
    from pyrobot import RoboBrowser

    browser = RoboBrowser(user_agent='a python robot')
    browser.open('https://github.com/')

    # Inspect the browser session
    browser.session.cookies['_gh_sess']         # BAh7Bzo...
    browser.session.headers['User-Agent']       # a python robot

    # Searched the parsed HTML
    browser.select('div.teaser-icon')       # [<div class="teaser-icon">
                                            # <span class="mega-octicon octicon-checklist"></span>
                                            # </div>,
                                            # ...
    browser.find(class_=re.compile(r'column', re.I))    # <div class="one-third column">
                                                        # <div class="teaser-icon">
                                                        # <span class="mega-octicon octicon-checklist"></span>
                                                        # ...

PyRobot also includes tools for working with forms, inspired by
`WebTest <https://github.com/Pylons/webtest>`_ and `Mechanize <http://wwwsearch.sourceforge.net/mechanize/>`_.

.. code-block:: python
    
    from pyrobot import Browser
    browser = RoboBrowser()

    # Get the signup form
    signup_form = browser.get_form(class_='signup')
    signup_form                     # <RoboForm user[name]=, user[email]=, ...

    # Inspect its values
    signup_form['authenticity_token'].value     # 6d03597 ...

    # Fill it out
    signup_form['user[name]'] = 'python-robot'
    signup_form['user[user_password]'] = 'secret'

    # Serialize it to JSON
    signup_form.serialize()         # {'data': {'authenticity_token': '6d03597...',
                                    #  'context': '',
                                    #  'user[email]': '',
                                    #  'user[name]': 'python-robot',
                                    #  'user[user_password]': ''}}   

    # And submit
    browser.submit_form(signup_form)

