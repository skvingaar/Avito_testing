import pytest
from playwright.sync_api import Page

from pages.list_page import ListPage
from pages.stats_page import StatsPage


BASE_URL = "https://cerulean-praline-8e5aa6.netlify.app"


@pytest.fixture(autouse=True)
def configure_page(page: Page) -> None:
    page.set_default_timeout(15_000)


@pytest.fixture
def listing_page(page: Page) -> ListPage:
    page.goto(BASE_URL)
    page.get_by_role("heading", name="Модерация объявлений").wait_for()
    listing = ListPage(page)
    listing.wait_until_loaded()
    return listing


@pytest.fixture
def mobile_page(page: Page) -> Page:
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(BASE_URL)
    page.get_by_role("heading", name="Модерация объявлений").wait_for()
    return page


@pytest.fixture
def statistics_page(page: Page) -> StatsPage:
    statistics = StatsPage(page)
    statistics.open(BASE_URL)
    return statistics
