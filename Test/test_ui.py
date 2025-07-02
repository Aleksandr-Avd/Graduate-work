import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Ui.main_page import MainPage
import Ui.config as config
from selenium import webdriver

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(25)
    yield driver
    driver.quit()

@pytest.fixture
def main_page(driver):
    page = MainPage(driver)
    page.open()
    yield page

@allure.title("Проверка загрузки главной страницы")
def test_main_page_loads(main_page) -> None:
    """
    Проверяет, что главная страница загружается корректно.
    """
    wait = WebDriverWait(main_page.driver, 20)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTOR_LOGO_IMG)))
    assert main_page.is_loaded(), "Главная страница не загрузилась"

@allure.title("Проверка отображения и расположения рейтинга фильма")
def test_movie_rating_displayed(main_page) -> None:
    """
    Проверяет, что рейтинг фильма отображается и расположен корректно.
    """
    main_page.open_film_page(config.FILM_ID)
    rating = main_page.rating_element()
    assert rating.is_displayed(), "Рейтинг фильма не отображается"
    loc = rating.location
    assert loc["x"] > 0 and loc["y"] > 0, f"Рейтинг расположен некорректно, координаты: {loc}"

@allure.title("Проверка работы кнопки назад в браузере")
def test_browser_back_button(driver, main_page) -> None:
    """
    Проверяет, что кнопка назад в браузере возвращает на главную страницу.
    """
    driver.get(f"{config.BASE_URL}film/{config.FILM_ID}")
    driver.back()
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTOR_LOGO_IMG)))
    assert "Кинопоиск" in driver.title

@allure.title("Проверка расположения меню навигации слева")
def test_navigation_menu_location(main_page) -> None:
    """
    Проверяет, что меню навигации расположено слева (x < 100).
    """
    location, _ = main_page.get_navigation_menu_location()
    assert location["x"] < 100, f"Меню не слева, x={location['x']}"

@allure.title("Проверка изменения курсора на pointer при наведении")
def test_cursor_changes_to_pointer_on_hover(main_page) -> None:
    """
    Проверяет, что при наведении курсор меняется на pointer.
    """
    wait = WebDriverWait(main_page.driver, 10)
    active_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTOR_LOGO_IMG)))
    main_page.hover_over_element(active_elem)
    cursor = main_page.get_cursor_style_on_element(active_elem)
    assert cursor == "pointer", f"Курсор не pointer, а {cursor}"