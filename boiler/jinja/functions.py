from flask import current_app as app, has_request_context, request

def asset(url = None):
    """
    Asset helper
    Generates path to a static asset based on configuration base path and
    support for versioning. Will easily allow you to move your assets away to
    a CDN without changing templates. Versioning allows you to cache your asset
    changes forever by the webserver.

    :param url: string - relative path to asset
    :return: string - full versioned url
    """

    # fallback to url_for('static') if assets path not configured
    url = url.lstrip('/')
    assets_path = app.config.get('ASSETS_PATH')
    if not assets_path:
        url_for = app.jinja_env.globals.get('url_for')
        url = url_for('static', filename=url)
    else:
        assets_path = assets_path.rstrip('/')
        url = assets_path + '/' + url

    version = app.config.get('ASSETS_VERSION')
    if not version:
        return url

    sign = '?'
    if sign in url:
        sign = '&'

    pattern = '{url}{sign}v{version}'
    return pattern.format(url=url, sign=sign, version=version)

def dev_proxy():
    """
    Is dev proxy?
    A boolean method to check if we are in development proxy mode. Dev proxy
    mode is detected by the presence of request header that you dev proxy
    server should append to request.
    :return:
    """
    if not has_request_context():
        return False

    header = app.config.get('DEV_PROXY_HEADER')
    if not header:
        return False

    return bool(request.headers.get(header))
