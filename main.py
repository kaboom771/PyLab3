import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Добавляем корневую директорию в путь для импортов
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, current_dir)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)



from app.database.init_database import initialize_database, database_exists
from app.lib.trip import TripManager, NoAvailableSeatsError, DatabaseError, AlreadyBookedError
from app.lib.logger import setup_logger

class TravelBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система бронирования путевок")
        self.root.geometry("900x700")
        
        # Инициализация компонентов
        self.trip_manager = TripManager()
        self.logger = setup_logger()
        self.current_user_id = None
        self.current_user_name = None
        
        # Инициализация базы данных (только если не существует)
        self.initialize_app()
        
        # Создание GUI
        self.create_widgets()
        self.load_users()
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
        
        # User selection frame
        user_frame = ttk.LabelFrame(main_frame, text="Выбор пользователя")
        user_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(user_frame, text="Пользователь:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.user_var = tk.StringVar(value="Не выбран")
        self.user_combo = ttk.Combobox(user_frame, textvariable=self.user_var, state="readonly", width=40)
        self.user_combo.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        self.user_combo.bind('<<ComboboxSelected>>', self.on_user_selected)
        
        self.user_info_label = ttk.Label(user_frame, text="Выберите пользователя для бронирования", foreground="blue")
        self.user_info_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Title
        title_label = ttk.Label(main_frame, text="Доступные путевки", font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 5))
        
        # Table frame
        table_frame = ttk.LabelFrame(main_frame, text="Список путевок")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create table
        columns = ("ID", "Направление", "Дата начала", "Дата окончания", "Цена (руб)", "Всего мест", "Доступно мест")
        self.trips_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
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
            command=self.refresh_data
        )
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # My bookings button
        self.bookings_button = ttk.Button(
            button_frame,
            text="Мои бронирования",
            command=self.show_my_bookings,
            state=tk.DISABLED
        )
        self.bookings_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Выберите пользователя и путевку для бронирования", foreground="blue")
        self.status_label.pack(pady=5)
        
        # Bind table selection
        self.trips_table.bind('<<TreeviewSelect>>', self.on_table_select)
    
    def load_users(self):
        """Загружает список пользователей в выпадающий список."""
        try:
            users = self.trip_manager.get_all_users()
            user_dict = {f"{user[1]} (ID: {user[0]})": user[0] for user in users}
            
            self.users_data = user_dict
            self.user_combo['values'] = list(user_dict.keys())
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {e}")
            self.logger.error(f"Ошибка загрузки пользователей: {e}")
    
    def on_user_selected(self, event):
        """Обрабатывает выбор пользователя."""
        selected_display = self.user_combo.get()
        if selected_display in self.users_data:
            self.current_user_id = self.users_data[selected_display]
            self.current_user_name = selected_display.split(' (ID:')[0]  # Извлекаем только ФИО
            
            self.user_info_label.config(text=f"Выбран: {self.current_user_name}", foreground="green")
            self.bookings_button.config(state=tk.NORMAL)
            self.update_status()
            
            self.logger.info(f"Выбран пользователь: {self.current_user_name} (ID: {self.current_user_id})")
        else:
            self.current_user_id = None
            self.current_user_name = None
            self.user_info_label.config(text="Выберите пользователя для бронирования", foreground="blue")
            self.bookings_button.config(state=tk.DISABLED)
            self.book_button.config(state=tk.DISABLED)
    
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
            
            self.update_status()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить путевки: {e}")
            self.logger.error(f"Ошибка загрузки путевок: {e}")
    
    def refresh_data(self):
        """Обновляет данные о путевках и пользователях."""
        self.load_trips()
        self.load_users()
    
    def on_table_select(self, event):
        """Обрабатывает выбор путевки в таблице."""
        if not self.current_user_id:
            self.status_label.config(text="Сначала выберите пользователя", foreground="red")
            return
            
        selection = self.trips_table.selection()
        if selection:
            self.book_button.config(state=tk.NORMAL)
            item = self.trips_table.item(selection[0])
            available_seats = item['values'][6]
            trip_id = item['values'][0]
            
            # Проверяем, не забронировал ли уже пользователь эту путевку
            try:
                already_booked = self.trip_manager.check_booking_exists(self.current_user_id, trip_id)
            except Exception as e:
                already_booked = False
            
            if already_booked:
                self.status_label.config(text="Вы уже забронировали эту путевку", foreground="orange")
                self.book_button.config(state=tk.DISABLED)
            elif available_seats <= 0:
                self.status_label.config(text="В этой путевке нет свободных мест", foreground="red")
                self.book_button.config(state=tk.DISABLED)
            else:
                self.status_label.config(
                    text=f"Выбрано: {item['values'][1]} - {available_seats} мест доступно", 
                    foreground="green"
                )
        else:
            self.book_button.config(state=tk.DISABLED)
            self.update_status()
    
    def update_status(self):
        """Обновляет статусную строку."""
        if self.current_user_id:
            self.status_label.config(text="Выберите путевку для бронирования", foreground="blue")
        else:
            self.status_label.config(text="Выберите пользователя и путевку для бронирования", foreground="blue")
    
    def book_selected_trip(self):
        """Бронирует выбранную путевку для текущего пользователя."""
        if not self.current_user_id:
            messagebox.showwarning("Предупреждение", "Сначала выберите пользователя")
            return
            
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
                f"Вы уверены, что хотите забронировать путевку в {destination} для {self.current_user_name}?"
            )
            
            if result:
                booking_result = self.trip_manager.book_trip(self.current_user_id, trip_id)
                
                messagebox.showinfo(
                    "Успех", 
                    f"{self.current_user_name} успешно забронировал(а) путевку в {booking_result['destination']}!\n"
                    f"Осталось свободных мест: {booking_result['remaining_seats']}"
                )
                
                # Refresh table and selection
                self.load_trips()
                self.book_button.config(state=tk.DISABLED)
                
        except AlreadyBookedError as e:
            messagebox.showerror("Ошибка", str(e))
            self.load_trips()  # Refresh to update status
        except NoAvailableSeatsError as e:
            messagebox.showerror("Ошибка", str(e))
            self.load_trips()  # Refresh to update available seats
        except DatabaseError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {e}")
            self.logger.error(f"Неизвестная ошибка при бронировании: {e}")
    
    def show_my_bookings(self):
        """Показывает бронирования текущего пользователя."""
        if not self.current_user_id:
            messagebox.showwarning("Предупреждение", "Сначала выберите пользователя")
            return
        
        try:
            bookings = self.trip_manager.get_user_bookings(self.current_user_id)
            
            if not bookings:
                messagebox.showinfo("Бронирования", f"{self.current_user_name} еще не бронировал(а) путевки")
                return
            
            # Создаем окно с бронированиями
            bookings_window = tk.Toplevel(self.root)
            bookings_window.title(f"Бронирования - {self.current_user_name}")
            bookings_window.geometry("700x400")
            
            # Создаем таблицу бронирований
            columns = ("Направление", "Дата начала", "Дата окончания", "Цена (руб)", "Дата бронирования")
            tree = ttk.Treeview(bookings_window, columns=columns, show="headings", height=15)
            
            # Настраиваем колонки
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor=tk.CENTER)
            
            # Заполняем данными
            for booking in bookings:
                tree.insert("", tk.END, values=booking[1:])  # Пропускаем ID
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(bookings_window, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            self.logger.info(f"Показаны бронирования пользователя {self.current_user_name}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить бронирования: {e}")
            self.logger.error(f"Ошибка загрузки бронирований: {e}")

def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = TravelBookingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()