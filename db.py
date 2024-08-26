import sqlite3
import click
import flask

def get_db(*args, **kwargs):
    if 'db' not in flask.g:
        flask.g.db = sqlite3.connect(
            './db.db',
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        flask.g.db.row_factory = sqlite3.Row

def close_db(e=None):
    db = flask.g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    get_db()
    with flask.current_app.open_resource('schema.sql') as f:
        flask.g.db.executescript(f.read().decode('utf-8'))

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized db')


def init_app(app):

    with app.app_context():
        flask.current_app.before_request(get_db)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
