import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.mobile
def test_mobile_theme_switch_changes_page_appearance(mobile_page: Page) -> None:
    body = mobile_page.locator("body")
    switch = mobile_page.get_by_role("button", name=re.compile("Switch to .* theme"))
    before = body.evaluate(
        "el => ({background: getComputedStyle(el).backgroundColor, color: getComputedStyle(el).color})"
    )
    before_label = switch.get_attribute("aria-label")

    switch.click()
    expect(switch).not_to_have_attribute("aria-label", before_label)
    mobile_page.wait_for_function(
        "before => { const s = getComputedStyle(document.body); "
        "return s.backgroundColor !== before.background || s.color !== before.color; }",
        arg=before,
    )
    after = body.evaluate(
        "el => ({background: getComputedStyle(el).backgroundColor, color: getComputedStyle(el).color})"
    )

    assert after != before, f"После переключения темы стили body не изменились: {before}"
    assert mobile_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), (
        "После переключения темы появилась горизонтальная прокрутка"
    )

    switch.click()
    expect(switch).to_have_attribute("aria-label", before_label)
    mobile_page.wait_for_function(
        "before => { const s = getComputedStyle(document.body); "
        "return s.backgroundColor === before.background && s.color === before.color; }",
        arg=before,
    )
