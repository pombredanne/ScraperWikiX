from django.contrib.auth.models import User
from lettuce import step,before,world,after
from nose.tools import assert_equals

prefix = 'http://localhost:8000'

@step(u'(?:When|And) I choose to write my scraper in "([^"]*)"')
def when_i_choose_to_write_my_scraper_in(step, language):
    world.browser.find_link_by_href("/scrapers/new/%s" % language.lower()).first.click()
    
@step(u'(?:When|And) I am on the homepage')
def and_i_am_on_the_homepage(step):
    world.browser.visit(prefix + '/')
    
@step(u'Then I should be on the scraper code editing page')
def then_i_should_be_on_the_scraper_code_editing_page(step):
    assert '/scrapers/new/' in world.browser.url

@step(u'And I create a scraper')
def and_i_create_a_scraper(step):
    step.behave_as("""
        And I am on the homepage
        And I click the button "Create a scraper"
        And I choose to write my scraper in "Python"
        Then I should be on the scraper code editing page
    """
    )

@step(u'When I save the scraper as "([^"]*)"')
def when_i_save_the_scraper_as(step, name):
    world.browser.find_by_value("save scraper").first.click()
    # See http://splinter.cobrateam.info/docs/iframes-and-alerts.html
    prompt = world.browser.get_alert()
    prompt.fill_with(name)
    prompt.accept()

@step(u'Then I should be on my "([^"]*)" scraper page')
def then_i_should_be_on_my_scraper_page(step, scraper_name):
    url = '/scrapers/%s/edit/' % scraper_name.lower()
    world.wait_for_url(prefix + url)
    assert url in world.browser.url
                                
