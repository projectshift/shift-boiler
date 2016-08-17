from werkzeug import exceptions as e


def error_pages_feature(app):
    """
    Error pages feature
    Adds custom error pages to flask app
    """
    from flask import render_template

    # create generic exception handler
    def error_page(exception):
        http_exception = isinstance(exception, e.HTTPException)
        code = exception.code if http_exception else 500
        template = 'errors/{}.html'.format(code)

        # log exceptions only (app debug should be off)
        if code == 500:
            app.logger.error(exception)

        return render_template(template, error=exception), code

    # attach handler to every exception
    for code in e.default_exceptions.keys():
        app.register_error_handler(code, error_page)




