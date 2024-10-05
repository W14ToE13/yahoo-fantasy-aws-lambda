import os

from config import logger
import fantasy_api as fantasyapi
import utils
import yahoo_oauth as yOauth

def lambda_handler(event, context):

    # print(event)
    # print(context)

    path = event['rawPath']
    logger.info('rawPath: %s', path)

    if path =='/login':
        return yOauth.login()

    elif path == '/callback':
        return yOauth.callback(event['rawQueryString'])

    # for routes other than login and callback, we need  session id
    sessionId = utils.getSessionIdFromCookies(event['cookies'])
    logger.info('SessionId: %s', sessionId)
    valid = utils.isValidSession(sessionId)
    if valid == False:
        logger.info('Invalid SessionId: %s, rediect to login page.', sessionId)
        return {
            "isBase64Encoded": False,
            "statusCode": 302,
            "headers": {
                "Location": f'{os.environ.get("BASE_URL")}/login'
            }
        }

   
    
    if path =='/api/userleauges':

        return fantasyapi.get_leagues()

    elif path == '/api/analyze':

        return fantasyapi.analyze()

 