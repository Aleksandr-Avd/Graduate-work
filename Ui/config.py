from dotenv import load_dotenv
import os


load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://www.kinopoisk.ru/")
FILM_ID = int(os.getenv("FILM_ID", 301))

SELECTOR_CAPTCHA_BUTTON = os.getenv("SELECTOR_CAPTCHA_BUTTON", ".CheckboxCaptcha-Button")
SELECTOR_LOGO_IMG = os.getenv("SELECTOR_LOGO_IMG", 'img[alt="Кинопоиск"]')
SELECTOR_RATING_SPAN = os.getenv("SELECTOR_RATING_SPAN", "span.styles_ratingKpTop__84afd")
SELECTOR_NAVIGATION_MENU = os.getenv("SELECTOR_NAVIGATION_MENU", "nav[data-tid='e500879d'] > ul")

