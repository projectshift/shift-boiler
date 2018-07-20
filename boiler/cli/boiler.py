import click, os, sys, shutil
from boiler.cli.colors import *
from click import echo
from boiler.version import version as boiler_version

# -----------------------------------------------------------------------------
# Group setup
# -----------------------------------------------------------------------------


@click.group(help=yellow('Boiler project tools'))
def cli():
    pass


# -----------------------------------------------------------------------------
# Show version number
# -----------------------------------------------------------------------------

@cli.command(name='version', help='Display current boiler version')
def version():
    """
    Version
    Imports and displays current boiler version.
    :return:
    """
    echo(green('\nshift-boiler:'))
    echo(green('-' * 40))
    echo(yellow('Version: ') + '{}'.format(boiler_version))
    echo(yellow('GitHub: ') + 'https://github.com/projectshift/shift-boiler')
    echo(yellow('PyPi: ') + 'https://pypi.org/project/shiftboiler/')
    echo()


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
    help='Skip existing objects in destination'
)
def init(destination, force=False, skip=True):
    """ Initialise new project """
    import os
    from uuid import uuid1
    import fileinput

    ignores = ['.DS_Store', '__pycache__', ]

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
            echo(yellow('{}. {}'.format(index, path)))

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
                echo(red('OVERWRITING: ' + dst))
                if os.path.exists(dst):
                    shutil.rmtree(dst, ignore_errors=True)
                os.makedirs(dst)
            elif dst in exist_in_dst and skip:
                echo(yellow('SKIPPING: ' + dst))
            else:
                echo('CREATING: ' + dst)
                os.makedirs(dst)

        for file in files:
            if file in ignores:
                continue
            src = os.path.join(path, file)
            dst = src.replace(source, destination)
            if('__pycache__' in src):
                continue

            if dst in exist_in_dst and force:
                echo(red('OVERWRITING: ' + dst))
                if os.path.exists(dst):
                    os.remove(dst)
                shutil.copy(src, dst)
            elif dst in exist_in_dst and skip:
                echo(yellow('SKIPPING: ' + dst))
            else:
                echo('CREATING: ' + dst)
                shutil.copy(src, dst)

    # create secret keys
    path = os.path.join(os.getcwd(), 'dist.env')
    secrets = ['USER_JWT_SECRET', 'SECRET_KEY']
    for line in fileinput.input(path, inplace=True):
        line = line.strip('\n')
        found = False
        for secret in secrets:
            if secret in line:
                found = True
                break

        if not found:
            echo(line)
        else:
            echo(line.replace('SET_ME', '\'' + str(uuid1()) + '\''))

    # create .env
    dotenv_dist = os.path.join(os.getcwd(), 'dist.env')
    dotenv = os.path.join(os.getcwd(), '.env')

    if not os.path.isfile(dotenv):
        shutil.copy(dotenv_dist, dotenv)

    # rename gitignore
    ignore_src = os.path.join(os.getcwd(), 'dist.gitignore')
    ignore_dst = os.path.join(os.getcwd(), '.gitignore')
    if os.path.isfile(ignore_src) and not os.path.exists(ignore_dst):
        shutil.move(ignore_src, ignore_dst)

    # create requirements file
    reqs = os.path.join(os.getcwd(), 'requirements.txt')
    if not os.path.exists(reqs):
        with open(reqs, 'a') as file:
            file.write('shiftboiler=={}\n'.format(boiler_version))


    echo()
    return


# -----------------------------------------------------------------------------
# Install feature dependencies
# -----------------------------------------------------------------------------

@cli.command(name='dependencies')
@click.argument('feature', default=None, required=False)
def install_dependencies(feature=None):
    """ Install dependencies for a feature """
    import subprocess

    echo(green('\nInstall dependencies:'))
    echo(green('-' * 40))

    req_path = os.path.realpath(os.path.dirname(__file__) + '/../_requirements')

    # list all features if no feature name
    if not feature:
        echo(yellow('Please specify a feature to install. \n'))
        for index, item in enumerate(os.listdir(req_path)):
            item = item.replace('.txt', '')
            echo(green('{}. {}'.format(index + 1, item)))

        echo()
        return

    # install if got feature name
    feature_file = feature.lower() + '.txt'
    feature_reqs = os.path.join(req_path, feature_file)

    # check existence
    if not os.path.isfile(feature_reqs):
        msg = 'Unable to locate feature requirements file [{}]'
        echo(red(msg.format(feature_file)) + '\n')
        return

    msg = 'Now installing dependencies for "{}" feature...'.format(feature)
    echo(yellow(msg))

    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', '-r', feature_reqs]
    )

    # update requirements file with dependencies
    reqs = os.path.join(os.getcwd(), 'requirements.txt')
    if os.path.exists(reqs):
        with open(reqs) as file:
            existing = [x.strip().split('==')[0] for x in file.readlines() if x]

        lines = ['\n']
        with open(feature_reqs) as file:
            incoming = file.readlines()

            for line in incoming:
                if not(len(line)) or line.startswith('#'):
                    lines.append(line)
                    continue

                package = line.strip().split('==')[0]
                if package not in existing:
                    lines.append(line)

        with open(reqs, 'a') as file:
            file.writelines(lines)

    echo(green('DONE\n'))


