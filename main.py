import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Добавляем корневую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.init_database import initialize_database, database_exists
from app.lib.trip import TripManager, NoAvailableSeatsError, DatabaseError
from app.lib.logger import setup_logger

class TravelBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система бронирования путевок")
        self.root.geometry("800x600")
        
        # Инициализация компонентов
        self.trip_manager = TripManager()
        self.logger = setup_logger()
        
        # Инициализация базы данных (только если не существует)
        self.initialize_app()
        
        # Создание GUI
        self.create_widgets()
        self.load_trips()
    
    def initialize_app(self):
        """Инициализирует приложение и базу данных только при первом запуске."""
        try:
            if not database_exists():
                # Первый запуск - создаем БД с тестовыми данными
                if not initialize_database():
                    messagebox.showerror("Ошибка", "Не удалось инициализировать базу данных")
                    self.root.quit()
                    return
                self.logger.info("База данных создана с начальными данными")
            else:
                # БД уже существует, используем существующую
                self.logger.info("Используется существующая база данных")
            
            self.logger.info("Приложение успешно инициализировано")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка инициализации: {e}")
            self.root.quit()
    
    def create_widgets(self):
        """Создает элементы интерфейса."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Доступные путевки", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Table frame
        table_frame = ttk.LabelFrame(main_frame, text="Список путевок")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create table
        columns = ("ID", "Направление", "Дата начала", "Дата окончания", "Цена (руб)", "Всего мест", "Доступно мест")
        self.trips_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = [50, 120, 100, 100, 100, 80, 100]
        for col, width in zip(columns, column_widths):
            self.trips_table.heading(col, text=col)
            self.trips_table.column(col, width=width, anchor=tk.CENTER)
        
        # Scrollbar for table
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.trips_table.yview)
        self.trips_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.trips_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Book button
        self.book_button = ttk.Button(
            button_frame, 
            text="Забронировать выбранную путевку", 
            command=self.book_selected_trip,
            state=tk.DISABLED
        )
        self.book_button.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_button = ttk.Button(
            button_frame, 
            text="Обновить список", 
            command=self.load_trips
        )
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Выберите путевку для бронирования", foreground="blue")
        self.status_label.pack(pady=5)
        
        # Bind table selection
        self.trips_table.bind('<<TreeviewSelect>>', self.on_table_select)
    
    def on_table_select(self, event):
        """Обрабатывает выбор путевки в таблице."""
        selection = self.trips_table.selection()
        if selection:
            self.book_button.config(state=tk.NORMAL)
            item = self.trips_table.item(selection[0])
            available_seats = item['values'][6]
            
            if available_seats <= 0:
                self.status_label.config(text="В этой путевке нет свободных мест", foreground="red")
                self.book_button.config(state=tk.DISABLED)
            else:
                self.status_label.config(
                    text=f"Выбрано: {item['values'][1]} - {available_seats} мест доступно", 
                    foreground="green"
                )
        else:
            self.book_button.config(state=tk.DISABLED)
            self.status_label.config(text="Выберите путевку для бронирования", foreground="blue")
    
    def load_trips(self):
        """Загружает путевки из базы данных и отображает в таблице."""
        try:
            # Clear table
            for item in self.trips_table.get_children():
                self.trips_table.delete(item)
            
            # Load trips
            trips = self.trip_manager.get_all_trips()
            
            # Populate table
            for trip in trips:
                self.trips_table.insert("", tk.END, values=trip)
            
            self.status_label.config(text=f"Загружено {len(trips)} путевок", foreground="blue")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить путевки: {e}")
            self.logger.error(f"Ошибка загрузки путевок: {e}")
    
    def book_selected_trip(self):
        """Бронирует выбранную путевку."""
        selection = self.trips_table.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите путевку для бронирования")
            return
        
        try:
            item = self.trips_table.item(selection[0])
            trip_id = item['values'][0]
            destination = item['values'][1]
            
            result = messagebox.askyesno(
                "Подтверждение бронирования", 
                f"Вы уверены, что хотите забронировать путевку в {destination}?"
            )
            
            if result:
                booking_result = self.trip_manager.book_trip(trip_id)
                
                messagebox.showinfo(
                    "Успех", 
                    f"Вы успешно забронировали путевку в {booking_result['destination']}!\n"
                    f"Осталось свободных мест: {booking_result['remaining_seats']}"
                )
                
                # Refresh table
                self.load_trips()
                self.book_button.config(state=tk.DISABLED)
                
        except NoAvailableSeatsError as e:
            messagebox.showerror("Ошибка", str(e))
            self.load_trips()  # Refresh to update available seats
        except DatabaseError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {e}")
            self.logger.error(f"Неизвестная ошибка при бронировании: {e}")

def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = TravelBookingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()