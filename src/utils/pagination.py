from math import ceil


class Pagination:
    """Paginador reutilizable para listas del frontend."""

    ALLOWED_PER_PAGE = (5, 10, 20, 50, 100)

    def __init__(self, items=None, page=1, per_page=10):
        self.items = items or []

        try:
            self.per_page = int(per_page)
        except (TypeError, ValueError):
            self.per_page = 10

        if self.per_page not in self.ALLOWED_PER_PAGE:
            self.per_page = 10

        try:
            self.page = int(page)
        except (TypeError, ValueError):
            self.page = 1

        self.page = max(1, self.page)
        self.total = len(self.items)
        self.total_pages = max(1, ceil(self.total / self.per_page))
        self.page = min(self.page, self.total_pages)

        self.start = (self.page - 1) * self.per_page
        self.end = self.start + self.per_page
        self.items_page = self.items[self.start:self.end]

    @property
    def has_previous(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.total_pages

    @property
    def previous_page(self):
        return max(1, self.page - 1)

    @property
    def next_page(self):
        return min(self.total_pages, self.page + 1)

    @property
    def first_item(self):
        return 0 if self.total == 0 else self.start + 1

    @property
    def last_item(self):
        return min(self.end, self.total)

    @property
    def pages(self):
        if self.total_pages <= 7:
            return list(range(1, self.total_pages + 1))

        pages = [1]
        start = max(2, self.page - 2)
        end = min(self.total_pages - 1, self.page + 2)

        if start > 2:
            pages.append(None)

        pages.extend(range(start, end + 1))

        if end < self.total_pages - 1:
            pages.append(None)

        pages.append(self.total_pages)
        return pages


def paginate(items, page=1, per_page=10):
    return Pagination(items, page, per_page)
