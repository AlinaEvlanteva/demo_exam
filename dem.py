import sys
import os
import pymysql
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from datetime import datetime

# Глобальные переменные
current_user_name = ""
current_user_role = ""

# Параметры подключения к БД
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'demo2026',
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# ==================== ОКНО АВТОРИЗАЦИИ ====================
class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setFixedSize(350, 250)
        self.setStyleSheet("background-color: #f0f0f0;")
        
        try:
            db = get_db_connection()
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к БД:\n{str(e)}")
            sys.exit(1)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Логин")
        self.login_edit.setStyleSheet("padding: 8px; font-size: 14px;")
        layout.addWidget(self.login_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("padding: 8px; font-size: 14px;")
        layout.addWidget(self.password_edit)
        
        btn_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("Войти")
        self.login_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 5px;")
        self.login_btn.clicked.connect(self.login)
        
        self.skip_btn = QPushButton("Пропустить (гость)")
        self.skip_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px; border-radius: 5px;")
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
        
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT name, role FROM user WHERE login=%s AND password=%s", (login, password))
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
    def __init__(self, item_data, parent_window=None):
        super().__init__()
        self.item_data = item_data
        self.parent_window = parent_window
        self.setup_ui()
    
    def setup_ui(self):
        tovar_id, picture, category, name, desc, maker, diler, price, metric, stock, discount = self.item_data
        self.tovar_id = tovar_id
        
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ФОТО
        photo_label = QLabel()
        photo_label.setFixedSize(120, 120)
        photo_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        photo_label.setAlignment(Qt.AlignCenter)
        
        if picture and picture != "picture.png":
            pix = QPixmap(f"images/{picture}")
            if not pix.isNull():
                photo_label.setPixmap(pix.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                photo_label.setText("📷")
                photo_label.setStyleSheet("font-size: 40px;")
        else:
            photo_label.setText("📷")
            photo_label.setStyleSheet("font-size: 40px;")
        main_layout.addWidget(photo_label)
        
        # ИНФОРМАЦИЯ
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        title = QLabel(f"<b>{name}</b>")
        title.setStyleSheet("font-size: 16px;")
        info_layout.addWidget(title)
        info_layout.addWidget(QLabel(f"{category}"))
        
        if desc:
            short_desc = desc[:100] + '...' if len(desc) > 100 else desc
            info_layout.addWidget(QLabel(f"{short_desc}"))
        
        if maker:
            info_layout.addWidget(QLabel(f"Производитель: {maker}"))
        if diler and diler != "None":
            info_layout.addWidget(QLabel(f"Поставщик: {diler}"))
        
        # Цена со скидкой
        if discount and discount > 0:
            new_price = price - (price * discount / 100)
            price_layout = QHBoxLayout()
            price_layout.setContentsMargins(0, 0, 0, 0)
            old_price = QLabel(f"{price:.2f} ₽")
            old_price.setStyleSheet("color: red; text-decoration: line-through;")
            new_price_label = QLabel(f"{new_price:.2f} ₽")
            new_price_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
            price_layout.addWidget(old_price)
            price_layout.addWidget(new_price_label)
            price_layout.addWidget(QLabel(f"  (скидка {discount}%)"))
            price_widget = QWidget()
            price_widget.setLayout(price_layout)
            info_layout.addWidget(price_widget)
        else:
            info_layout.addWidget(QLabel(f"{price:.2f} ₽"))
        
        if metric:
            info_layout.addWidget(QLabel(f"{metric}"))
        
        stock_label = QLabel(f"На складе: {stock} шт.")
        if stock == 0:
            stock_label.setText("НЕТ В НАЛИЧИИ")
            stock_label.setStyleSheet("color: red; font-weight: bold;")
        elif stock < 5:
            stock_label.setStyleSheet("color: orange; font-weight: bold;")
        info_layout.addWidget(stock_label)
        
        info_widget.setLayout(info_layout)
        main_layout.addWidget(info_widget, 1)
        
        # СКИДКА
        discount_widget = QWidget()
        discount_widget.setFixedWidth(150)
        discount_layout = QVBoxLayout()
        disc_value = discount if discount else 0
        disc_label = QLabel(f"{disc_value}%")
        disc_label.setAlignment(Qt.AlignCenter)
        disc_label.setStyleSheet("border: 2px solid red; border-radius: 15px; padding: 10px; font-weight: bold; font-size: 18px; color: red; background-color: white;")
        discount_layout.addWidget(disc_label)
        discount_widget.setLayout(discount_layout)
        main_layout.addWidget(discount_widget)
        
        self.setLayout(main_layout)
        
        # Подсветка
        if stock == 0:
            self.setStyleSheet("QFrame { background-color: #D3D3D3; border-radius: 8px; }")
        elif discount and discount > 15:
            self.setStyleSheet("QFrame { background-color: #008080; border-radius: 8px; }")
        else:
            self.setStyleSheet("QFrame { background-color: white; border-radius: 8px; }")
    
    def mouseDoubleClickEvent(self, event):
        if current_user_role == "Администратор":
            self.edit_product()
    
    def edit_product(self):
        if EditProductWindow.is_open():
            QMessageBox.warning(self, "Внимание", "Окно редактирования уже открыто")
            return
        self.edit_window = EditProductWindow(self.tovar_id, self.parent_window)
        self.edit_window.show()

# ==================== ОКНО РЕДАКТИРОВАНИЯ ТОВАРА ====================
class EditProductWindow(QWidget):
    edit_window_instance = None
    
    @classmethod
    def is_open(cls):
        return cls.edit_window_instance is not None and cls.edit_window_instance.isVisible()
    
    def __init__(self, tovar_id, parent_window=None):
        super().__init__()
        if EditProductWindow.is_open():
            QMessageBox.warning(self, "Внимание", "Окно редактирования уже открыто")
            self.close()
            return
        
        EditProductWindow.edit_window_instance = self
        self.tovar_id = tovar_id
        self.parent_window = parent_window
        self.setWindowTitle("Редактирование товара")
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout()
        
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT name, category, description, maker, diler, price, metric, stock, discount FROM tovar WHERE tovar_id=%s", (tovar_id,))
            self.product = cursor.fetchone()
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.close()
            return
        
        layout.addWidget(QLabel("Наименование:"))
        self.name_edit = QLineEdit(self.product[0])
        layout.addWidget(self.name_edit)
        
        layout.addWidget(QLabel("Категория:"))
        self.category_edit = QLineEdit(self.product[1])
        layout.addWidget(self.category_edit)
        
        layout.addWidget(QLabel("Описание:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setText(self.product[2])
        layout.addWidget(self.desc_edit)
        
        layout.addWidget(QLabel("Производитель:"))
        self.maker_edit = QLineEdit(self.product[3])
        layout.addWidget(self.maker_edit)
        
        layout.addWidget(QLabel("Поставщик:"))
        self.diler_edit = QLineEdit(self.product[4])
        layout.addWidget(self.diler_edit)
        
        layout.addWidget(QLabel("Цена:"))
        self.price_edit = QLineEdit(str(self.product[5]))
        layout.addWidget(self.price_edit)
        
        layout.addWidget(QLabel("Единица измерения:"))
        self.metric_edit = QLineEdit(self.product[6])
        layout.addWidget(self.metric_edit)
        
        layout.addWidget(QLabel("Количество на складе:"))
        self.stock_edit = QLineEdit(str(self.product[7]))
        layout.addWidget(self.stock_edit)
        
        layout.addWidget(QLabel("Скидка (%):"))
        self.discount_edit = QLineEdit(str(self.product[8]))
        layout.addWidget(self.discount_edit)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_product)
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_product)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def save_product(self):
        try:
            name = self.name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Ошибка", "Введите наименование товара")
                return
            
            price = float(self.price_edit.text())
            stock = int(self.stock_edit.text())
            discount = int(self.discount_edit.text())
            
            if price < 0 or stock < 0 or discount < 0 or discount > 100:
                QMessageBox.warning(self, "Ошибка", "Цена, количество и скидка должны быть от 0 до 100")
                return
            
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                UPDATE tovar SET name=%s, category=%s, description=%s, maker=%s, diler=%s,
                price=%s, metric=%s, stock=%s, discount=%s WHERE tovar_id=%s
            """, (name, self.category_edit.text(), self.desc_edit.toPlainText(),
                  self.maker_edit.text(), self.diler_edit.text(), price, self.metric_edit.text(),
                  stock, discount, self.tovar_id))
            db.commit()
            db.close()
            QMessageBox.information(self, "Успех", "Товар сохранен")
            if self.parent_window:
                self.parent_window.load_items()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def delete_product(self):
        # Проверка, есть ли товар в заказах (заглушка, т.к. в задании требуется)
        reply = QMessageBox.question(self, "Подтверждение", "Удалить товар?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                db = get_db_connection()
                cursor = db.cursor()
                # Проверяем, используется ли товар в заказах (если есть связь)
                cursor.execute("SELECT COUNT(*) FROM order_items WHERE product_id=%s", (self.tovar_id,))
                count = cursor.fetchone()[0]
                if count > 0:
                    QMessageBox.warning(self, "Ошибка", "Товар присутствует в заказах, удаление невозможно")
                    db.close()
                    return
                cursor.execute("DELETE FROM tovar WHERE tovar_id=%s", (self.tovar_id,))
                db.commit()
                db.close()
                QMessageBox.information(self, "Успех", "Товар удален")
                if self.parent_window:
                    self.parent_window.load_items()
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def closeEvent(self, event):
        EditProductWindow.edit_window_instance = None
        event.accept()

# ==================== ОКНО ДОБАВЛЕНИЯ ТОВАРА ====================
class AddProductWindow(QWidget):
    add_window_instance = None
    
    @classmethod
    def is_open(cls):
        return cls.add_window_instance is not None and cls.add_window_instance.isVisible()
    
    def __init__(self, parent_window=None):
        super().__init__()
        if AddProductWindow.is_open():
            QMessageBox.warning(self, "Внимание", "Окно добавления товара уже открыто")
            self.close()
            return
        
        AddProductWindow.add_window_instance = self
        self.parent_window = parent_window
        self.setWindowTitle("Добавление товара")
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Наименование:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        layout.addWidget(QLabel("Категория:"))
        self.category_edit = QLineEdit()
        layout.addWidget(self.category_edit)
        
        layout.addWidget(QLabel("Описание:"))
        self.desc_edit = QTextEdit()
        layout.addWidget(self.desc_edit)
        
        layout.addWidget(QLabel("Производитель:"))
        self.maker_edit = QLineEdit()
        layout.addWidget(self.maker_edit)
        
        layout.addWidget(QLabel("Поставщик:"))
        self.diler_edit = QLineEdit()
        layout.addWidget(self.diler_edit)
        
        layout.addWidget(QLabel("Цена:"))
        self.price_edit = QLineEdit()
        layout.addWidget(self.price_edit)
        
        layout.addWidget(QLabel("Единица измерения:"))
        self.metric_edit = QLineEdit()
        layout.addWidget(self.metric_edit)
        
        layout.addWidget(QLabel("Количество на складе:"))
        self.stock_edit = QLineEdit()
        layout.addWidget(self.stock_edit)
        
        layout.addWidget(QLabel("Скидка (%):"))
        self.discount_edit = QLineEdit()
        layout.addWidget(self.discount_edit)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Добавить")
        save_btn.clicked.connect(self.save_product)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def save_product(self):
        try:
            name = self.name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Ошибка", "Введите наименование товара")
                return
            
            price = float(self.price_edit.text())
            stock = int(self.stock_edit.text())
            discount = int(self.discount_edit.text())
            
            if price < 0 or stock < 0 or discount < 0 or discount > 100:
                QMessageBox.warning(self, "Ошибка", "Цена, количество и скидка должны быть от 0 до 100")
                return
            
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO tovar (name, category, description, maker, diler, price, metric, stock, discount, picture)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'picture.png')
            """, (name, self.category_edit.text(), self.desc_edit.toPlainText(),
                  self.maker_edit.text(), self.diler_edit.text(), price, self.metric_edit.text(),
                  stock, discount))
            db.commit()
            db.close()
            QMessageBox.information(self, "Успех", "Товар добавлен")
            if self.parent_window:
                self.parent_window.load_items()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def closeEvent(self, event):
        AddProductWindow.add_window_instance = None
        event.accept()

# ==================== ОКНО ДОБАВЛЕНИЯ ЗАКАЗА ====================
class AddOrderWindow(QWidget):
    add_order_instance = None

    @classmethod
    def is_open(cls):
        return cls.add_order_instance is not None and cls.add_order_instance.isVisible()

    def __init__(self, parent_window=None):
        super().__init__()
        if AddOrderWindow.is_open():
            QMessageBox.warning(self, "Внимание", "Окно добавления заказа уже открыто")
            self.close()
            return

        AddOrderWindow.add_order_instance = self
        self.parent_window = parent_window
        self.setWindowTitle("Добавление заказа")
        self.setFixedSize(400, 350)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Артикул:"))
        self.article_edit = QLineEdit()
        layout.addWidget(self.article_edit)

        layout.addWidget(QLabel("Статус заказа:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Новый", "В обработке", "Доставлен", "Завершен"])
        layout.addWidget(self.status_combo)

        layout.addWidget(QLabel("Адрес пункта выдачи:"))
        self.address_edit = QLineEdit()
        layout.addWidget(self.address_edit)

        layout.addWidget(QLabel("Дата заказа (ГГГГ-ММ-ДД):"))
        self.order_date_edit = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        layout.addWidget(self.order_date_edit)

        layout.addWidget(QLabel("Дата выдачи (ГГГГ-ММ-ДД):"))
        self.delivery_date_edit = QLineEdit()
        layout.addWidget(self.delivery_date_edit)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Добавить")
        save_btn.clicked.connect(self.save_order)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.close)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def save_order(self):
        try:
            article = self.article_edit.text().strip()
            if not article:
                QMessageBox.warning(self, "Ошибка", "Введите артикул")
                return
            status = self.status_combo.currentText()
            address = self.address_edit.text().strip()
            if not address:
                QMessageBox.warning(self, "Ошибка", "Введите адрес пункта выдачи")
                return
            order_date = self.order_date_edit.text().strip()
            delivery_date = self.delivery_date_edit.text().strip() or None

            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO orders (article, status, delivery_address, order_date, delivery_date) VALUES (%s, %s, %s, %s, %s)",
                (article, status, address, order_date, delivery_date)
            )
            db.commit()
            db.close()
            QMessageBox.information(self, "Успех", "Заказ добавлен")
            if self.parent_window:
                self.parent_window.load_orders()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def closeEvent(self, event):
        AddOrderWindow.add_order_instance = None
        event.accept()

# ==================== ОКНО РЕДАКТИРОВАНИЯ ЗАКАЗА ====================
class EditOrderWindow(QWidget):
    edit_order_instance = None

    @classmethod
    def is_open(cls):
        return cls.edit_order_instance is not None and cls.edit_order_instance.isVisible()

    def __init__(self, order_id, parent_window=None):
        super().__init__()
        if EditOrderWindow.is_open():
            QMessageBox.warning(self, "Внимание", "Окно редактирования заказа уже открыто")
            self.close()
            return

        EditOrderWindow.edit_order_instance = self
        self.order_id = order_id
        self.parent_window = parent_window
        self.setWindowTitle("Редактирование заказа")
        self.setFixedSize(400, 350)

        layout = QVBoxLayout()

        # Загружаем данные заказа
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "SELECT article, status, delivery_address, order_date, delivery_date FROM orders WHERE order_id=%s",
                (order_id,)
            )
            self.order_data = cursor.fetchone()
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.close()
            return

        layout.addWidget(QLabel("Артикул:"))
        self.article_edit = QLineEdit(self.order_data[0])
        layout.addWidget(self.article_edit)

        layout.addWidget(QLabel("Статус заказа:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Новый", "В обработке", "Доставлен", "Завершен"])
        self.status_combo.setCurrentText(self.order_data[1])
        layout.addWidget(self.status_combo)

        layout.addWidget(QLabel("Адрес пункта выдачи:"))
        self.address_edit = QLineEdit(self.order_data[2])
        layout.addWidget(self.address_edit)

        layout.addWidget(QLabel("Дата заказа (ГГГГ-ММ-ДД):"))
        self.order_date_edit = QLineEdit(str(self.order_data[3]))
        layout.addWidget(self.order_date_edit)

        layout.addWidget(QLabel("Дата выдачи (ГГГГ-ММ-ДД):"))
        self.delivery_date_edit = QLineEdit(str(self.order_data[4]) if self.order_data[4] else "")
        layout.addWidget(self.delivery_date_edit)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_order)
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_order)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.close)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def save_order(self):
        try:
            article = self.article_edit.text().strip()
            if not article:
                QMessageBox.warning(self, "Ошибка", "Введите артикул")
                return
            status = self.status_combo.currentText()
            address = self.address_edit.text().strip()
            if not address:
                QMessageBox.warning(self, "Ошибка", "Введите адрес пункта выдачи")
                return
            order_date = self.order_date_edit.text().strip()
            delivery_date = self.delivery_date_edit.text().strip() or None

            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "UPDATE orders SET article=%s, status=%s, delivery_address=%s, order_date=%s, delivery_date=%s WHERE order_id=%s",
                (article, status, address, order_date, delivery_date, self.order_id)
            )
            db.commit()
            db.close()
            QMessageBox.information(self, "Успех", "Заказ обновлен")
            if self.parent_window:
                self.parent_window.load_orders()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_order(self):
        reply = QMessageBox.question(self, "Подтверждение", "Удалить заказ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                db = get_db_connection()
                cursor = db.cursor()
                cursor.execute("DELETE FROM orders WHERE order_id=%s", (self.order_id,))
                db.commit()
                db.close()
                QMessageBox.information(self, "Успех", "Заказ удален")
                if self.parent_window:
                    self.parent_window.load_orders()
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def closeEvent(self, event):
        EditOrderWindow.edit_order_instance = None
        event.accept()

# ==================== ОКНО ЗАКАЗОВ ====================
class OrdersWindow(QWidget):
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window
        self.setWindowTitle("Заказы")
        self.setGeometry(100, 100, 900, 500)
        
        layout = QVBoxLayout()
        
        # Верхняя панель с кнопками
        top_layout = QHBoxLayout()
        back_btn = QPushButton("← Назад")
        back_btn.clicked.connect(self.close)
        top_layout.addWidget(back_btn)
        
        # Кнопка добавления заказа (только для администратора)
        if current_user_role == "Администратор":
            add_btn = QPushButton("+ Добавить заказ")
            add_btn.clicked.connect(self.add_order)
            add_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 5px;")
            top_layout.addWidget(add_btn)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Таблица заказов
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Артикул", "Статус", "Адрес выдачи", "Дата заказа", "Дата выдачи"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_orders()
        
        # Двойной клик для редактирования (только админ)
        if current_user_role == "Администратор":
            self.table.itemDoubleClicked.connect(self.edit_order)
    
    def load_orders(self):
        try:
            db = get_db_connection()
            cursor = db.cursor()
            # Предполагаем структуру таблицы orders: order_id, article, status, delivery_address, order_date, delivery_date
            cursor.execute("SELECT order_id, article, status, delivery_address, order_date, delivery_date FROM orders")
            orders = cursor.fetchall()
            db.close()
            
            self.table.setRowCount(len(orders))
            for row, (oid, article, status, address, order_date, delivery_date) in enumerate(orders):
                self.table.setItem(row, 0, QTableWidgetItem(str(oid)))
                self.table.setItem(row, 1, QTableWidgetItem(article))
                self.table.setItem(row, 2, QTableWidgetItem(status))
                self.table.setItem(row, 3, QTableWidgetItem(address))
                self.table.setItem(row, 4, QTableWidgetItem(str(order_date)))
                self.table.setItem(row, 5, QTableWidgetItem(str(delivery_date) if delivery_date else ""))
            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить заказы: {e}")
    
    def add_order(self):
        if AddOrderWindow.is_open():
            QMessageBox.warning(self, "Внимание", "Окно добавления заказа уже открыто")
            return
        self.add_order_win = AddOrderWindow(self)
        self.add_order_win.show()
    
    def edit_order(self, item):
        row = item.row()
        order_id = int(self.table.item(row, 0).text())
        if EditOrderWindow.is_open():
            QMessageBox.warning(self, "Внимание", "Окно редактирования заказа уже открыто")
            return
        self.edit_order_win = EditOrderWindow(order_id, self)
        self.edit_order_win.show()

# ==================== ОКНО СПИСКА ТОВАРОВ ====================
class ItemsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Товары")
        self.setGeometry(100, 100, 1100, 700)
        self.setStyleSheet("background-color: #f5f5f5;")
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ВЕРХНЯЯ ПАНЕЛЬ
        top_panel = QWidget()
        top_panel.setStyleSheet("background-color: white; border-radius: 5px;")
        top_layout = QHBoxLayout()
        
        exit_btn = QPushButton("Выйти")
        exit_btn.clicked.connect(self.back_to_login)
        exit_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px 15px; border-radius: 5px;")
        top_layout.addWidget(exit_btn)
        
        # Кнопка заказов (для менеджера и админа)
        if current_user_role in ["Менеджер", "Администратор"]:
            orders_btn = QPushButton("📋 Заказы")
            orders_btn.clicked.connect(self.open_orders)
            orders_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px 15px; border-radius: 5px;")
            top_layout.addWidget(orders_btn)
        
        # Кнопка добавления товара (только админ)
        if current_user_role == "Администратор":
            add_btn = QPushButton("+ Добавить товар")
            add_btn.clicked.connect(self.add_product)
            add_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 15px; border-radius: 5px;")
            top_layout.addWidget(add_btn)
        
        logo_label = QLabel("🛍️ Магазин обуви")
        logo_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(logo_label)
        top_layout.addStretch()
        
        user_label = QLabel(f"👤 {current_user_name} ({current_user_role})")
        user_label.setStyleSheet("font-size: 12px; color: gray;")
        top_layout.addWidget(user_label)
        
        top_panel.setLayout(top_layout)
        main_layout.addWidget(top_panel)
        
        # ПАНЕЛЬ ФИЛЬТРОВ (только для менеджера и админа)
        if current_user_role in ["Менеджер", "Администратор"]:
            filter_panel = QWidget()
            filter_panel.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px;")
            filter_layout = QHBoxLayout()
            
            search_label = QLabel("🔍 Поиск:")
            filter_layout.addWidget(search_label)
            self.search_edit = QLineEdit()
            self.search_edit.setPlaceholderText("Название, категория, описание...")
            self.search_edit.setMinimumWidth(200)
            filter_layout.addWidget(self.search_edit)
            
            discount_label = QLabel("Скидка:")
            filter_layout.addWidget(discount_label)
            self.discount_filter = QComboBox()
            self.discount_filter.addItems(["Все диапазоны", "0-10.99%", "11-14.99%", "15% и более"])
            filter_layout.addWidget(self.discount_filter)
            
            sort_label = QLabel("Сортировка:")
            filter_layout.addWidget(sort_label)
            self.sort_combo = QComboBox()
            self.sort_combo.addItems(["По умолчанию", "Цена ▲", "Цена ▼", "Склад ▲", "Склад ▼"])
            filter_layout.addWidget(self.sort_combo)
            
            filter_layout.addStretch()
            filter_panel.setLayout(filter_layout)
            main_layout.addWidget(filter_panel)
            
            # Подключаем события
            self.search_edit.textChanged.connect(self.load_items)
            self.discount_filter.currentTextChanged.connect(self.load_items)
            self.sort_combo.currentTextChanged.connect(self.load_items)
        
        # ОБЛАСТЬ ТОВАРОВ
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
        self.load_items()
    
    def back_to_login(self):
        global current_user_name, current_user_role
        current_user_name = ""
        current_user_role = ""
        self.login_form = LoginForm()
        self.login_form.show()
        self.close()
    
    def open_orders(self):
        self.orders_window = OrdersWindow(self)
        self.orders_window.show()
    
    def add_product(self):
        if AddProductWindow.is_open():
            QMessageBox.warning(self, "Внимание", "Окно добавления товара уже открыто")
            return
        self.add_window = AddProductWindow(self)
        self.add_window.show()
    
    def load_items(self):
        # Очистка
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        try:
            db = get_db_connection()
            cursor = db.cursor()
            query = """SELECT tovar_id, picture, category, name, description, maker, diler, price, metric, stock, discount FROM tovar WHERE 1=1"""
            params = []
            
            if current_user_role in ["Менеджер", "Администратор"]:
                search_text = self.search_edit.text().strip()
                if search_text:
                    query += " AND (LOWER(name) LIKE %s OR LOWER(category) LIKE %s OR LOWER(description) LIKE %s OR LOWER(maker) LIKE %s)"
                    search_param = f"%{search_text.lower()}%"
                    params.extend([search_param, search_param, search_param, search_param])
                
                discount_range = self.discount_filter.currentText()
                if discount_range == "0-10.99%":
                    query += " AND discount >= 0 AND discount < 11"
                elif discount_range == "11-14.99%":
                    query += " AND discount >= 11 AND discount < 15"
                elif discount_range == "15% и более":
                    query += " AND discount >= 15"
                
                sort_by = self.sort_combo.currentText()
                if sort_by == "Цена ▲":
                    query += " ORDER BY price ASC"
                elif sort_by == "Цена ▼":
                    query += " ORDER BY price DESC"
                elif sort_by == "Склад ▲":
                    query += " ORDER BY stock ASC"
                elif sort_by == "Склад ▼":
                    query += " ORDER BY stock DESC"
                else:
                    query += " ORDER BY name"
            else:
                query += " ORDER BY name"
            
            cursor.execute(query, params)
            items = cursor.fetchall()
            cursor.close()
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))
            return
        
        if not items:
            empty_label = QLabel("📭 Товаров не найдено")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-size: 18px; color: gray; padding: 50px;")
            self.items_layout.addWidget(empty_label)
            return
        
        for item in items:
            card = ItemCard(item, self)
            self.items_layout.addWidget(card)
        
        count_label = QLabel(f"📊 Найдено товаров: {len(items)}")
        count_label.setStyleSheet("color: gray; padding: 5px;")
        self.items_layout.addWidget(count_label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = LoginForm()
    window.show()
    sys.exit(app.exec_())