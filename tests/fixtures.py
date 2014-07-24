from robobrowser import responses

from tests import utils

mock_links = utils.mock_responses(
    [
        utils.ArgCatcher(
            responses.GET, 'http://robobrowser.com/links/',
            body=b'''
                <a href="/link1/">sheer heart attack</a>
                <a href="/link2/" class="song">night at the opera</a>
                <a class="nohref">no href</a>
            '''
        ),
        utils.ArgCatcher(responses.GET, 'http://robobrowser.com/link1/'),
        utils.ArgCatcher(responses.GET, 'http://robobrowser.com/link2/'),
    ]
)

mock_forms = utils.mock_responses(
    [
        utils.ArgCatcher(
            responses.GET, 'http://robobrowser.com/get_form/',
            body=b'''
                <form id="bass" method="get" action="/get_form/">'
                    <input name="deacon" value="john" />
                </form>
                <form id="drums" method="post" action="/get_form/">'
                    <input name="deacon" value="john" />
                </form>
            '''
        ),
        utils.ArgCatcher(
            responses.GET, 'http://robobrowser.com/multi_submit_form/',
            body=b'''
                <form id="bass" method="get" action="/multi_submit_form/">'
                    <input name="deacon" value="john" />
                    <input type="submit" name="submit1" value="value1" />
                    <input type="submit" name="submit2" value="value2" />
                </form>
            '''
        ),
        utils.ArgCatcher(
            responses.GET, 'http://robobrowser.com/post_form/',
            body=b'''
                <form id="bass" method="post" action="/submit/">'
                    <input name="deacon" value="john" />
                </form>
                <form id="drums" method="post" action="/submit/">'
                    <input name="deacon" value="john" />
                </form>
            '''
        ),
        utils.ArgCatcher(
            responses.GET, 'http://robobrowser.com/noname/',
            body=b'''
                <form name="input" action="action" method="get">
                <input type="checkbox" name="vehicle" value="Bike">
                    I have a bike<br>
                <input type="checkbox" name="vehicle" value="Car">I have a car
                <br><br>
                <input type="submit" value="Submit">
                </form>
            '''
        ),
        utils.ArgCatcher(
            responses.POST, 'http://robobrowser.com/submit/',
        ),
    ]
)

mock_urls = utils.mock_responses(
    [
        utils.ArgCatcher(responses.GET, 'http://robobrowser.com/page1/'),
        utils.ArgCatcher(responses.GET, 'http://robobrowser.com/page2/'),
        utils.ArgCatcher(responses.GET, 'http://robobrowser.com/page3/'),
        utils.ArgCatcher(responses.GET, 'http://robobrowser.com/page4/'),
    ]
)
