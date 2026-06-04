import sys
import os
import pymysql
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt

# Глобальные переменные
current_user_name = ""
current_user_role = ""

# Параметры подключения к БД
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # ЗАМЕНИ НА СВОЙ ПАРОЛЬ
    'database': 'demo2026',
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_db_connection():
    """Создает новое подключение к БД через pymysql"""
    return pymysql.connect(**DB_CONFIG)

# ==================== ОКНО АВТОРИЗАЦИИ ====================
class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setFixedSize(350, 250)
        self.setStyleSheet("background-color: #f0f0f0;")
        
        # Проверяем подключение
        try:
            db = get_db_connection()
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к БД:\n{str(e)}")
            sys.exit(1)
        
        # Создаем виджеты
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Поле логина
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Логин")
        self.login_edit.setStyleSheet("padding: 8px; font-size: 14px;")
        layout.addWidget(self.login_edit)
        
        # Поле пароля
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("padding: 8px; font-size: 14px;")
        layout.addWidget(self.password_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("Войти")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.login_btn.clicked.connect(self.login)
        
        self.skip_btn = QPushButton("Пропустить (гость)")
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        self.skip_btn.clicked.connect(self.skip)
        
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.skip_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def skip(self):
        global current_user_name, current_user_role
        current_user_name = "Гость"
        current_user_role = "Пользователь"
        self.open_items()
    
    def login(self):
        global current_user_name, current_user_role
        login = self.login_edit.text()
        password = self.password_edit.text()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        
        # Создаем новое подключение для проверки
        db = get_db_connection()
        cursor = db.cursor()
        
        cursor.execute(
            "SELECT name, role FROM user WHERE login=%s AND password=%s", 
            (login, password)
        )
        result = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        if not result:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
            return
        
        current_user_name = result[0]
        current_user_role = result[1]
        self.open_items()
    
    def open_items(self):
        self.items_window = ItemsWindow()
        self.items_window.show()
        self.close()

# ==================== КАРТОЧКА ТОВАРА ====================
class ItemCard(QFrame):
    def __init__(self, item_data):
        super().__init__()
        self.item_data = item_data
        self.setup_ui()
    
    def setup_ui(self):
        tovar_id, picture, category, name, desc, maker, diler, price, metric, stock, discount = self.item_data
        
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        
        # Основной layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ===== ФОТО =====
        photo_label = QLabel()
        photo_label.setFixedSize(120, 120)
        photo_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        photo_label.setAlignment(Qt.AlignCenter)
        
        # Загружаем фото
        image_path = f"images/{picture}" if picture and picture != "picture.png" and os.path.exists(f"images/{picture}") else "picture.png"
        if not os.path.exists(image_path):
            image_path = "picture.png"
        
        if os.path.exists(image_path):
            pix = QPixmap(image_path)
            if not pix.isNull():
                photo_label.setPixmap(pix.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                photo_label.setText("📷")
                photo_label.setStyleSheet("font-size: 40px;")
        else:
            photo_label.setText("📷")
            photo_label.setStyleSheet("font-size: 40px;")
        
        main_layout.addWidget(photo_label)
        
        # ===== ИНФОРМАЦИЯ =====
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # Название
        title = QLabel(f"<b>{name}</b>")
        title.setStyleSheet("font-size: 16px;")
        info_layout.addWidget(title)
        
        # Категория
        info_layout.addWidget(QLabel(f"{category}"))
        
        # Описание
        if desc:
            short_desc = desc[:100] + '...' if len(desc) > 100 else desc
            info_layout.addWidget(QLabel(f"{short_desc}"))
        
        # Производитель и поставщик
        if maker:
            info_layout.addWidget(QLabel(f"Производитель: {maker}"))
        if diler and diler != "None":
            info_layout.addWidget(QLabel(f"Поставщик: {diler}"))
        
        # Цена со скидкой
        if discount and discount > 0:
            new_price = price - (price * discount / 100)
            price_widget = QWidget()
            price_layout = QHBoxLayout()
            price_layout.setContentsMargins(0, 0, 0, 0)
            
            old_price = QLabel(f"{price:.2f} ₽")
            old_price.setStyleSheet("color: red; text-decoration: line-through;")
            new_price_label = QLabel(f"{new_price:.2f} ₽")
            new_price_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
            
            price_layout.addWidget(old_price)
            price_layout.addWidget(new_price_label)
            price_layout.addWidget(QLabel(f"  (скидка {discount}%)"))
            price_widget.setLayout(price_layout)
            info_layout.addWidget(price_widget)
        else:
            info_layout.addWidget(QLabel(f" {price:.2f} ₽"))
        
        # Единица измерения
        if metric:
            info_layout.addWidget(QLabel(f" {metric}"))
        
        # Склад
        stock_label = QLabel(f"На складе: {stock} шт.")
        if stock == 0:
            stock_label.setText("НЕТ В НАЛИЧИИ")
            stock_label.setStyleSheet("color: red; font-weight: bold;")
        elif stock < 5:
            stock_label.setStyleSheet("color: orange; font-weight: bold;")
        
        info_layout.addWidget(stock_label)
        
        info_widget.setLayout(info_layout)
        main_layout.addWidget(info_widget, 1)
        
        # ===== СКИДКА =====
        discount_widget = QWidget()
        discount_widget.setFixedWidth(150)
        discount_layout = QVBoxLayout()
        
        disc_value = discount if discount else 0
        disc_label = QLabel(f"{disc_value}%")
        disc_label.setAlignment(Qt.AlignCenter)
        disc_label.setStyleSheet("""
            border: 2px solid red;
            border-radius: 15px;
            padding: 10px;
            font-weight: bold;
            font-size: 18px;
            color: red;
            background-color: white;
        """)
        discount_layout.addWidget(disc_label)
        discount_widget.setLayout(discount_layout)
        main_layout.addWidget(discount_widget)
        
        self.setLayout(main_layout)
        
        # Подсветка если скидка > 15%
        if discount and discount > 15:
            self.setStyleSheet("QFrame { background-color: #2E8B57; border-radius: 8px; }")
        else:
            self.setStyleSheet("QFrame { background-color: white; border-radius: 8px; }")

# ==================== ОКНО СПИСКА ТОВАРОВ ====================
class ItemsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Товары")
        self.setGeometry(100, 100, 1100, 700)
        self.setStyleSheet("background-color: #f5f5f5;")
        
        # Главный layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ===== ВЕРХНЯЯ ПАНЕЛЬ =====
        top_panel = QWidget()
        top_panel.setStyleSheet("background-color: white; border-radius: 5px;")
        top_layout = QHBoxLayout()
        
        # Кнопка выхода
        exit_btn = QPushButton("Выйти")
        exit_btn.clicked.connect(self.back_to_login)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        top_layout.addWidget(exit_btn)
        
        # Логотип/название
        logo_label = QLabel("Магазин обуви")
        logo_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(logo_label)
        
        top_layout.addStretch()
        
        # Информация о пользователе
        user_label = QLabel(f"{current_user_name} ({current_user_role})")
        user_label.setStyleSheet("font-size: 12px; color: gray;")
        top_layout.addWidget(user_label)
        
        top_panel.setLayout(top_layout)
        main_layout.addWidget(top_panel)
        
        # ===== ПАНЕЛЬ ФИЛЬТРОВ (только для менеджера и админа) =====
        if current_user_role in ["Менеджер", "Администратор"]:
            filter_panel = QWidget()
            filter_panel.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px;")
            filter_layout = QHBoxLayout()
            
            # Поиск
            search_label = QLabel("Поиск:")
            filter_layout.addWidget(search_label)
            self.search_edit = QLineEdit()
            self.search_edit.setPlaceholderText("Название, категория, описание...")
            self.search_edit.setMinimumWidth(250)
            filter_layout.addWidget(self.search_edit)
            
            # Фильтр по поставщику
            supplier_label = QLabel("Поставщик:")
            filter_layout.addWidget(supplier_label)
            self.diler_filter = QComboBox()
            self.diler_filter.setMinimumWidth(150)
            self.diler_filter.addItem("Все поставщики")
            
            # Загружаем список поставщиков
            try:
                db = get_db_connection()
                cursor = db.cursor()
                # Проверяем, есть ли колонка diler в таблице
                cursor.execute("SHOW COLUMNS FROM tovar")
                columns = [col[0] for col in cursor.fetchall()]
                if 'diler' in columns:
                    cursor.execute("SELECT DISTINCT diler FROM tovar WHERE diler IS NOT NULL AND diler != '' AND diler != 'None'")
                    suppliers = cursor.fetchall()
                    for supplier in suppliers:
                        if supplier[0]:
                            self.diler_filter.addItem(supplier[0])
                else:
                    self.diler_filter.addItem("Нет данных")
                cursor.close()
                db.close()
            except Exception as e:
                print(f"Ошибка загрузки поставщиков: {e}")
                self.diler_filter.addItem("Ошибка загрузки")
            
            filter_layout.addWidget(self.diler_filter)
            
            # Сортировка по складу
            sort_label = QLabel("Сортировка по складу:")
            filter_layout.addWidget(sort_label)
            self.sort_combo = QComboBox()
            self.sort_combo.addItems(["По умолчанию", "По возрастанию", "По убыванию"])
            filter_layout.addWidget(self.sort_combo)
            
            filter_layout.addStretch()
            filter_panel.setLayout(filter_layout)
            main_layout.addWidget(filter_panel)
            
            # Подключаем события
            self.search_edit.textChanged.connect(self.load_items)
            self.diler_filter.currentTextChanged.connect(self.load_items)
            self.sort_combo.currentTextChanged.connect(self.load_items)
        
        # ===== ОБЛАСТЬ ДЛЯ ТОВАРОВ (скролл) =====
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background-color: transparent;")
        
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(15)
        self.items_layout.setAlignment(Qt.AlignTop)
        self.items_widget.setLayout(self.items_layout)
        
        self.scroll_area.setWidget(self.items_widget)
        main_layout.addWidget(self.scroll_area)
        
        self.setLayout(main_layout)
        
        # Загружаем товары
        self.load_items()
    
    def back_to_login(self):
        global current_user_name, current_user_role
        current_user_name = ""
        current_user_role = ""
        self.login_form = LoginForm()
        self.login_form.show()
        self.close()
    
    def load_items(self):
        # Очищаем старые карточки
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Подключаемся к БД
        try:
            db = get_db_connection()
            cursor = db.cursor()
            
            # Базовый запрос
            query = """SELECT tovar_id, picture, category, name, description, maker, diler, 
                              price, metric, stock, discount 
                       FROM tovar WHERE 1=1"""
            params = []
            
            # ДЛЯ МЕНЕДЖЕРА И АДМИНА - добавляем фильтры
            if current_user_role in ["Менеджер", "Администратор"]:
                # Поиск по тексту
                search_text = self.search_edit.text().strip()
                if search_text:
                    query += """ AND (LOWER(name) LIKE %s 
                                 OR LOWER(category) LIKE %s 
                                 OR LOWER(description) LIKE %s
                                 OR LOWER(maker) LIKE %s)"""
                    search_param = f"%{search_text.lower()}%"
                    params.extend([search_param, search_param, search_param, search_param])
                
                # Фильтр по поставщику
                supplier = self.diler_filter.currentText()
                if supplier and supplier != "Все поставщики" and supplier != "Нет данных" and supplier != "Ошибка загрузки":
                    query += " AND diler = %s"
                    params.append(supplier)
                
                # Сортировка по складу
                sort_order = self.sort_combo.currentText()
                if sort_order == "По возрастанию":
                    query += " ORDER BY stock ASC"
                elif sort_order == "По убыванию":
                    query += " ORDER BY stock DESC"
            else:
                # Для гостя - без сортировки
                query += " ORDER BY name"
            
            # Выполняем запрос
            cursor.execute(query, params)
            items = cursor.fetchall()
            
            cursor.close()
            db.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка запроса:\n{str(e)}\n\nЗапрос: {query}")
            return
        
        if not items:
            empty_label = QLabel("Товаров не найдено")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-size: 18px; color: gray; padding: 50px;")
            self.items_layout.addWidget(empty_label)
            return
        
        # Создаем карточки
        for item in items:
            card = ItemCard(item)
            self.items_layout.addWidget(card)
        
        # Показываем количество товаров
        count_label = QLabel(f"Найдено товаров: {len(items)}")
        count_label.setStyleSheet("color: gray; padding: 5px;")
        self.items_layout.addWidget(count_label)

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    
    window = LoginForm()
    window.show()
    sys.exit(app.exec_())