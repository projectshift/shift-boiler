from jinja2 import Markup


"""
Filters
This holds custom jinja filters for localization and formatting dates
"""


class LocalizableFilterSet:

    def __init__(self):
        self.locale = None

    def get_locale(self):
        """
        Get locale
        Will extract locale from application, trying to get one from babel
        first, then, if not available, will get one from app config
        """
        if not self.locale:
            try:
                import flask_babel as babel
                self.locale = str(babel.get_locale()).lower()
            except ImportError:
                from flask import current_app
                self.locale = current_app.config['DEFAULT_LOCALE'].lower

        return self.locale

    def get_language(self):
        """
        Get language
        If locale contains region, will cut that off. Returns just
        the language code
        """
        locale = self.get_locale()
        language = locale
        if '_' in locale:
            language = locale[0:locale.index('_')]
        return language


class HumanizeFilters(LocalizableFilterSet):
    """
    Humanize filters collection
    Provides facilities to humanize dates, date interval and numbers in
    a localized way. For examples see: https://github.com/jmoiron/humanize
    """
    def get_filter_names(self):
        """ Returns a list of supported filter names """
        return [
            'naturalsize',
            'naturaltime',
            'naturalday',
            'naturaldate',
            'intword',
            'apnumber',
            'fractional'
        ]

    def localize_humanize(self):
        """ Setts current language to humanize """
        import humanize
        language = self.get_language()
        if language != 'en':
            humanize.i18n.activate(language)

    def __getattr__(self, item):
        """ Overloads calls to supported humanize methods """
        if item in self.get_filter_names():
            import humanize

            def humanizer(*args, **kwargs):
                self.localize_humanize()
                func = getattr(humanize, item)
                return func(*args, **kwargs)
            return humanizer

    def get_filters(self):
        """ Returns a dictionary of filters """
        filters = dict()
        for filter in self.get_filter_names():
            filters[filter] = getattr(self, filter)
        return filters


class DateFilters(LocalizableFilterSet):
    """
    Date filters
    These allow to format adn transform datetime objects in templates
    """
    def get_filters(self):
        """ Returns a dictionry of filters """
        return dict(
            date_format=self.date_format,
            date_fromnow=self.date_fromnow,
        )

    def date_format(self, value, format='%d-%m-%Y %H:%M'):
        """ Format datetime object """
        return Markup(value.strftime(format))

    def date_fromnow(self, value):
        """ Displays humanized date (time since) """
        import humanize
        language = self.get_language()
        if language != 'en':
            humanize.i18n.activate(language)
        return Markup(humanize.naturaltime(value))





class MomentJsFilters:
    """
    Provides a set of javascript filters with moment.js.
    This will require you to include momentjs javascript file. You can load one
    from a CDN. You can also load locale dictionary jsvascript to translate
    on the fly: https://cdnjs.com/libraries/moment.js/

    Use the filter inside your templates like so:
        {{ something.datetime | moment_fromnow}}
        {{ something.datetime | moment_format('MMMM Do YYYY, h:mm:ss a' )}}

    Visit MomentJS for more formatting options:
        http://momentjs.com/ for more formatting options

    """

    def _render(self, value, format):
        """ Writes javascript to call momentjs function """
        template = '<script>\ndocument.write(moment(\"{t}\").{f});\n</script>'
        return Markup(template.format(t=value, f=format))

    def format(self, value, format='MMMM Do YYYY'):
        return self._render(value, 'format(\"{}\")'.format(format))

    def calendar(self, value):
        return self._render(value, 'calendar()')

    def from_now(self, value):
        return self._render(value, 'fromNow()')

    def get_filters(self):
        """ Returns a collection of momentjs filters """
        return dict(
            moment_format=self.format,
            moment_calendar=self.calendar,
            moment_fromnow=self.from_now,
        )
