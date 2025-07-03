from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://www.kinopoisk.ru/")
FILM_ID = int(os.getenv("FILM_ID", 301))