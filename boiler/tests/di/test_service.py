class TestService():
    """
    Test service
    This is used for testing dependency injection
    """
    def __init__(self, one=None, two=None):
        self.one = one
        self.two = two
        self.three = None

    def __repr__(self):
        """ Get printable representation of service"""
        tpl = '<TestService one={} two={} three={}>'
        return tpl.format(self.one, self.two, self.three)

    def setter(self, one, two, three):
        """ Testing setter injection """
        self.one = one
        self.two = two
        self.three = three
        return self