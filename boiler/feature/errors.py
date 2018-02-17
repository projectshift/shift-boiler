from werkzeug import exceptions as e
from flask import render_template





def errors_feature(app):
    """
    Error pages feature
    Adds custom error pages to flask app
    """
    # create generic exception handler

    # return

    def error_page(exception):
        http_exception = isinstance(exception, e.HTTPException)
        code = exception.code if http_exception else 500
        template = 'errors/{}.j2'.format(code)

        # log exceptions only (app debug should be off)
        if code == 500:
            app.logger.error(exception)

        return render_template(template, error=exception), code

    # attach handler to every exception
    for code in e.default_exceptions.keys():
        # print(code, e.default_exceptions[code])
        app.register_error_handler(code, error_page)




