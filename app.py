import json
import secrets
import flask
import flask_cors
import db


app = flask.Flask(__file__)

with open('./.secrets.json') as f:
    SECRETS = json.loads(f.read().strip())

db.init_app(app)
flask_cors.CORS(app, origins=SECRETS['domains'])


@app.before_request
def authorization():
    if flask.request.method.upper() != 'OPTIONS' and isinstance(flask.request.headers.get('Authorization'), str) and not secrets.compare_digest(flask.request.headers.get('Authorization'), f'Basic {SECRETS['data']}'):
        flask.abort(403)


@app.get('/')
def list():
    return [{k: e[k] for k in e.keys()} for e in flask.g.db.execute('select * from entry where hide = 0 order by created desc;')]

@app.post('/')
def add():
    cursor = flask.g.db.cursor()
    cursor.execute(
        'insert into entry (text, author, colour) values (?, ?, ?)', (
            flask.request.form.get('text'),
            flask.request.form.get('author') or 'anonymous',
            flask.request.form.get('colour') or '000000',
        )
    )
    cursor.connection.commit()
    return str(cursor.lastrowid)

@app.get('/edit/<id>')
def entry(id):
    if (entry := flask.g.db.execute('select * from entry where id = ?', (id,)).fetchone()) is not None:
        return {k: entry[k] for k in entry.keys()}
    flask.abort(404)

@app.put('/edit/<id>')
def edit(id):
    if (entry := flask.g.db.execute('select * from entry where id = ?', (id,)).fetchone()) is not None:
        flask.g.db.execute('update entry set text = ?, author = ?, colour = ? where id = ?', (
            flask.request.form.get('text'),
            flask.request.form.get('author') or 'anonymous',
            flask.request.form.get('colour') or '000000',
            id
        ))
        flask.g.db.commit()
        return ''
    flask.abort(404)
