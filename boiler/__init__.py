import os
from dotenv import load_dotenv as dotenvs


def load_dotenvs():
    """
    Load dotenvs
    Loads .env and .flaskenv files from project root directory.
    :return:
    """
    if not os.getenv('DOTENVS_LOADED'):
        envs = ['.env', '.flaskenv']
        for env in envs:
            path = os.path.join(os.getcwd(), env)
            if os.path.isfile(path):
                dotenvs(path)
        os.environ['DOTENVS_LOADED'] = 'yes'


# run immediately
load_dotenvs()
