from selenium import webdriver
import time

def get_login_data():
    browser = webdriver.Firefox(executable_path='/Users/eliogruttadauria/PycharmProjects/volt_scraping/geckodriver')
    browser.get('https://volt.team/sign_in')
    action = webdriver.ActionChains(browser)

    link = browser.find_element_by_xpath('//a[@class="btn btn-lg btn-block btn-social btn-google-plus btn-color"]')
    link.click()

    login_url = str(browser.current_url)

    time.sleep(1)

    emailElem = browser.find_element_by_id('identifierId')
    emailElem.send_keys('XXX')
    nextButton = browser.find_element_by_id('identifierNext')
    nextButton.click()

    time.sleep(1)
    passwordElem = browser.find_element_by_name('password')
    passwordElem.send_keys('XXX')
    signinButton = browser.find_element_by_id('passwordNext')
    signinButton.click()

    time.sleep(1)

    cookie_val = browser.get_cookie('_community_hr_session')['value']

    time.sleep(1)

    browser.quit()

    return login_url, cookie_val



