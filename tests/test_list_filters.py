import pytest
from playwright.sync_api import Page

from pages.list_page import ListPage


@pytest.mark.desktop
def test_price_filter_shows_only_prices_inside_selected_range(app_page: Page) -> None:
    listing = ListPage(app_page)
    original_prices = listing.prices()
    lower, upper = min(original_prices), max(original_prices)

    listing.select_price_range(lower, upper)
    actual_prices = listing.prices()

    assert actual_prices, "После применения диапазона цен выдача неожиданно пуста"
    assert all(lower <= price <= upper for price in actual_prices), (
        f"Цены вне диапазона {lower}–{upper}: "
        f"{[price for price in actual_prices if not lower <= price <= upper]}"
    )


@pytest.mark.desktop
@pytest.mark.parametrize(
    ("order", "reverse"),
    [("По возрастанию", False), ("По убыванию", True)],
)
def test_price_sorting_orders_visible_cards(app_page: Page, order: str, reverse: bool) -> None:
    listing = ListPage(app_page)
    listing.select_sort(order)
    prices = listing.prices()

    assert len(prices) > 1, "Для проверки сортировки нужно минимум две карточки"
    assert prices == sorted(prices, reverse=reverse), (
        f"Цены не отсортированы ({order.lower()}): {prices}"
    )


@pytest.mark.desktop
def test_category_filter_shows_only_selected_category(app_page: Page) -> None:
    listing = ListPage(app_page)
    visible_categories = listing.categories()
    selected = visible_categories[0]
    assert selected in listing.available_categories()

    listing.choose_category(selected)
    actual_categories = listing.categories()

    assert actual_categories, f"Для категории «{selected}» выдача неожиданно пуста"
    assert set(actual_categories) == {selected}, (
        f"В фильтр «{selected}» попали категории: {sorted(set(actual_categories))}"
    )


@pytest.mark.desktop
@pytest.mark.xfail(
    strict=True,
    reason="BUG-01: фильтр «Только срочные» оставляет обычные объявления",
)
def test_only_urgent_shows_urgent_ads(app_page: Page) -> None:
    listing = ListPage(app_page)
    listing.enable_only_urgent()

    assert listing.cards.count() > 0, "После включения «Только срочные» выдача пуста"
    ordinary = [
        card.locator("h3").inner_text()
        for card in listing.cards.all()
        if card.get_by_text("Срочно", exact=False).count() == 0
    ]
    assert not ordinary, (
        "После включения «Только срочные» показаны обычные объявления: "
        f"{ordinary}"
    )
