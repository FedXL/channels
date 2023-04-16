import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

# looks not good, better to have DataBase class with all those methods.
from database_handlers import get_assignment_from_base, get_task_from_base, get_tasks_from_base, \
    delete_task_from_base, add_task, stop_channel, stop_task, start_new_loop, \
    get_user_by_login
from config import SECRET_KEY, host, port
from utils2 import string_to_list
from user_login import UserLogin

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager(app)
process = None
app.permanent_session_lifetime = datetime.timedelta(days=1)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().from_db(user_id)


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = get_user_by_login(request.form['username'])
        if user and check_password_hash(user.password, request.form['password']):
            user_login = UserLogin().create(user)
            login_user(user_login)
            return redirect(url_for('start_page'))
        else:
            return "Mistake"
    return render_template('login.html')

@app.route('/')
@login_required
def start_page():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    tasks = get_assignment_from_base()
    return render_template('main.html', tasks=tasks)


@app.route('/task_list<int:channel>')
@login_required
def task_list(channel):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if channel:
        title = "task"
    else:
        title = "tasks"
    if channel:
        task = get_task_from_base(channel)
        h1 = f"{channel} channel task list:"
    else:
        task = get_tasks_from_base()
        h1 = f"Full task list:"

    time = datetime.datetime.now()
    context = {"title": title,
               "task": task,
               "h1": h1,
               "time": time}

    return render_template('task_list.html', context=context)


@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def task_form():
    if request.method == "POST":
        try:
            channel = int(request.form['channel'])
            working_time = int(request.form['working-time'])
            pause_time = int(request.form['pause-time'])
            subchannels = str(request.form['subchannels'])
            assert isinstance(channel, int)
            assert isinstance(working_time, int)
            assert isinstance(pause_time, int)
            assert isinstance(subchannels, str)
            delete_task_from_base(channel)
            subchannels = string_to_list(subchannels)
            add_task(*subchannels, main_channel=channel, working_time=working_time, pause_time=pause_time)
            return redirect(url_for('task_list', channel=channel))
        except Exception as ER:
            return render_template('error.html', error_message=f"Ошибка {ER} попробуйте ещё", task_form=url_for('task_form'))
    else:
        return render_template('add_task.html')


@app.route('/kill_process<int:channel>')
@login_required
def kill_process(channel):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if channel:
        delete_task_from_base(channel)
        stop_channel(channel)
        return redirect(url_for('start_page'))
    else:
        return redirect(url_for('start_page'))


@app.route('/stop_process<int:channel>')
@login_required
def stop_process(channel):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if channel:
        stop_task(channel)
        stop_channel(channel)
        return redirect(url_for('start_page'))
    else:
        return redirect(url_for('start_page'))


@app.route('/start_process<int:channel>')
@login_required
def start_process(channel):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if channel:
        start_new_loop(channel)
    return redirect(url_for('start_page'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host=host, port=port,debug=True)