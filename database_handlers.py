import datetime
import random
from sqlalchemy.orm import Session
from engine_and_models import engine, Tasks, engine_server_1, Prov, Goip, engine_server_2, Assignment, User
from config import test_mode
from utils2 import turn_1_to_0001


def start_channel(channel):
    channel = turn_1_to_0001(channel)
    with Session(engine_server_1) as session:
        session.query(Goip).filter(Goip.prefix == channel).update({Goip.sost: 0})
        session.commit()


def stop_channel(channel):
    channel = turn_1_to_0001(channel)
    with Session(engine_server_1) as session:
        print(channel)
        session.query(Goip).filter(Goip.prefix == channel).update({Goip.sost: 2})
        session.commit()


def start_subchannel(channel, subchannel):
    print(channel, subchannel)
    channel = turn_1_to_0001(channel)
    with Session(engine_server_2) as session:
        session.query(Prov).filter(Prov.prefix == channel).update(
            {Prov.minsim: subchannel, Prov.maxsim: subchannel})
        session.commit()


def start_new_loop(channel):
    print(channel)
    with Session(engine) as session:
        new_tasks = session.query(Assignment).filter_by(channel=channel).one_or_none()
        task_to_delete = session.query(Assignment).filter_by(channel=channel).one_or_none()
        if task_to_delete is not None:
            session.delete(task_to_delete)
            session.commit()
        subchannels = str(new_tasks.subchannel)
        subchannels = subchannels.strip('[]').split(",")
        subchannels = [int(x.strip()) for x in subchannels]
        add_task(*subchannels, main_channel=new_tasks.channel, working_time=new_tasks.working_time,
                 pause_time=new_tasks.pause_time)


def create_task_queue(*args, main_channel,
                      working_time: int,
                      pause_time: int,
                      ):
    # Сохраняем полностью задание в базу . При start_again именно от туда будут вытаскиваться параметры микрозадач для запуска цикла ещё раз.
    insert_assignment_to_base(*args, main_channel=main_channel, working_time=working_time, pause_time=pause_time)

    if test_mode:
        pause_time_delta = datetime.timedelta(seconds=pause_time)
        working_interval = datetime.timedelta(seconds=working_time)
    else:
        pause_time_delta = datetime.timedelta(minutes=pause_time)
        working_interval = datetime.timedelta(minutes=working_time)

    task = []
    time = datetime.datetime.now()

    sleeping_interval = pause_time_delta - (len(args) - 1) * working_interval

    # Старт канал включаем субканал потом основной канал
    task.append(("start_subchannel", main_channel, args[0], time))
    task.append(("start_channel", main_channel, None, time))

    # Подключаем по очередно все каналы через интервал
    for subchannel in args[1:]:
        time = time + working_interval
        task.append(("start_subchannel", main_channel, subchannel, time))
    time = time + working_interval
    # Каналы отработали, думаем чё делать дальше либо организовывать паузу либо

    if sleeping_interval <= datetime.timedelta(0):
        print("with_dont_stop_channel")
    else:
        task.append(("stop_channel", main_channel, None, time))
        time = time + sleeping_interval
    # Добавляем команду повторить цикл после в конце. После паузы или без паузы.

    task.append(("start_again", main_channel, None, time))
    return tuple(task)


def insert_task_to_base(assignment):
    """subfunction to add task"""
    with Session(engine) as session:
        for task, channel, subchannel, time in assignment:
            new_task = Tasks(command=task, channel=channel, subchannel=subchannel, time=time)

            session.add(new_task)
        session.commit()


def insert_assignment_to_base(*args, main_channel, working_time, pause_time):
    """subfunction to add assignment"""
    with Session(engine) as session:
        subchannels = str([*args])
        new_assignment = Assignment(channel=main_channel, working_time=working_time, pause_time=pause_time,
                                    subchannel=subchannels, in_work=True)
        session.add(new_assignment)
        session.commit()


def add_task(*args, main_channel: int, working_time: int, pause_time: int):
    """use this function to add task in sistem"""
    stmt = create_task_queue(*args, main_channel=main_channel, working_time=working_time, pause_time=pause_time)
    insert_task_to_base(stmt)


def multitask():
    """тестовая функция для наполнения тестовой базы данных """
    for i in range(1, 121):
        n = random.randint(1, 30)  # Случайное количество чисел от 1 до 10
        channel = turn_1_to_0001(i)
        subchannels = [random.randint(1, 30) for _ in range(n)]
        working_time = random.randint(10, 50)
        pause_time = working_time * (len(subchannels) + 2)
        add_task(*subchannels, main_channel=channel, working_time=working_time, pause_time=pause_time)


def get_assignment_from_base():
    with Session(engine) as session:
        assignments = session.query(Assignment).order_by(Assignment.channel).all()
        return assignments


def get_task_from_base(channel):
    with Session(engine) as session:
        task = session.query(Tasks).filter(Tasks.channel == channel).all()
        return task


def get_tasks_from_base():
    with Session(engine) as session:
        tasks = session.query(Tasks).order_by(Tasks.time).all()
        return tasks


def delete_task_from_base(channel):
    """соответственно удаляет и задачи и таски"""
    with Session(engine) as session:
        tasks = session.query(Tasks).filter(Tasks.channel == channel).all()
        for task in tasks:
            session.delete(task)
        session.commit()
        assignment = session.query(Assignment).filter(Assignment.channel == channel).all()
        for assign in assignment:
            session.delete(assign)
        session.commit()


def stop_task(channel):
    """Удаляет только таски а задачу оставляет"""
    with Session(engine) as session:
        tasks = session.query(Tasks).filter(Tasks.channel == channel).all()
        for task in tasks:
            session.delete(task)
        assignment = session.query(Assignment).filter(Assignment.channel == channel).one()
        assignment.in_work = False
        session.commit()


def stop_all_tasks():
    with Session(engine) as session:
        tasks = session.query(Tasks).all()
        for task in tasks:
            session.delete(task)
        session.commit()


def clean_database():
    with Session(engine) as session:
        session.query(Tasks).delete()
        session.query(Assignment).delete()
        session.commit()


def get_user_by_id(user_id):
    with Session(engine) as session:
        user = session.query(User).filter(User.id == user_id).one()
        if user:
            return user
        else:
            return False


def get_user_by_login(login):
    with Session(engine) as session:
        user = session.query(User).filter(User.username == login).one()
        if user:
            return user
        else:
            return False
