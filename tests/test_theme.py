import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.mobile
def test_mobile_theme_switch_changes_page_appearance(mobile_page: Page) -> None:
    page_body = mobile_page.locator("body")
    theme_button = mobile_page.get_by_role(
        "button", name=re.compile("Switch to .* theme")
    )
    initial_colors = page_body.evaluate(
        "el => ({background: getComputedStyle(el).backgroundColor, color: getComputedStyle(el).color})"
    )
    initial_button_name = theme_button.get_attribute("aria-label")

    theme_button.click()
    expect(theme_button).not_to_have_attribute("aria-label", initial_button_name)
    mobile_page.wait_for_function(
        "initial => { const current = getComputedStyle(document.body); "
        "return current.backgroundColor !== initial.background "
        "|| current.color !== initial.color; }",
        arg=initial_colors,
    )
    changed_colors = page_body.evaluate(
        "el => ({background: getComputedStyle(el).backgroundColor, color: getComputedStyle(el).color})"
    )

    assert changed_colors != initial_colors, (
        f"После переключения цвета не изменились: {initial_colors}"
    )
    assert mobile_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), (
        "После переключения темы появилась горизонтальная прокрутка"
    )

    theme_button.click()
    expect(theme_button).to_have_attribute("aria-label", initial_button_name)
    mobile_page.wait_for_function(
        "initial => { const current = getComputedStyle(document.body); "
        "return current.backgroundColor === initial.background "
        "&& current.color === initial.color; }",
        arg=initial_colors,
    )
