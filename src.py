import dryscrape
import time
from models import engine, Fighter
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


class Browser:

    def __init__(self, site):
        self.session = dryscrape.Session()
        self.session.visit(site)
        self.soup = BeautifulSoup(self.session.body(), 'lxml')


class StatBot(Browser):

    def __init__(self):
        Browser.__init__(self, 'http://www.saltybet.com/')
        self.wins = 0
        self.losses = 0
        self.balance = 0
        self.win_streak = 0
        self.loss_streak = 0

    def get_crowd_stats(self):
        """Scrapes site to find who the crowd favorite of the voters are"""
        red_team = []
        # Wait until votes are tallied
        while len(red_team) < 2:
            red_team = self.soup.find('span', class_='redtext').text.split('|')
            blue_team = self.soup.find('span', class_='bluetext').text.split('|')

        self.time_start = time.time()
        red_team.append('Red')
        blue_team.append('Blue')
        self.red_team, self.blue_team = red_team, blue_team

    def get_winner(self):
        """Waits for winner of fight to be unveiled"""
        outcome = 'random string'
        while 'wins' not in outcome:
            self.soup = BeautifulSoup(self.session.body(), 'lxml')
            outcome = self.soup.find('span', id='betstatus').text

        self.time_end = time.time()
        self.winner = outcome.split()[-1][:-1]

    def record_data(self, name, win, time_elapsed, votes):
        """Writes data to database session"""
        query = session.query(Fighter).filter_by(name=name).first()
        if query:
            fighter = session.query(Fighter).filter_by(name=name).first()
        else:
            fighter = Fighter(name=name)
            session.add(fighter)
            session.commit()
            fighter = session.query(Fighter).filter_by(name=name).first()

        fighter.average_percent_of_votes = int(fighter.average_number_of_votes) + int(votes)
        if win:
            fighter.wins = int(fighter.wins) + 1
            fighter.average_win_time = (int(fighter.average_win_time) + time_elapsed) / 2
        else:
            fighter.losses += 1
            fighter.average_loss_time += (int(fighter.average_loss_time) + time_elapsed) / 2

        session.add(fighter)
        session.commit()

    def run_recording_session(self):

        while True:
            self.get_crowd_stats()
            self.get_winner()
            elapsed_time = self.time_end - self.time_start
            total_votes = self.red_team[0] + self.blue_team[1]
            self.record_data(name=self.red_team[1], win=self.winner == self.red_team[-1],
                             time_elapsed=elapsed_time, votes=self.red_team[0] / total_votes)
            self.record_data(name=self.blue_team[0], win=self.winner == self.blue_team[-1],
                             time_elapsed=elapsed_time, votes=self.blue_team[1] / total_votes)

if __name__ == '__main__':

    x = StatBot()
    x.run_recording_session()

