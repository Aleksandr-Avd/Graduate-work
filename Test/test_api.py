import pytest
import requests
import allure
import yaml
from pathlib import Path
from typing import Optional, Dict, Any


BASE_DIR = Path(__file__).parent.parent / "API"

with open(BASE_DIR / "config.yaml", encoding="utf-8") as f:
    config: Dict[str, Any] = yaml.safe_load(f)

with open(BASE_DIR / "test_data.yaml", encoding="utf-8") as f:
    test_data: Dict[str, Any] = yaml.safe_load(f)

BASE_URL: str = config["base_url"]
DEFAULT_API_KEY: str = config["api_key"]

HEADERS: Dict[str, str] = {
    "Content-Type": "application/json",
    "X-API-KEY": DEFAULT_API_KEY
}


def make_request(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> requests.Response:
    """
    Выполняет HTTP-запрос к API.

    :param method: HTTP-метод (GET, POST и т.д.)
    :param endpoint: путь API (например, "/movies")
    :param params: словарь параметров запроса
    :param api_key: ключ API (если None — используется ключ из конфигурации)
    :return: объект Response от requests
    """
    with allure.step(f"Формирование запроса {method} {endpoint} с параметрами {params} и api_key={'указан' if api_key else 'по умолчанию'}"):
        headers = HEADERS.copy()
        if api_key:
            headers["X-API-KEY"] = api_key
        url = BASE_URL + endpoint
        response = requests.request(method, url, headers=headers, params=params)
        allure.attach(url, name="URL запроса", attachment_type=allure.attachment_type.URI_LIST)
        allure.attach(str(headers), name="Заголовки запроса", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(params), name="Параметры запроса", attachment_type=allure.attachment_type.TEXT)
    return response


@allure.feature("Позитивные тесты Кинопоиска")
@allure.title("Поиск фильма с использованием фильтров")
def test_search_movie_with_filters() -> None:
    """
    Тест: Поиск фильма с использованием фильтров.

    Проверяется, что ответ успешный и содержит ожидаемые поля.
    """
    case = next(c for c in test_data["positive"] if c["name"] == "Поиск фильма с использованием фильтров")
    with allure.step(f"Выполнение запроса: {case['name']}"):
        response: requests.Response = make_request("GET", case["endpoint"], params=case.get("params"))
        with allure.step("Проверка кода ответа и содержания"):
            allure.attach(str(response.status_code), name="Status Code", attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"
            json_resp: Dict[str, Any] = response.json()
            assert any(k in json_resp for k in ("docs", "items", "total")), "В ответе отсутствуют ожидаемые поля"


@allure.feature("Позитивные тесты Кинопоиска")
@allure.title("Поиск фильмов по рейтингу")
def test_search_movies_by_rating() -> None:
    """
    Тест: Поиск фильмов по рейтингу.
    """
    case = next(c for c in test_data["positive"] if c["name"] == "Поиск фильмов по рейтингу")
    with allure.step(f"Выполнение запроса: {case['name']}"):
        response = make_request("GET", case["endpoint"], params=case.get("params"))
        with allure.step("Проверка кода ответа и содержания"):
            allure.attach(str(response.status_code), name="Status Code", attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200
            json_resp = response.json()
            assert any(k in json_resp for k in ("docs", "items", "total"))


@allure.feature("Позитивные тесты Кинопоиска")
@allure.title("Поиск фильма по названию")
def test_search_movie_by_name() -> None:
    """
    Тест: Поиск фильма по названию.
    """
    case = next(c for c in test_data["positive"] if c["name"] == "Поиск фильма по названию")
    with allure.step(f"Выполнение запроса: {case['name']}"):
        response = make_request("GET", case["endpoint"], params=case.get("params"))
        with allure.step("Проверка кода ответа и содержания"):
            allure.attach(str(response.status_code), name="Status Code", attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200
            json_resp = response.json()
            assert any(k in json_resp for k in ("docs", "items", "total"))


@allure.feature("Негативные тесты Кинопоиска")
@allure.title("Поиск фильма с датой из будущего (негативный кейс)")
def test_search_movie_future_year() -> None:
    """
    Тест: Поиск фильма с датой из будущего (негативный кейс).
    """
    case = next(c for c in test_data["negative"] if c["name"] == "Поиск фильма с датой из будущего")
    with allure.step(f"Выполнение запроса: {case['name']}"):
        response = make_request("GET", case["endpoint"], params=case.get("params"))
        with allure.step("Проверка кода ответа или пустого результата"):
            allure.attach(str(response.status_code), name="Status Code", attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            # Либо ошибка, либо 200 с пустым списком
            assert response.status_code != 200 or (
                response.status_code == 200 and (
                    len(response.json().get("docs", [])) == 0 or
                    len(response.json().get("items", [])) == 0 or
                    response.json().get("total", 1) == 0
                )
            )


@allure.feature("Негативные тесты Кинопоиска")
@allure.title("Поиск фильма с некорректным токеном (негативный кейс)")
def test_search_movie_invalid_token() -> None:
    """
    Тест: Поиск фильма с некорректным токеном (негативный кейс).
    """
    case = next(c for c in test_data["negative"] if c["name"] == "Поиск фильма с некорректным токеном")
    with allure.step(f"Выполнение запроса: {case['name']}"):
        response = make_request("GET", case["endpoint"], api_key=case.get("api_key"))
        with allure.step("Проверка кода ответа 401 или 403"):
            allure.attach(str(response.status_code), name="Status Code", attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code in (401, 403)


@allure.feature("Негативные тесты Кинопоиска")
@allure.title("Поиск фильма с несуществующим диапазоном рейтинга (негативный кейс)")
def test_search_movie_invalid_rating_range() -> None:
    """
    Тест: Поиск фильма с несуществующим диапазоном рейтинга (негативный кейс).
    """
    case = next(c for c in test_data["negative"] if c["name"] == "Поиск фильма с несуществующим диапазоном рейтинга")
    with allure.step(f"Выполнение запроса: {case['name']}"):
        response = make_request("GET", case["endpoint"], params=case.get("params"))
        with allure.step("Проверка кода ответа или пустого результата"):
            allure.attach(str(response.status_code), name="Status Code", attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code != 200 or (
                response.status_code == 200 and (
                    len(response.json().get("docs", [])) == 0 or
                    len(response.json().get("items", [])) == 0 or
                    response.json().get("total", 1) == 0
                )
            )


@allure.feature("Негативные тесты Кинопоиска")
@allure.title("Поиск фильма по несуществующему названию (негативный кейс)")
def test_search_movie_nonexistent_name() -> None:
    """
    Тест: Поиск фильма по несуществующему названию (негативный кейс).
    """
    case = next(c for c in test_data["negative"] if c["name"] == "Поиск фильма по несуществующему названию")
    with allure.step(f"Выполнение запроса: {case['name']}"):
        response = make_request("GET", case["endpoint"], params=case.get("params"))
        with allure.step("Проверка кода ответа или пустого результата"):
            allure.attach(str(response.status_code), name="Status Code", attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code != 200 or (
                response.status_code == 200 and (
                    len(response.json().get("docs", [])) == 0 or
                    len(response.json().get("items", [])) == 0 or
                    response.json().get("total", 1) == 0
                )
            )


@allure.feature("Негативные тесты Кинопоиска")
@allure.title("Поиск фильма с датой из далёкого прошлого (негативный кейс)")
def test_search_movie_past_year() -> None:
    """
    Тест: Поиск фильма с датой из далёкого прошлого (негативный кейс).
    """
    case = next(c for c in test_data["negative"] if c["name"] == "Поиск фильма с датой из далёкого прошлого")
    with allure.step(f"Выполнение запроса: {case['name']}"):
        response = make_request("GET", case["endpoint"], params=case.get("params"))
        with allure.step("Проверка кода ответа или пустого результата"):
            allure.attach(str(response.status_code), name="Status Code", attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code != 200 or (
                response.status_code == 200 and (
                    len(response.json().get("docs", [])) == 0 or
                    len(response.json().get("items", [])) == 0 or
                    response.json().get("total", 1) == 0
                )
            )
