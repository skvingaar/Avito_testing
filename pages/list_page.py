import re

from playwright.sync_api import Page, expect


class ListPage:
    CARD_SELECTOR = 'main [class*="_card_"]:has(> [class*="card__checkbox"])'
    PRICE_SELECTOR = '[class*="card__price"]'
    CATEGORY_SELECTOR = '[class*="card__category"]'

    def __init__(self, page: Page) -> None:
        self.page = page
        self.cards = page.locator(self.CARD_SELECTOR)
        self.min_price_input, self.max_price_input = page.get_by_role("spinbutton").all()
        dropdowns = page.get_by_role("combobox")
        self.sort_field = dropdowns.filter(
            has=page.get_by_role("option", name="Цене", exact=True)
        )
        self.sort_direction = dropdowns.filter(
            has=page.get_by_role("option", name="По возрастанию", exact=True)
        )
        self.category_filter = dropdowns.filter(
            has=page.get_by_role("option", name="Все категории", exact=True)
        )
        self.only_urgent_checkbox = page.get_by_role(
            "checkbox", name=re.compile("Только срочные")
        )

    @staticmethod
    def _parse_price(text: str) -> int:
        return int("".join(re.findall(r"\d+", text)))

    def wait_until_loaded(self) -> None:
        self.page.wait_for_function(
            """selector => document.querySelector(selector)
                || document.body.textContent.includes('Объявления не найдены')""",
            arg=self.CARD_SELECTOR,
            timeout=30_000,
        )

    def has_cards(self, minimum: int = 1) -> bool:
        return self.cards.count() >= minimum

    def visible_prices(self) -> list[int]:
        price_texts = self.cards.locator(self.PRICE_SELECTOR).all_inner_texts()
        return [self._parse_price(text) for text in price_texts]

    def visible_categories(self) -> list[str]:
        category_texts = self.cards.locator(self.CATEGORY_SELECTOR).all_inner_texts()
        return [text.strip() for text in category_texts]

    def apply_price_filter(self, min_price: int, max_price: int) -> None:
        self.min_price_input.fill(str(min_price))
        self.max_price_input.fill(str(max_price))
        self.max_price_input.press("Enter")
        self.wait_until_loaded()

    def sort_by_price(self, direction: str) -> None:
        self.sort_field.select_option(label="Цене")
        self.sort_direction.select_option(label=direction)
        descending = direction == "По убыванию"
        self.page.wait_for_function(
            r"""({selector, descending}) => {
                const values = [...document.querySelectorAll(selector)].map(el =>
                    Number(el.textContent.replace(/\D/g, ''))
                );
                if (values.length < 2) return false;
                const sorted = [...values].sort((a, b) => descending ? b - a : a - b);
                return values.every((value, index) => value === sorted[index]);
            }""",
            arg={"selector": self.PRICE_SELECTOR, "descending": descending},
        )

    def available_categories(self) -> list[str]:
        return self.category_filter.locator("option").all_text_contents()[1:]

    def select_category(self, category_name: str) -> None:
        self.category_filter.select_option(label=category_name)
        self.page.wait_for_function(
            """({selector, categoryName}) => {
                const values = [...document.querySelectorAll(selector)]
                    .map(el => el.textContent.trim());
                const empty = document.body.textContent.includes('Объявления не найдены');
                return empty || (values.length > 0
                    && values.every(value => value === categoryName));
            }""",
            arg={
                "selector": self.CATEGORY_SELECTOR,
                "categoryName": category_name,
            },
        )

    def show_only_urgent(self) -> None:
        # Кликаем видимую подпись.
        self.page.get_by_text("Только срочные", exact=False).first.click()
        expect(self.only_urgent_checkbox).to_be_checked()
        self.page.wait_for_function(
            """selector => {
                const cards = [...document.querySelectorAll(selector)];
                return cards.length > 0
                    && cards.every(card => card.textContent.includes('Срочно'));
            }""",
            arg=self.CARD_SELECTOR,
        )
