from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    """
    Regex converter
    Allows to use regular expressions in flask urls definitions.
    An example of route definition: '/<regex("[abcABC0-9]{4,6}"):user>-<slug>/
    Will produce: user and slug variables.
    """
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
