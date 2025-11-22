Travel Planner - это desktop-приложение для управления бронированием туристических путевок, разработанное на Python с использованием Tkinter для графического интерфейса, SQLite3 для хранения данных и Docker для контейнеризации. Система предоставляет функционал многопользовательского бронирования с предотвращением конфликтов и контролем доступности мест.

Технологический стек
Язык программирования: Python 3.12+
Графический интерфейс: Tkinter
База данных: SQLite3
Контейнеризация: Docker
Тестирование: pytest
Логирование: стандартный модуль logging

Установка и запуск, локальный запуск (без Docker)

1.Клонируйте репозиторий:
git clone https://github.com/kaboom771/PyLab3
cd PyLab3

2.Создайте виртуальное окружение:
python -m venv venv
source venv/bin/activate # Linux/MacOS
venv\Scripts\activate # Windows

3.Установите зависимости:
pip install -r requirements.txt

4.Запустите приложение:

python3 main.py

команды для докера
создание образа: docker build -t lab3 .
сборка контейнера: docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw lab3
