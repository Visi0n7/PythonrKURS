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
    def __init__(self, processor_id, task_queue, log_area, update_gui_callback, update_chart_callback):
        super().__init__()
        self.processor_id = processor_id
        self.task_queue = task_queue
        self.log_area = log_area
        self.update_gui_callback = update_gui_callback
        self.update_chart_callback = update_chart_callback

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
            except queue.Empty:
                self.log_area.insert(tk.END, f"Процессор {self.processor_id} завершил работу\n")
                self.update_gui_callback(self.processor_id, "Завершил работу")
                break

# Основной класс приложения
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Симуляция обработки данных")
        self.task_queue = queue.Queue()

        # Инициализация данных для диаграммы
        self.processor_durations = []

        # Создание GUI
        self.create_widgets()

    def create_widgets(self):
        # Панель ввода параметров
        self.params_frame = tk.Frame(self.root)
        self.params_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        ttk.Label(self.params_frame, text="Количество процессоров:", font=("Arial", 14)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.num_processors_entry = ttk.Entry(self.params_frame, font=("Arial", 14), width=5)
        self.num_processors_entry.grid(row=0, column=1, pady=5)
        self.num_processors_entry.insert(0, "3")

        ttk.Label(self.params_frame, text="Количество задач:", font=("Arial", 14)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.num_tasks_entry = ttk.Entry(self.params_frame, font=("Arial", 14), width=5)
        self.num_tasks_entry.grid(row=1, column=1, pady=5)
        self.num_tasks_entry.insert(0, "10")

        # Лог-область
        self.log_area = tk.Text(self.root, height=30, width=80, state=tk.DISABLED, font=("Arial", 12))
        self.log_area.grid(row=1, column=0, rowspan=2, padx=10, pady=10, sticky=tk.NS)

        # Диаграмма выполнения
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.bar_chart = None
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=1, padx=10, pady=10)

        # Кнопки управления
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.grid(row=2, column=1, pady=10)

        button_font = ("Arial", 16)  # Увеличенный шрифт для кнопок

        self.start_button = tk.Button(self.buttons_frame, text="Запустить", font=button_font, command=self.start_simulation, width=15, height=2)
        self.start_button.grid(row=0, column=0, padx=10)

        self.exit_button = tk.Button(self.buttons_frame, text="Выход", font=button_font, command=self.root.quit, width=15, height=2)
        self.exit_button.grid(row=0, column=1, padx=10)

        # Метка для отображения завершения
        self.finished_label = ttk.Label(self.root, text="", font=("Arial", 14, "bold"))
        self.finished_label.grid(row=3, column=0, columnspan=3, pady=10)

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
        self.canvas.draw()

    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message)
        self.log_area.config(state=tk.DISABLED)
        self.log_area.see(tk.END)

    def start_simulation(self):
        # Очищаем логи перед запуском
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)

        # Получаем значения из полей ввода
        num_processors = int(self.num_processors_entry.get())
        num_tasks = int(self.num_tasks_entry.get())

        # Очистка очереди задач
        self.task_queue.queue.clear()

        # Генерация случайных задач
        for i in range(1, num_tasks + 1):
            task_duration = random.randint(1, 5)
            self.task_queue.put(Task(task_id=i, duration=task_duration))

        # Создание и запуск процессоров
        self.processors = []
        for i in range(1, num_processors + 1):
            processor = Processor(
                processor_id=i,
                task_queue=self.task_queue,
                log_area=self.log_area,
                update_gui_callback=self.update_gui,
                update_chart_callback=self.update_chart,
            )
            self.processors.append(processor)
            processor.start()

        # Ожидание завершения всех задач
        threading.Thread(target=self.wait_for_completion).start()

    def wait_for_completion(self):
        self.task_queue.join()
        for processor in self.processors:
            processor.join()

        self.finished_label.config(text="Все задачи обработаны.\n")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
