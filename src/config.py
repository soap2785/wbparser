from os import getenv
from dotenv import load_dotenv

load_dotenv()

RUSSIAN_PROXIES = getenv("RUSSIAN_PROXIES").split(";")