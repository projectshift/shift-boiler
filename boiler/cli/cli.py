import click, os
from boiler.cli.colors import *

# -----------------------------------------------------------------------------
# Group setup
# -----------------------------------------------------------------------------


@click.group(help=yellow('Welcome to project console!'))
def cli():
    pass


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------


@cli.command(name='run')
@click.option('--host', '-h', default='0.0.0.0', help='Bind to')
@click.option('--port', '-p', default=5000, help='Listen on port')
@click.option('--reload/--no-reload', default=True, help='Reload on change?')
@click.option('--debug/--no-debug', default=True, help='Use debugger?')
@click.option('--ssl', default=None, help='SSL context')
def run(host='0.0.0.0', port=5000, reload=True, debug=True, ssl=None):
    """ Run development server """
    from werkzeug.serving import run_simple
    from boiler import bootstrap

    # run with ssl context?
    ssl = ssl.lower() if ssl else None
    ssl_context = None
    if ssl == 'adhoc':
        ssl_context = ssl
    elif ssl and ssl.find(','):
        ssl = ssl.split(',')
        ssl_context = (ssl[0], ssl[1])

    app = bootstrap.get_app()
    return run_simple(
        hostname=host,
        port=port,
        application=app,
        use_reloader=reload,
        use_debugger=debug,
        ssl_context=ssl_context
    )


@cli.command(name='shell')
def shell():
    """ Start application-aware shell """
    import importlib
    from boiler import bootstrap

    app = bootstrap.get_app()
    context = dict(app=app)

    # and push app context
    app_context = app.app_context()
    app_context.push()

    # got ipython?
    ipython = importlib.util.find_spec("IPython")

    # run now
    if ipython:
        from IPython import embed
        embed(user_ns=context)
    else:
        import code
        code.interact(local=context)


# -----------------------------------------------------------------------------
# Testing commands
# -----------------------------------------------------------------------------

@cli.command(name='test',context_settings=dict(ignore_unknown_options=True))
@click.argument('nose_argsuments', nargs=-1, type=click.UNPROCESSED)
def test(nose_argsuments):
    """ Run application tests """
    from nose import run

    params = ['__main__', '-c', 'nose.ini']
    params.extend(nose_argsuments)
    run(argv=params)




