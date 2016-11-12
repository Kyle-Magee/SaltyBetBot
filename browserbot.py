from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from betbot import prediction
import time
import config


class Browser:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get('http://www.saltybet.com/authenticate?signin=1')

    def login(self):
        username = self.driver.find_element_by_id('email')
        password = self.driver.find_element_by_id('pword')
        username.send_keys(config.username)
        password.send_keys(config.password)
        password.send_keys(Keys.RETURN)

    def vote(self):
        red = self.driver.find_element_by_id('player1')
        blue = self.driver.find_element_by_id('player2')
        red_name = red.text
        blue_name = blue.text
        predicted_winner, confidence = prediction(red_name, blue_name)
        if predicted_winner:
            wager = self.driver.find_element_by_id('wager')
            wager.send_keys(confidence * 10)
            if predicted_winner == red_name:
                red.click()
            else:
                blue.click()

    def wait(self):
        status = self.driver.find_element_by_id('betstatus')
        while 'OPEN' not in status.text:
            time.sleep(1)

    def wait_until_next(self):
        status = self.driver.find_element_by_id('betstatus')
        while 'locked' not in status.text:
            time.sleep(1)

if __name__ == '__main__':
    x = Browser()
    x.login()
    while True:
        x.wait()
        x.vote()
        x.wait_until_next()
