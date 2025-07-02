import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from . import config


class MainPage:
    URL = config.BASE_URL

    def __init__(self, driver: WebDriver):
        """
        Инициализация страницы с драйвером и ожиданием.
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    @allure.step("Проверяем наличие капчи")
    def is_captcha_page(self) -> bool:
        """
        Проверяет, отображается ли страница с капчей.

        :return: True, если капча есть, иначе False
        """
        try:
            self.driver.find_element(By.CSS_SELECTOR, config.SELECTOR_CAPTCHA_BUTTON)
            return True
        except NoSuchElementException:
            return False

    @allure.step("Обрабатываем капчу, если она появляется")
    def captcha(self):
        """
        Если капча появляется, пытается её закрыть.
        """
        if self.is_captcha_page():
            try:
                button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTOR_CAPTCHA_BUTTON)))
                button.click()
                self.wait.until_not(EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTOR_CAPTCHA_BUTTON)))
            except TimeoutException:
                pass

    @allure.step("Открыть главную страницу")
    def open(self) -> None:
        """
        Открывает главную страницу и обрабатывает капчу.
        """
        self.driver.get(self.URL)
        self.captcha()

    @allure.step("Проверить, что главная страница загружена (логотип КиноПоиск видим)")
    def is_loaded(self) -> bool:
        """
        Проверяет, что логотип видим (главная страница загружена).

        :return: True, если логотип видим, иначе False
        """
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, config.SELECTOR_LOGO_IMG)))
            return True
        except TimeoutException:
            return False

    @allure.step("Получить элемент рейтинга фильма")
    def rating_element(self):
        """
        Возвращает элемент рейтинга фильма.

        :return: WebElement с рейтингом
        """
        return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTOR_RATING_SPAN)))

    @allure.step("Получить элемент меню навигации")
    def navigation_menu(self):
        """
        Возвращает элемент меню навигации.

        :return: WebElement меню навигации
        """
        return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTOR_NAVIGATION_MENU)))

    @allure.step("Получить расположение и размер меню")
    def get_navigation_menu_location(self):
        """
        Возвращает расположение и размер навигационного меню.

        :return: Кортеж (location, size)
        """
        menu = self.navigation_menu()
        return menu.location, menu.size

    @allure.step("Навести курсор на элемент")
    def hover_over_element(self, element):
        """
        Наводит курсор мыши на элемент.

        :param element: WebElement для наведения
        """
        ActionChains(self.driver).move_to_element(element).perform()

    @allure.step("Получить CSS-свойство 'cursor' элемента")
    def get_cursor_style_on_element(self, element) -> str:
        """
        Получает CSS-свойство 'cursor' у элемента.

        :param element: WebElement
        :return: Значение свойства cursor
        """
        return self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).getPropertyValue('cursor');",
            element
        )

    @allure.step("Открыть страницу фильма по ID")
    def open_film_page(self, film_id: int = None) -> None:
        """
        Открывает страницу фильма по ID.

        :param film_id: ID фильма. Если None, используется дефолт из config.
        """ 
        if film_id is None:
            film_id = config.FILM_ID
        film_url = f"{self.URL}film/{film_id}"
        self.driver.get(film_url)