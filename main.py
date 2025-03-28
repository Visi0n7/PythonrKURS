import threading
import queue
import time
import random
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Определение класса задачи
class Task:
    def __init__(self, task_id, duration):
        self.task_id = task_id
        self.duration = duration

# Определение класса процессора
class Processor(threading.Thread):
    def __init__(self, processor_id, task_queue, log_area, update_gui_callback, update_chart_callback, stats_callback):
        super().__init__()
        self.processor_id = processor_id
        self.task_queue = task_queue
        self.log_area = log_area
        self.update_gui_callback = update_gui_callback
        self.update_chart_callback = update_chart_callback
        self.stats_callback = stats_callback
        self.tasks_completed = 0
        self.idle_time = 0

    def run(self):
        while True:
            try:
                task = self.task_queue.get(timeout=1)
                self.log_area.insert(tk.END, f"Процессор {self.processor_id} начал выполнение задачи {task.task_id} (время: {task.duration} сек)\n")
                self.update_gui_callback(self.processor_id, f"Выполняется задача {task.task_id}")
                self.update_chart_callback(self.processor_id - 1, task.duration)
                time.sleep(task.duration)
                self.log_area.insert(tk.END, f"Процессор {self.processor_id} завершил задачу {task.task_id}\n")
                self.update_gui_callback(self.processor_id, "Ожидание задачи")
                self.task_queue.task_done()
                self.tasks_completed += 1
                self.stats_callback(self.processor_id, task.duration, False)
            except queue.Empty:
                self.idle_time += 1
                self.log_area.insert(tk.END, f"Процессор {self.processor_id} завершил работу\n")
                self.update_gui_callback(self.processor_id, "Завершил работу")
                self.stats_callback(self.processor_id, self.idle_time, True)
                break

# Основной класс приложения
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Симуляция обработки данных")
        self.task_queue = queue.Queue()

        # Конфигурируемые параметры
        self.num_processors = 3
        self.num_tasks = 10
        self.max_task_duration = 5  # Максимальное время задачи (сек)

        # Инициализация данных для диаграммы
        self.processor_durations = [0] * self.num_processors  # Время выполнения каждого процессора
        self.processor_stats = {"completed": [0] * self.num_processors, "idle": [0] * self.num_processors, "total_duration": 0}

        # Создание GUI
        self.create_widgets()

    def create_widgets(self):
        # Лог-область
        self.log_area = tk.Text(self.root, height=15, width=50, state=tk.DISABLED)
        self.log_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Панель процессоров
        self.processor_frame = tk.Frame(self.root)
        self.processor_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        self.processor_labels = []
        for i in range(1, self.num_processors + 1):
            label = ttk.Label(self.processor_frame, text=f"Процессор {i}: Ожидание задачи", relief=tk.SUNKEN, width=40)
            label.grid(row=i, column=0, padx=5, pady=5)
            self.processor_labels.append(label)

        # Диаграмма выполнения
        self.figure, self.ax = plt.subplots(figsize=(5, 3))
        self.bar_chart = self.ax.bar(
            range(1, self.num_processors + 1),
            self.processor_durations,
            tick_label=[f"Проц {i}" for i in range(1, self.num_processors + 1)],
        )
        self.ax.set_title("Загрузка процессоров (время работы)")
        self.ax.set_xlabel("Процессоры")
        self.ax.set_ylabel("Время выполнения (сек)")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Конфигурируемые параметры
        self.num_processors_label = ttk.Label(self.root, text="Количество процессоров:")
        self.num_processors_label.grid(row=3, column=0, padx=5, pady=5)

        self.num_processors_entry = ttk.Entry(self.root)
        self.num_processors_entry.insert(0, str(self.num_processors))
        self.num_processors_entry.grid(row=3, column=1, padx=5, pady=5)

        self.num_tasks_label = ttk.Label(self.root, text="Количество задач:")
        self.num_tasks_label.grid(row=4, column=0, padx=5, pady=5)

        self.num_tasks_entry = ttk.Entry(self.root)
        self.num_tasks_entry.insert(0, str(self.num_tasks))
        self.num_tasks_entry.grid(row=4, column=1, padx=5, pady=5)

        self.max_task_duration_label = ttk.Label(self.root, text="Максимальная продолжительность задачи (сек):")
        self.max_task_duration_label.grid(row=5, column=0, padx=5, pady=5)

        self.max_task_duration_entry = ttk.Entry(self.root)
        self.max_task_duration_entry.insert(0, str(self.max_task_duration))
        self.max_task_duration_entry.grid(row=5, column=1, padx=5, pady=5)

        # Кнопки управления
        self.start_button = ttk.Button(self.root, text="Запустить", command=self.start_simulation)
        self.start_button.grid(row=6, column=0, padx=10, pady=10)

        self.exit_button = ttk.Button(self.root, text="Выход", command=self.root.quit)
        self.exit_button.grid(row=6, column=1, padx=10, pady=10)

        # Панель статистики
        self.stats_label = ttk.Label(self.root, text="Статистика:")
        self.stats_label.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        self.stats_text = tk.Text(self.root, height=10, width=50, state=tk.DISABLED)
        self.stats_text.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    def update_gui(self, processor_id, status):
        self.processor_labels[processor_id - 1].config(text=f"Процессор {processor_id}: {status}")
        self.root.update_idletasks()

    def update_chart(self, processor_index, task_duration):
        # Увеличиваем общее время выполнения для процессора
        self.processor_durations[processor_index] += task_duration
        # Обновляем диаграмму
        for bar, new_height in zip(self.bar_chart, self.processor_durations):
            bar.set_height(new_height)
        self.ax.set_ylim(0, max(self.processor_durations) + 1)  # Автоматическое масштабирование оси Y
        self.canvas.draw_idle()

    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message)
        self.log_area.config(state=tk.DISABLED)
        self.log_area.see(tk.END)

    def stats_message(self, processor_id, duration, is_idle):
        if is_idle:
            self.processor_stats["idle"][processor_id - 1] = duration
        else:
            self.processor_stats["total_duration"] += duration
            self.processor_stats["completed"][processor_id - 1] += 1
        self.update_stats_display()

    def update_stats_display(self):
        # Обновление статистики
        stats_message = f"Общее время работы: {self.processor_stats['total_duration']} сек\n"
        for i in range(self.num_processors):
            stats_message += f"Процессор {i + 1} - Завершено задач: {self.processor_stats['completed'][i]}, Время простоя: {self.processor_stats['idle'][i]} сек\n"
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_message)
        self.stats_text.config(state=tk.DISABLED)

    def start_simulation(self):
        # Изменяем конфигурируемые параметры
        self.num_processors = int(self.num_processors_entry.get())
        self.num_tasks = int(self.num_tasks_entry.get())
        self.max_task_duration = int(self.max_task_duration_entry.get())

        # Очистка очереди задач
        self.task_queue.queue.clear()
        for i in range(1, self.num_tasks + 1):
            task_duration = random.randint(1, self.max_task_duration)
            self.task_queue.put(Task(task_id=i, duration=task_duration))

        # Создание и запуск процессоров
        self.processors = []
        for i in range(1, self.num_processors + 1):
            processor = Processor(
                processor_id=i,
                task_queue=self.task_queue,
                log_area=self.log_area,
                update_gui_callback=self.update_gui,
                update_chart_callback=self.update_chart,
                stats_callback=self.stats_message
            )
            self.processors.append(processor)
            processor.start()

        # Ожидание завершения всех задач
        threading.Thread(target=self.wait_for_completion).start()

    def wait_for_completion(self):
        self.task_queue.join()
        for processor in self.processors:
            processor.join()

        self.log_message("Все задачи обработаны.\n")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
