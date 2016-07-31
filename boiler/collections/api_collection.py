from json import dumps
from boiler.collections import PaginatedCollection


class ApiCollection(PaginatedCollection):
    """
    API Collection
    Works the same way as a paginated collection, but also applies
    serializer to each item. Useful in API responses.
    """
    def __init__(self, query, *_, serialize_function, **kwargs):
        self.serializer = serialize_function
        super().__init__(query, **kwargs)

    def __iter__(self):
        """ Performs generator-based iteration through page items """
        offset = 0
        while offset < len(self.items):
            item = self.items[offset]
            offset += 1
            yield self.serializer(item)

    def dict(self):
        """ Returns current collection as a dictionary """
        collection = super().dict()
        serialized_items = []
        for item in collection['items']:
            serialized_items.append(self.serializer(item))

        collection['items'] = serialized_items
        return collection

    def json(self):
        """ Returns a json representation of collection """
        return dumps(self.dict())