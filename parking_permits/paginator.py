from django.core.paginator import Paginator


class QuerySetPaginator:
    default_page_size = 10

    def __init__(self, qs, page_input):
        page_size = page_input.get("page_size", self.default_page_size)
        self.paginator = Paginator(qs, page_size)
        page_index = page_input.get("page", 1)
        self.page = self.paginator.page(page_index)

    @property
    def next_page(self):
        return self.page.next_page_number() if self.page.has_next() else None

    @property
    def prev_page(self):
        return self.page.previous_page_number() if self.page.has_previous() else None

    @property
    def object_list(self):
        return self.page.object_list

    @property
    def page_info(self):
        return {
            "next": self.next_page,
            "prev": self.prev_page,
            "page": self.page.number,
            "num_pages": self.paginator.num_pages,
            "start_index": self.page.start_index(),
            "end_index": self.page.end_index(),
            "count": self.paginator.count,
        }
