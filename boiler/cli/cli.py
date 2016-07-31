import click, os, sys, shutil
from boiler.cli.colors import *
from click import echo


# -----------------------------------------------------------------------------
# Group setup
# -----------------------------------------------------------------------------


@click.group(help=yellow('Welcome to project console!'))
def cli():
    pass


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------

@cli.command(name='init')
@click.argument('destination', type=click.Path(exists=True))
@click.option('--force', '-f',
    default=False,
    is_flag=True,
    help='Skip existing objects in destination'
)
@click.option('--skip', '-s',
    default=False,
    is_flag=True,
    help='Skip existing objects in dstination'
)
def init(destination, force=False, skip=True):
    """ Initialise new project """
    import os
    ignores = ['.DS_Store', '__pycache__']

    echo(green('\nInitialise project:'))
    echo(green('-' * 40))

    destination = os.path.realpath(destination)
    source = os.path.realpath(os.path.dirname(__file__) + '/../boiler_template')




    # dry run first
    exist_in_dst = []
    for path, dirs, files in os.walk(source):
        for dir in dirs:
            if dir in ignores:
                continue
            dst = os.path.join(path, dir).replace(source, destination)
            if os.path.exists(dst):
                exist_in_dst.append(dst)

        for file in files:
            if file in ignores:
                continue
            dst = os.path.join(path, file).replace(source, destination)
            if os.path.exists(dst):
                exist_in_dst.append(dst)

    # require force option if existing files found
    if exist_in_dst and not force and not skip:

        msg = 'The following objects were found in destination.'
        msg += 'What do you want to do with these?'
        echo(red(msg))
        echo(red('Use either --force or --skip option \n'))

        for index,path in enumerate(exist_in_dst):
            print(yellow('{}. {}'.format(index, path)))

        echo()
        return

    for path, dirs, files in os.walk(source):
        for dir in dirs:
            if dir in ignores:
                continue
            src = os.path.join(path, dir)
            dst = src.replace(source, destination)
            if dst in exist_in_dst and force:
                print(red('OVERWRITING: ' + dst))
                if os.path.exists(dst):
                    shutil.rmtree(dst, ignore_errors=True)
                os.makedirs(dst)
            elif dst in exist_in_dst and skip:
                print(yellow('SKIPPING: ' + dst))
            else:
                print('CREATING: ' + dst)
                os.makedirs(dst)

        for file in files:
            if file in ignores:
                continue
            src = os.path.join(path, file)
            dst = src.replace(source, destination)
            if dst in exist_in_dst and force:
                print(red('OVERWRITING: ' + dst))
                if os.path.exists(dst):
                    os.remove(dst)
                shutil.copy(src, dst)
            elif dst in exist_in_dst and skip:
                print(yellow('SKIPPING: ' + dst))
            else:
                print('CREATING: ' + dst)
                shutil.copy(src, dst)

    echo()
    return



@cli.command(name='run')
@click.option('--host', '-h', default='0.0.0.0', help='Bind to')
@click.option('--port', '-p', default=5000, help='Listen on port')
@click.option('--reload/--no-reload', default=True, help='Reload on change?')
@click.option('--debug/--no-debug', default=True, help='Use debugger?')
def run(host='0.0.0.0', port=5000, reload=True, debug=True):
    """ Run development server """
    from werkzeug.serving import run_simple
    from boiler.bootstrap import create_middleware
    from config.config import DevConfig

    app = create_middleware(config=DevConfig())
    return run_simple(
        hostname=host,
        port=port,
        application=app,
        use_reloader=reload,
        use_debugger=debug,
    )


@cli.command(name='shell')
def shell():
    """ Start application-aware shell """
    context = dict()

    # mount apps
    from boiler.bootstrap import create_middleware
    middleware = create_middleware()
    context['apps'] = dict(frontend=middleware.app)
    for mount in middleware.mounts:
        context['apps'][mount] = middleware.mounts[mount]

    # and push app context
    app_context = middleware.app.app_context()
    app_context.push()

    # and run
    try:
        from IPython import embed
        embed(user_ns=context)
    except ImportError:
        import code
        code.interact(local=context)


# -----------------------------------------------------------------------------
# Testing commands
# -----------------------------------------------------------------------------

# @todo: how can we intercept these args
nose_argv = None
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    nose_argv = sys.argv[2:]
    sys.argv = sys.argv[:2]


@cli.command(name='test')
def test():
    """ Run application tests """
    from nose import run
    params = ['__main__', '-c', 'nose.ini']
    params.extend(nose_argv)
    run(argv=params)




