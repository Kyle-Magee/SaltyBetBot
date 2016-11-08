import dryscrape
from bs4 import BeautifulSoup


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
        blue_team = []
        # Wait until votes are tallied
        while len(red_team) < 2:
            red_team = self.soup.find('span', class_='redtext').text.split('|')
            blue_team = self.soup.find('span', class_='bluetext').text.split('|')

        self.red_team, self.blue_team = red_team, blue_team

    def get_winner(self):
        """Waits for winner of fight to be unveiled"""
        outcome = 'random string'
        while 'wins' not in outcome:
            self.soup = BeautifulSoup(self.session.body(), 'lxml')
            outcome = self.soup.find('span', id='betstatus').text
            print(outcome)

        self.winner = outcome.split[-1]

    def record_data(self):
        pass

if __name__ == '__main__':

    x = StatBot()
    x.get_winner()

