import datetime
import time
from sqlalchemy.orm import Session
from database_handlers import start_channel, stop_channel, start_new_loop, start_subchannel
from engine_and_models import engine, Tasks


def execute_command(task: Tasks):
    match task.command:
        case "start_subchannel":
            print(task, "start_subchannel")
            start_subchannel(task.channel, task.subchannel)
        case "start_channel":
            print(task, "start_channel")
            start_channel(task.channel)
        case "stop_channel":
            print(task, "stop_channel")
            stop_channel(task.channel)
        case "start_again":
            print(task, "start_again")
            start_new_loop(task.channel)


def get_tasks_within_one_second():
    while True:
        with Session(engine) as session:
            current_time = datetime.datetime.now()
            one_second_ago = current_time - datetime.timedelta(minutes=1)  # делта по времени для зацепления задачи
            tasks = session.query(Tasks).filter(Tasks.time.between(one_second_ago, current_time)).all()
            print(current_time)
            for task in tasks:
                execute_command(task)
                session.delete(task)
            session.commit()
        time.sleep(1)


if __name__ == "__main__":
    get_tasks_within_one_second()
