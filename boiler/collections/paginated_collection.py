from math import ceil
from boiler.collections.pagination import paginate
from pprint import pprint as pp


class PaginatedCollection:
    """
    Paginated collection
    Accepts an SQLAlchemy query object on initialization along with some
    pagination settings and then allows you to iterate over itself in a
    paginated manner: iterate over items in current page then call next_page()
    to fetch next slice of data.
    """
    def __init__(self, query, *_, page=1, per_page=10, pagination_range=5):
        """
        Initialise collection
        Creates an instance of collection. Requires an query object to
        iterate through. Will issue 2 queries: one to count total items and
        second to fetch actual items. Optionally generates a page range
        to print range-like paginations of a given slice size.

        :param query:
        :param _: args, ignored
        :param page: int, page to fetch
        :param per_page: int, items per page
        :param pagination_range: int, number of pages in pagination
        """
        self._query = query
        self.page = page
        self.per_page = per_page
        self.total_items = self._query.count()
        self.total_pages = ceil(self.total_items / per_page)

        # paginate
        self.pagination = paginate(
            page=page,
            total_pages=self.total_pages,
            total_items=self.total_items,
            slice_size=pagination_range
        )['pagination']

        # fetch items
        self.items = self.fetch_items()

    def __repr__(self):
        """ Get  printable representation of collection """
        data = 'page="{}" per_page="{}" total_items="{}" total_pages="{}" '
        data += 'items="[...]"' if len(list(self.items)) > 0 else 'items="[]"'
        class_name = self.__class__.__name__
        printable = '<{} {}>'.format(class_name, data)
        return printable.format(
            self.page,
            self.per_page,
            self.total_items,
            self.total_pages
        )

    def __iter__(self):
        """ Performs generator-based iteration through page items """
        offset = 0
        while offset < len(self.items):
            item = self.items[offset]
            offset += 1
            yield item

    def fetch_items(self):
        """
        Fetch items
        Performs a query to retrieve items based on current query and
        pagination settings.
        """
        offset = self.per_page * (self.page - 1)
        items = self._query.limit(self.per_page).offset(offset).all()
        return items

    def dict(self):
        """ Returns current collection as a dictionary """
        collection = dict(
            page=self.page,
            per_page=self.per_page,
            total_items=self.total_items,
            total_pages=self.total_pages,
            pagination=self.pagination,
            items=list(self.items)
        )
        return collection

    def is_first_page(self):
        """ Check if we are on the first page """
        return self.page == 1

    def is_last_page(self):
        """ Checks if we are on the last page """
        return self.page == self.total_pages

    def next_page(self):
        """
        Next page
        Uses query object to fetch next slice of items unless on last page in
        which case does nothing
        """
        if self.is_last_page():
            return False

        self.page += 1
        self.items = self.fetch_items()
        return True

    def previous_page(self):
        """
        Previous page
        Uses query object to fetch previous slice of items unless on first
        page in which case does nothing
        """
        if self.is_first_page():
            return False

        self.page -= 1
        self.items = self.fetch_items()
        return True






