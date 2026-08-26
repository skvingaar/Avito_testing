import re

import pytest
from playwright.sync_api import Page


BASE_URL = "https://cerulean-praline-8e5aa6.netlify.app"


@pytest.fixture(autouse=True)
def configure_page(page: Page) -> None:
    page.set_default_timeout(15_000)


@pytest.fixture
def app_page(page: Page) -> Page:
    page.goto(BASE_URL)
    page.get_by_role("heading", name="Модерация объявлений").wait_for()
    page.locator("main h3").first.wait_for(timeout=30_000)
    return page


@pytest.fixture
def mobile_page(page: Page) -> Page:
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(BASE_URL)
    page.get_by_role("heading", name="Модерация объявлений").wait_for()
    return page


@pytest.fixture
def stats_page(page: Page) -> Page:
    # Direct /stats requests return Netlify 404, therefore navigate through the SPA.
    page.goto(BASE_URL)
    page.get_by_role("link", name=re.compile("Статистика")).click()
    page.get_by_role("heading", name=re.compile("Статистика модератора")).wait_for()
    return page

