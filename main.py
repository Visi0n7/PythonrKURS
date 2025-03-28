import threading
import queue
import time
import random

# Определение класса задачи
class Task:
    def __init__(self, task_id, duration):
        self.task_id = task_id
        self.duration = duration

    def execute(self):
        print(f"Задача {self.task_id} начинается. Оценочная длительность: {self.duration} секунд(ы)")
        time.sleep(self.duration)
        print(f"Задача {self.task_id} завершена.")

# Определение класса процессора
class Processor(threading.Thread):
    def __init__(self, processor_id, task_queue):
        super().__init__()
        self.processor_id = processor_id
        self.task_queue = task_queue

    def run(self):
        while True:
            try:
                task = self.task_queue.get(timeout=1)  # Ожидание задачи
                print(f"Процессор {self.processor_id} взял задачу {task.task_id}.")
                task.execute()
                self.task_queue.task_done()
            except queue.Empty:
                print(f"Процессор {self.processor_id} завершил работу.")
                break

# Основная функция программы
def main():
    num_processors = 2  # Уменьшено количество процессоров, чтобы избежать ограничений на потоки
    num_tasks = 10  # Количество задач

    # Создание общей очереди задач
    task_queue = queue.Queue()

    # Генерация случайных задач
    for i in range(1, num_tasks + 1):
        task_duration = random.randint(1, 5)  # Случайная длительность от 1 до 5 секунд
        task_queue.put(Task(task_id=i, duration=task_duration))

    # Создание и запуск процессоров
    processors = []
    for i in range(1, num_processors + 1):
        processor = Processor(processor_id=i, task_queue=task_queue)
        processors.append(processor)
        processor.start()

    # Ожидание завершения всех задач
    task_queue.join()

    # Ожидание завершения работы всех процессоров
    for processor in processors:
        processor.join()

    print("Все задачи были успешно обработаны.")

# Точка входа в программу
if __name__ == "__main__":
    main()
