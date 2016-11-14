from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from betbot import prediction
from models import engine, Fighter, Fight
from sqlalchemy.orm import sessionmaker
import random
import time
import config

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


class Browser:

    def __init__(self):
        display = Display(visible=0, size=(1200,800))
        display.start()
        self.driver = webdriver.Chrome()
        self.driver.get('http://www.saltybet.com/authenticate?signin=1')

    def login(self):
        username = self.driver.find_element_by_id('email')
        password = self.driver.find_element_by_id('pword')
        username.send_keys(config.username)
        password.send_keys(config.password)
        password.send_keys(Keys.RETURN)
        time.sleep(15)

    def vote(self):
        red = self.driver.find_element_by_id('player1')
        blue = self.driver.find_element_by_id('player2')
        red_name = red.text
        blue_name = blue.text
        predicted_winner, confidence = prediction(red_name, blue_name)
        wager = self.driver.find_element_by_id('wager')
        if predicted_winner:
            random_val = False
            wager.send_keys(confidence * 10)
            if predicted_winner == red_name:
                red.click()
                voted = red_name
                against = blue_name
            else:
                blue.click()
                voted = blue_name
                against = red_name
        else:
            random_val = True
            wager.send_keys(10)
            bet = random.choice(['red', 'blue'])
            if bet == 'red':
                red.click()
                voted = red_name
                against = blue_name
            else:
                blue.click()
                voted = red_name
                against = blue_name

        with open('fightlog.txt', 'a') as text:
                text.write('Voting for {} against {}. Random: {}\n'.format(voted, against, random_val))

    def wait(self):
        status = self.driver.find_element_by_id('betstatus')
        while 'OPEN' not in status.text:
            time.sleep(1)

    def wait_until_next(self):
        status = self.driver.find_element_by_id('betstatus')
        while 'locked' not in status.text:
            time.sleep(1)

    def get_crowd_stats(self):
        """Scrapes site to find who the crowd favorite of the voters are"""
        red_team = self.driver.find_element_by_class_name('redtext').text.split('|')
        blue_team = self.driver.find_element_by_class_name('bluetext').text.split('|')
        total_votes = int(red_team[0]) + int(blue_team[1])
        time_start = time.time()
        outcome = 'random string'
        while 'wins' not in outcome:
            outcome = self.driver.find_element_by_id('betstatus').text
        time_elapsed = time.time() - time_start
        winner = outcome.split()[-1][:-1]
        self.record_data(name=red_team[1], win=winner == 'Red', time_elapsed=time_elapsed,
                         votes=float(red_team[0]) / total_votes * 100)
        self.record_data(name=blue_team[0], win=winner == 'Blue', time_elapsed=time_elapsed,
                         votes=float(blue_team[1]) / total_votes * 100)
        self.record_fight_outcome(red_team[1].strip(), blue_team[0].strip(), winner)

    def record_fight_outcome(self, red_team, blue_team, winner):
        if 'Red' == winner:
            winner = red_team
        else:
            winner = blue_team
        fight = Fight(fighter_one=red_team, fighter_two=blue_team, winner=winner)
        session.add(fight)
        session.commit()

    def record_data(self, name, win, time_elapsed, votes):
        """Writes data to database session"""
        name = name.strip()
        fighter = session.query(Fighter).filter_by(name=name).first()
        if fighter:
            if win:
                fighter.wins += 1
                fighter.average_win_time += time_elapsed
                fighter.average_win_time /= 2
            else:
                fighter.losses += 1
                fighter.average_loss_time += time_elapsed
                fighter.average_win_time /= 2

            fighter.average_percent_of_votes += votes
            fighter.average_percent_of_votes /= 2
        else:
            if win:
                fighter = Fighter(name=name, average_percent_of_votes=votes, wins=1, average_win_time=time_elapsed)
            else:
                fighter = Fighter(name=name, average_percent_of_votes=votes, losses=1, average_loss_time=time_elapsed)

        session.add(fighter)
        session.commit()

if __name__ == '__main__':
    x = Browser()
    x.login()
    while True:
         x.wait()
         x.vote()
         x.wait_until_next()
         x.get_crowd_stats()
