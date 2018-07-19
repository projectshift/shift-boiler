from flask import render_template


def home():
    """
    Home action
    Displays project homepage
    :return: string
    """
    return render_template('index/home.j2')





