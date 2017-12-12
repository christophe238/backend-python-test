from alayatodo import app, db
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash,
    jsonify
    )
from flask_paginate import Pagination, get_page_parameter
from orm import (User, Todo)

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

    user = User.query.filter_by(username=username, password=password).first_or_404()

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
    todo = Todo.query.get_or_404(id=id)
    #TODO: should security check todo.user.id == g.user.id or throw error
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

    per_page = 5
    page = request.args.get(get_page_parameter(), type=int, default=1)

    query = Todo.query.paginate(page, per_page, False)

    pagination = Pagination(page=page, per_page=per_page, total=query.total)

    return render_template('todos.html', todos=query.items, pagination=pagination)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')

    todoDescription = request.form.get('description', '')
    if len(todoDescription) > 0:
        todo = Todo(user=g.user, description=todoDescription)
        db.session.add(todo)
        db.session.commit()
        flash('TODO successfully added', 'success')
    else:
        flash('TODO Description cannot be empty', 'danger')
    return redirect('/todo')

def todo_markdone(id, done):
    if not session.get('logged_in'):
        return redirect('/login')

    todo = Todo.query.get_or_404(id)
    todo.done = done
    db.session.commit()
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
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('TODO successfully removed', 'success')
    return redirect('/todo')
