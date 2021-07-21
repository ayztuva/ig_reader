from selenium import webdriver


options = webdriver.FirefoxOptions()
options = webdriver.
# options.add_argument('--headless')
driver = webdriver.Firefox(options=options)


class Viewer:
    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password
        self.requests = 0

    def login(self):
        self.driver.get('https://www.instagram.com/accounts/login/')
        self.driver.find_element_by_xpath(
            '//input[@name="username"]').send_keys(self.username)
        self.driver.find_element_by_xpath(
            '//input[@name="password"]').send_keys(self.password)
