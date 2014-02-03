PyRobot: Your friendly neighborhood web scraper
===============================================

.. image:: https://badge.fury.io/py/pyrobot.png
    :target: http://badge.fury.io/py/pyrobot
    
.. image:: https://travis-ci.org/jmcarp/pyrobot.png?branch=master
        :target: https://travis-ci.org/jmcarp/pyrobot

.. image:: https://pypip.in/d/pyrobot/badge.png
        :target: https://crate.io/packages/pyrobot?version=latest

Browse the web from the comfort of your Python terminal.

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
    lyrics.text     # '\n[Intro]\nIs this the real life...
    
    # Back to results page
    browser.back()

    # Look up my favorite song
    browser.follow_link(text=re.compile(r'death on two legs', re.I))
    lyrics = browser.find(class_=re.compile(r'\blyrics\b'))
    lyrics.text     # '\n[Verse 1]\nYou suck my blood like a leech...




