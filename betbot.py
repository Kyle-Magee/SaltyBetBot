from models import Fight, Fighter, engine
from sqlalchemy.orm import sessionmaker
import numpy as np


Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


def get_statistic(statistic, data):
    x = list(engine.execute('select {} from fighters'.format(data)))
    if statistic == 'mean':
        return np.mean(x)
    else:
        return np.std(x)


def prediction(fighter_one, fighter_two):
    fighter_one = session.query(Fighter).filter_by(name=fighter_one).first()
    fighter_two = session.query(Fighter).filter_by(name=fighter_two).first()
    fighter_one_points = 0
    fighter_two_points = 0
    try:
        fighter_one.wins = (fighter_one.wins - get_statistic('mean', 'wins')) / get_statistic('std', 'wins')
        fighter_two.wins = (fighter_two.wins - get_statistic('mean', 'wins')) / get_statistic('std', 'wins')

    except:
        return None, None
    fighter_one.losses = (fighter_one.losses - get_statistic('mean', 'losses')) / get_statistic('std', 'losses')
    fighter_two.losses = (fighter_two.losses - get_statistic('mean', 'losses')) / get_statistic('std', 'losses')

    fighter_one.average_percent_of_votes = ((fighter_one.average_percent_of_votes -
                                             get_statistic('mean', 'average_percent_of_votes')) /
                                            get_statistic('std', 'average_percent_of_votes'))

    fighter_two.average_percent_of_votes = ((fighter_two.average_percent_of_votes -
                                             get_statistic('mean', 'average_percent_of_votes')) /
                                            get_statistic('std', 'average_percent_of_votes'))
    fighter_one.average_win_time = \
        ((fighter_one.average_win_time - get_statistic('mean', 'average_win_time')) /
         get_statistic('std','average_win_time'))
    fighter_two.average_win_time = \
        ((fighter_two.average_win_time - get_statistic('mean', 'average_win_time')) /
         get_statistic('std','average_win_time'))

    fighter_one.average_loss_time = \
        ((fighter_one.average_loss_time - get_statistic('mean', 'average_loss_time')) /
         get_statistic('std','average_loss_time'))
    fighter_two.average_loss_time = \
        ((fighter_two.average_loss_time - get_statistic('mean', 'average_loss_time')) /
         get_statistic('std','average_loss_time'))

    if fighter_one.wins > fighter_two.wins:
        fighter_one_points += 3
    elif fighter_one.wins < fighter_two.wins:
        fighter_two_points += 3

    if fighter_one.losses < fighter_two.losses:
        fighter_one_points += 2
    elif fighter_one.losses > fighter_two.losses:
        fighter_two_points += 2

    if fighter_one.average_win_time > fighter_two.average_win_time:
        fighter_one_points += 2
    elif fighter_one.average_win_time < fighter_two.average_win_time:
        fighter_two_points += 2

    if fighter_one.average_loss_time > fighter_two.average_loss_time:
        fighter_one_points += 2
    elif fighter_one.average_loss_time < fighter_two.average_loss_time:
        fighter_two_points += 2

    if fighter_one.average_percent_of_votes > fighter_two.average_percent_of_votes:
        fighter_one_points += 1
    elif fighter_one.average_percent_of_votes < fighter_two.average_percent_of_votes:
        fighter_two_points += 1

    difference = abs(fighter_one_points - fighter_two_points)
    if fighter_one_points > fighter_two_points:
        return fighter_one.name, difference
    else:
        return fighter_two.name, difference

