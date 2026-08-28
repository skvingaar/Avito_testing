import re

import pytest
from playwright.sync_api import expect

from pages.stats_page import StatsPage


FULL_TIMER_RANGE = re.compile(r"^(5:00|4:5[5-9])$")


@pytest.mark.desktop
def test_refresh_updates_statistics(statistics_page: StatsPage) -> None:
    response = statistics_page.refresh_statistics()

    assert response.ok or response.status == 304, (
        f"Обновление статистики завершилось с HTTP {response.status}"
    )
    expect(statistics_page.timer).to_have_text(FULL_TIMER_RANGE)
    seconds_left = statistics_page.timer_seconds()
    assert 295 <= seconds_left <= 300, (
        f"После обновления осталось {seconds_left} секунд вместо пяти минут"
    )


@pytest.mark.desktop
def test_stop_timer_stops_countdown(statistics_page: StatsPage) -> None:
    statistics_page.stop_button.click()

    expect(statistics_page.start_button).to_be_visible()
    expect(statistics_page.timer_stopped_message).to_be_visible()
    expect(statistics_page.timer).to_be_hidden()


@pytest.mark.desktop
@pytest.mark.xfail(
    strict=True,
    reason="BUG-02: после остановки кнопка запуска не возобновляет таймер",
)
def test_start_timer_resumes_countdown(statistics_page: StatsPage) -> None:
    statistics_page.stop_button.click()
    expect(statistics_page.start_button).to_be_visible()

    statistics_page.start_button.click()
    expect(statistics_page.stop_button).to_be_visible()
    expect(statistics_page.timer).to_be_visible()
    timer_before_wait = statistics_page.timer.inner_text()
    expect(statistics_page.timer).not_to_have_text(timer_before_wait, timeout=2_500)
