from click import style


def colour(colour, message, bold=False):
    """ Color a message """
    return style(fg=colour, text=message, bold=bold)


def yellow(message, bold=False):
    """ Color in yellow """
    return colour('yellow', message, bold)


def red(message, bold=False):
    """ Color in red """
    return colour('red', message, bold)


def green(message, bold=False):
    """ Color in green """
    return colour('green', message, bold)


def blue(message, bold=False):
    """ Color in blue """
    return colour('blue', message, bold)


def magenta(message, bold=False):
    """ Color in magenta """
    return colour('magenta', message, bold)


def cyan(message, bold=False):
    """ Color in cyan """
    return colour('cyan', message, bold)


def white(message, bold=False):
    """ Color in white """
    return colour('white', message, bold)
