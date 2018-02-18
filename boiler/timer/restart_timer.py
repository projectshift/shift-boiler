import os
from datetime import datetime
from click import style


def time_restarts(data_path):
    """ When called will create a file and measure its mtime on restarts """
    path = os.path.join(data_path, 'last_restarted')
    if not os.path.isfile(path):
        with open(path, 'a'):
            os.utime(path, None)

    last_modified = os.stat(path).st_mtime

    with open(path, 'a'):
        os.utime(path, None)

    now = os.stat(path).st_mtime
    dif = round(now - last_modified, 2)
    last_restart = datetime.fromtimestamp(now).strftime('%H:%M:%S')
    result = 'LAST RESTART WAS {} SECONDS AGO at {}'.format(dif, last_restart)
    print(style(fg='green', bg='red', text=result))