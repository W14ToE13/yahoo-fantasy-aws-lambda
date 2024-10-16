import json
# import os
import requests
from urllib.parse import parse_qs
# import logging
# import base64
# import jwt
# import time
# import uuid
# import boto3
# from decimal import Decimal
# import config
import objectpath

import utils
import config
from config import logger

ACCESS_TOKEN = ''

def get_leagues():
    '''
    Return all leagues of current user for the recent season
    '''
    season = utils.getDefaultSeason()
    logger.info('get leagues for season {}'.format(season))

    uri = 'users;use_login=1/games;game_codes=nba;seasons={}/leagues'.format(season)
    resp = get_request(uri)
    t = objectpath.Tree(resp)
    jfilter = t.execute('$..leagues..(league_key, league_id, name, logo_url, scoring_type, start_date, end_date, current_week, start_week, end_week)')

    leagues = []
    for l in jfilter:
        leagues.append(l)

    # sort by league id
    leagues.sort(key = lambda league : int(league['league_id']))

    logger.info('leagues')
    logger.info(leagues)

    # [{"league_key": "428.l.7124", "league_id": "7124", "name": "Never Ending", "logo_url": false, "scoring_type": "head", "start_date": "2023-10-24", "end_date": "2024-04-14", "current_week": 24, "start_week": "1", "end_week": "24"}, {"league_key": "428.l.23476", "league_id": "23476", "name": "2023~2024 Gamma", "logo_url": "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/88a86479d6cf4bc472623e59484ab6c70e397336290032a9c744125e158d2c21.jpg", "scoring_type": "head", "start_date": "2023-10-24", "end_date": "2024-04-14", "current_week": 24, "start_week": "1", "end_week": "24"}]

    return leagues


def analyze(body):

    
    logger.info('request data for analyze： %s', body)
    
    get_game_stat_categories()
    
    # parms = parse_qs(queryString)

    # if 'code' not in parms:
    #     logger.error("Code Missing in query string.")

    return {
        'statusCode': 200,
        'body': 'Analyze' 
    }

def get_league_stat_categories(league_key):
    pass

def get_league_teams(league_key):
    pass


def get_team_stat(team_key, game_stat_categories, week=0):
    pass

def get_game_stat_categories():
    '''
    Return all available stat categories of the game(NBA),
    used to dynamically create the stat table.
    '''
    logger.info("get_game_stat_categories")
    
    # if data already cached in s3, read from s3;
    # otherwise retirive from yahoo and save to s3
    categories = utils.get_json_from_s3('data/game_stat_categories.json')
    if categories is not None:
        logger.info(json.dumps(categories, indent=4))  
    else:
        logger.info("Try to retrive game stat categories from yahoo.")
        categories = {}
        uri = 'game/nba/stat_categories'
        resp = get_request(uri)
        t = objectpath.Tree(resp)
        jfilter = t.execute('$..stat_categories..stats..(stat_id, display_name, sort_order)')

        for c in jfilter:
            if 'stat_id' in c and 'display_name' in c and 'sort_order' in c:
                categories[c['stat_id']] = c

        logger.info('categories')
        logger.info(categories)
        utils.save_json_to_s3(categories, 'data/game_stat_categories.json')

def get_league_matchup( league_teams, week):
    pass


def get_request(path): 
    """Send an API request to the URI and return the response as JSON

    :param uri: URI of the API to call
    :type uri: str
    :return: JSON document of the response
    :raises: RuntimeError if any response comes back with an error
    """
    url = f'{config.FANTASY_API_URL}/{path}'
    logger.info(f'request url: {url}')

    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN
    }

    response = requests.get(url, params={'format': 'json'}, headers = headers)

    if response.status_code != 200:
        logger.error('request to {} failed with error code {}'.format(url, response.status_code))
        raise RuntimeError(response.content)

    jresp = response.json()
    return jresp