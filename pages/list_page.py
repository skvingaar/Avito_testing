import re
from collections.abc import Sequence

from playwright.sync_api import Locator, Page, expect


class ListPage:
    CARD = 'main [class*="_card_"]:has(> [class*="card__checkbox"])'
    PRICE = '[class*="card__price"]'
    CATEGORY = '[class*="card__category"]'
    URGENT = '[class*="card__priority"], [class*="card__urgent"]'

    def __init__(self, page: Page) -> None:
        self.page = page
        self.cards = page.locator(self.CARD)
        self.min_price, self.max_price = page.get_by_role("spinbutton").all()
        comboboxes = page.get_by_role("combobox")
        self.sort = comboboxes.filter(
            has=page.get_by_role("option", name="Цене", exact=True)
        )
        self.order = comboboxes.filter(
            has=page.get_by_role("option", name="По возрастанию", exact=True)
        )
        self.category = comboboxes.filter(
            has=page.get_by_role("option", name="Все категории", exact=True)
        )
        self.only_urgent = page.get_by_role("checkbox", name=re.compile("Только срочные"))

    @staticmethod
    def _number(text: str) -> int:
        return int("".join(re.findall(r"\d+", text)))

    def wait_for_results(self) -> None:
        expect(self.cards.first).to_be_visible(timeout=30_000)

    def wait_until_changed(self, previous_title: str) -> None:
        expect(self.cards.first.locator("h3")).not_to_have_text(previous_title, timeout=15_000)
        self.wait_for_results()

    def first_title(self) -> str:
        return self.cards.first.locator("h3").inner_text()

    def prices(self) -> list[int]:
        return [self._number(text) for text in self.cards.locator(self.PRICE).all_inner_texts()]

    def categories(self) -> list[str]:
        return [text.strip() for text in self.cards.locator(self.CATEGORY).all_inner_texts()]

    def select_price_range(self, lower: int, upper: int) -> None:
        self.min_price.fill(str(lower))
        self.max_price.fill(str(upper))
        self.max_price.press("Enter")
        self.wait_for_results()

    def select_sort(self, order: str) -> None:
        self.sort.select_option(label="Цене")
        self.order.select_option(label=order)
        reverse = order == "По убыванию"
        self.page.wait_for_function(
            r"""({selector, reverse}) => {
                const values = [...document.querySelectorAll(selector)].map(el =>
                    Number(el.textContent.replace(/\D/g, ''))
                );
                if (values.length < 2) return false;
                const sorted = [...values].sort((a, b) => reverse ? b - a : a - b);
                return values.every((value, index) => value === sorted[index]);
            }""",
            arg={"selector": self.PRICE, "reverse": reverse},
        )

    def available_categories(self) -> Sequence[str]:
        return self.category.locator("option").all_text_contents()[1:]

    def choose_category(self, name: str) -> None:
        self.category.select_option(label=name)
        self.page.wait_for_function(
            """({selector, name}) => {
                const values = [...document.querySelectorAll(selector)]
                    .map(el => el.textContent.trim());
                return values.length > 0 && values.every(value => value === name);
            }""",
            arg={"selector": self.CATEGORY, "name": name},
        )

    def enable_only_urgent(self) -> None:
        # The native checkbox is visually hidden; click its accessible label.
        self.page.get_by_text("Только срочные", exact=False).first.click()
        expect(self.only_urgent).to_be_checked()
        self.page.wait_for_function(
            """selector => {
                const cards = [...document.querySelectorAll(selector)];
                return cards.length > 0
                    && cards.every(card => card.textContent.includes('Срочно'));
            }""",
            arg=self.CARD,
        )

    def urgent_badges(self) -> Locator:
        return self.cards.get_by_text(re.compile("Срочно"))
