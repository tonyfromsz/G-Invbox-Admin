# -*- coding:utf-8 *-*

import os

from app import setup_app
from flask_script import Manager, Shell


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = setup_app()
manager = Manager(app)


def make_shell_context():
    return dict(app=app)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def create_user(type):
    pass


if __name__ == '__main__':
    manager.run()
