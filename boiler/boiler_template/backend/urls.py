from boiler.routes.route import route
"""
A note on URLs: please define your URLS with a trailing slash (unless it has
an extension of course)! This way they will work both with and without trailing
slash. If it's missing - Flask will just add it.

"""

urls = dict()
urls['/'] = route('backend.views.home', 'home')




