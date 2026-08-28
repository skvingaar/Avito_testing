import re

import pytest
from playwright.sync_api import Page, expect


def _timer(page: Page):
    return page.get_by_text(re.compile(r"^\d+:\d{2}$"))


@pytest.mark.desktop
def test_refresh_requests_and_updates_statistics(stats_page: Page) -> None:
    refresh = stats_page.get_by_role("button", name="Обновить сейчас")
    timer = _timer(stats_page)

    with stats_page.expect_response(
        lambda response: response.request.resource_type in {"fetch", "xhr"}
        and "/api/v1/ads" in response.url
    ) as response_info:
        refresh.click()

    response = response_info.value
    assert response.ok or response.status == 304, (
        f"Обновление статистики завершилось с HTTP {response.status}"
    )
    expect(timer).to_have_text(re.compile(r"^(5:00|4:5[5-9])$"))
    timer_text = timer.inner_text()
    minutes, seconds = map(int, timer_text.split(":"))
    remaining_seconds = minutes * 60 + seconds
    assert 295 <= remaining_seconds <= 300, (
        f"После обновления таймер не сбросился к пяти минутам: {timer_text}"
    )


@pytest.mark.desktop
def test_stop_timer_stops_countdown(stats_page: Page) -> None:
    stop = stats_page.get_by_role("button", name="Отключить автообновление")
    timer = _timer(stats_page)

    stop.click()
    expect(stats_page.get_by_role("button", name="Включить автообновление")).to_be_visible()
    expect(stats_page.get_by_text("Автообновление выключено")).to_be_visible()
    expect(timer).to_be_hidden()


@pytest.mark.desktop
@pytest.mark.xfail(
    strict=True,
    reason="BUG-02: после остановки кнопка запуска не возобновляет таймер",
)
def test_start_timer_resumes_countdown(stats_page: Page) -> None:
    stats_page.get_by_role("button", name="Отключить автообновление").click()
    start = stats_page.get_by_role("button", name="Включить автообновление")
    expect(start).to_be_visible()

    start.click()
    expect(stats_page.get_by_role("button", name="Отключить автообновление")).to_be_visible()
    timer = _timer(stats_page)
    expect(timer).to_be_visible()
    initial = timer.inner_text()
    expect(timer).not_to_have_text(initial, timeout=2_500)
