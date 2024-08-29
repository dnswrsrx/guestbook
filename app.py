import json
import secrets
import flask
import flask_cors
import db


app = flask.Flask(__file__)

with open('./.secrets.json') as f:
    SECRETS = json.loads(f.read().strip())
 
db.init_app(app)
flask_cors.CORS(app,
                origins=SECRETS['domains'],
                methods=['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT'],
                resources=[r'/', r'/edit/*'])


@app.before_request
def authorization():
    if flask.request.method.upper() != 'OPTIONS' and isinstance(flask.request.headers.get('Authorization'), str) and not secrets.compare_digest(flask.request.headers.get('Authorization'), f'Basic {SECRETS['data']}'):
        flask.abort(403)


@app.get('/')
def list():
    return [{k: e[k] for k in e.keys()} for e in flask.g.db.execute('select author, colour, created, hide, id, text from entry where hide=false and admin_hide=false order by created desc;')]

@app.post('/')
def add():
    if flask.request.form.get('text') and flask.request.form.get('author'):
        cursor = flask.g.db.cursor()
        cursor.execute(
            'insert into entry (text, author, colour) values (?, ?, ?)', (
                flask.request.form.get('text'),
                flask.request.form.get('author'),
                flask.request.form.get('colour', ''),
            )
        )
        cursor.connection.commit()
        return str(cursor.lastrowid), 201
    return flask.abort(400)


@app.get('/edit/<id>')
def entry(id):
    if (entry := flask.g.db.execute('select * from entry where id=?', (id,)).fetchone()) is not None:
        return {k: entry[k] for k in entry.keys()}
    flask.abort(404)

@app.put('/edit/<id>')
def edit(id):
    if (entry := flask.g.db.execute('select * from entry where id=?', (id,)).fetchone()) is not None:
        flask.g.db.execute('update entry set text=?, author=?, colour=?, hide=? where id=?', (
            flask.request.form.get('text', ''),
            flask.request.form.get('author', ''),
            flask.request.form.get('colour', ''),
            not (flask.request.form.get('text') and flask.request.form.get('author')),
            id
        ))
        flask.g.db.commit()
        return '', 204
    flask.abort(404)


@app.route('/admin-listing', methods=('GET', 'POST'))
def admin_listing():
    if flask.request.method == 'POST':
        if flask.request.form.get('id'):
            entry_id, admin_hide = flask.g.db.execute('select id, admin_hide from entry where id=?', (flask.request.form.get('id'),)).fetchone()
            flask.g.db.execute('update entry set admin_hide=? where id=?', (not admin_hide, entry_id))
            flask.g.db.commit()

            return flask.redirect(flask.request.path)

    entries = ({k: e[k] for k in e.keys()} for e in flask.g.db.execute('select * from entry order by created desc;'))
    return flask.render_template('admin_listing.html', entries=entries)
