import pytest

from pages.list_page import ListPage


def skip_without_cards(list_page: ListPage, minimum: int = 1) -> None:
    if not list_page.has_cards(minimum):
        pytest.skip(f"Для проверки нужно карточек: {minimum}")


@pytest.mark.desktop
def test_price_filter_keeps_prices_in_range(listing_page: ListPage) -> None:
    skip_without_cards(listing_page)
    prices_before_filter = listing_page.visible_prices()
    min_price = min(prices_before_filter)
    max_price = max(prices_before_filter)

    listing_page.apply_price_filter(min_price, max_price)
    filtered_prices = listing_page.visible_prices()

    assert filtered_prices, "После фильтрации не найдено ни одного объявления"
    prices_outside_range = [
        price for price in filtered_prices if not min_price <= price <= max_price
    ]
    assert not prices_outside_range, (
        f"Цены вне диапазона {min_price}–{max_price}: {prices_outside_range}"
    )


@pytest.mark.desktop
@pytest.mark.parametrize(
    ("direction", "descending"),
    [("По возрастанию", False), ("По убыванию", True)],
)
def test_price_sorting_orders_cards(
    listing_page: ListPage, direction: str, descending: bool
) -> None:
    skip_without_cards(listing_page, minimum=2)
    listing_page.sort_by_price(direction)
    sorted_prices = listing_page.visible_prices()

    assert sorted_prices == sorted(sorted_prices, reverse=descending), (
        f"Цены не отсортированы ({direction.lower()}): {sorted_prices}"
    )


@pytest.mark.desktop
def test_category_filter_shows_selected_category(listing_page: ListPage) -> None:
    skip_without_cards(listing_page)
    selected_category = listing_page.visible_categories()[0]
    assert selected_category in listing_page.available_categories()

    listing_page.select_category(selected_category)
    filtered_categories = listing_page.visible_categories()

    if not filtered_categories:
        pytest.skip(f"В категории «{selected_category}» больше нет объявлений")
    assert set(filtered_categories) == {selected_category}, (
        f"В фильтр «{selected_category}» попали категории: "
        f"{sorted(set(filtered_categories))}"
    )


@pytest.mark.desktop
@pytest.mark.xfail(
    strict=True,
    reason="BUG-01: фильтр «Только срочные» оставляет обычные объявления",
)
def test_only_urgent_filter_hides_regular_ads(listing_page: ListPage) -> None:
    skip_without_cards(listing_page)
    listing_page.show_only_urgent()

    regular_ad_titles = [
        card.locator("h3").inner_text()
        for card in listing_page.cards.all()
        if card.get_by_text("Срочно", exact=False).count() == 0
    ]
    assert not regular_ad_titles, (
        "После включения «Только срочные» показаны обычные объявления: "
        f"{regular_ad_titles}"
    )
