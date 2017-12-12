from alayatodo import app
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash,
    jsonify
    )


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


def render_todo(id, json=False):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    if json:
        return jsonify(dict(todo))
    return render_template('todo.html', todo=todo)

@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    return render_todo(id)

@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    return render_todo(id, json=True)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos")
    todos = cur.fetchall()
    return render_template('todos.html', todos=todos)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')

    todoDescription = request.form.get('description', '')
    if len(todoDescription) > 0:
        #TODO: Not so safe... Need to checkk how to prevent SQL injection in python
        g.db.execute(
            "INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"
            % (session['user']['id'], request.form.get('description', ''))
        )
        g.db.commit()
    else:
        flash('TODO Description cannot be empty','error')
    return redirect('/todo')

def todo_markdone(id, done):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("UPDATE todos SET done = '%s' WHERE id ='%s'" % (done, id))
    g.db.commit()
    return redirect('/todo')

@app.route('/todo/done/<id>', methods=['POST'])
def todo_done(id):
    return todo_markdone(id, 1)

@app.route('/todo/undo/<id>', methods=['POST'])
def todo_undo(id):
    return todo_markdone(id, 0)

@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
    g.db.commit()
    return redirect('/todo')
