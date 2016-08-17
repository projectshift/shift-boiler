import click, os, sys, shutil
from boiler.cli.colors import *
from click import echo


# -----------------------------------------------------------------------------
# Group setup
# -----------------------------------------------------------------------------


@click.group(help=yellow('Boiler project tools'))
def cli():
    pass


# -----------------------------------------------------------------------------
# Sign python
# -----------------------------------------------------------------------------


@cli.command(name='sign-python', help='Sign python executable')
def sign_python():
    """
    Sign python (MacOS)
    Signing your python interpreter using self-signed certificate is used to
    get rid of annoying firewall questions about whether to allow incoming
    connections to the interpreter that happen on each app restart. This only
    makes sense on Mac. In order to use this command you must first create
    a certificate to sign your code with. To do it:

      1. Open Keychain Access
      2. Choose: Keychain Access > Certificate Assistant > Create Certificate
      3. Important: Use your current username for certificate name (id -un)
      4. Select Certificate Type: Code Signing
      5. Select Type: Self Signed Root
      6. Check 'Let me override defaults' box
      7. Click Continue, and give it a serial number (maximum randomness)
      8. Accept defaults for the rest

    You will only need to do this once. After this is done you can use
    generated certificate to sign your Python in any project.
    """
    from subprocess import check_output
    from os import system

    echo(green('\nSign python:'))
    echo(green('-' * 40))

    # get python
    python = check_output(['which', 'python']).decode().replace('\n', '')
    echo('Interpreter: ' + yellow(python))

    # get certificate name
    username = check_output(['id', '-un']).decode().replace('\n', '')
    echo('Using certificate: ' + yellow(username) + '\n')

    # signing
    cert = '"{}"'.format(username)
    cmd = "codesign -s {cert} -f {python}".format(cert=cert, python=python)
    system(cmd)

    echo(green('\nDONE\n'))


# -----------------------------------------------------------------------------
# Init project
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
            if('__pycache__' in src):
                continue

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
            if('__pycache__' in src):
                continue

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





