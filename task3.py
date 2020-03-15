import socket
import time
from datetime import datetime
import random

logfile = './log.log'
# Используем систему мониторинга Graphite
# она позволит отправлять по UDP метрики
# не блокируя выполнение кода в сервисе
CARBON_SERVER = '192.168.0.1'
CARBON_PORT = 100


# декоратор замеряющий время выполнения функции
def timing_record(name):
    def inner(func):
        def wrapper(*argsf, **kwargsf):

            start_time = time.time()
            rc = func(*argsf, **kwargsf)  # ВЫПОЛНЕНИЕ
            end_time = time.time()
            timing_ms = int((end_time - start_time) * 1000)

            message = '%s %d %d\n' % (name, timing_ms, end_time)

            try:
                # отправляем неблокирующее UDP соединение
                # оно не будет мешать программе
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(bytes(message, "utf-8"), (CARBON_SERVER, CARBON_PORT))
            except Exception:
                # не мешать работе кода, если ошибки в передаче метрики
                # ошибка автоматом обнаружится в Graphite,
                # когда перестанут приходить значения метрик
                pass

            return rc

        return wrapper

    return inner


# функция которую нужно измерить
@timing_record(name="FOO")
def func_to_check(param):
    delay = random.randint(100, 2000)
    time.sleep(delay / 1000)
    return True


# главная функция приложения, из которой вызываются остальные
def main(param):
    return func_to_check(param=param)


#===========

if __name__ == '__main__':
    # эмулируем параллельный, многократный запуск скрипта
    import multiprocessing as mp
    pool = mp.Pool(100)

    #прогон на 1000 запусков
    params = list(range(1000))
    pool.map(main, params)
