import re

from playwright.sync_api import Page, Response, TimeoutError as PlaywrightTimeoutError


class StatsPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role("heading", name=re.compile("Статистика модератора"))
        self.timer = page.get_by_text(re.compile(r"^\d+:\d{2}$"))
        self.refresh_button = page.get_by_role("button", name="Обновить сейчас")
        self.stop_button = page.get_by_role("button", name="Отключить автообновление")
        self.start_button = page.get_by_role("button", name="Включить автообновление")
        self.timer_stopped_message = page.get_by_text("Автообновление выключено")

    def open(self, base_url: str, attempts: int = 3) -> None:
        last_timeout: PlaywrightTimeoutError | None = None

        for _ in range(attempts):
            try:
                self.page.goto(base_url)
                stats_link = self.page.get_by_role("link", name=re.compile("Статистика"))
                stats_link.wait_for(timeout=5_000)
                stats_link.click()
                self.heading.wait_for(timeout=5_000)
                self.timer.wait_for(timeout=5_000)
                return
            except PlaywrightTimeoutError as error:
                # Повторяем открытие страницы.
                last_timeout = error

        raise AssertionError(
            f"Страница статистики не открылась за {attempts} попытки"
        ) from last_timeout

    def refresh_statistics(self) -> Response:
        with self.page.expect_response(
            lambda response: response.request.resource_type in {"fetch", "xhr"}
            and "/api/v1/ads" in response.url
        ) as response_info:
            self.refresh_button.click()

        return response_info.value

    def timer_seconds(self) -> int:
        minutes, seconds = map(int, self.timer.inner_text().split(":"))
        return minutes * 60 + seconds
