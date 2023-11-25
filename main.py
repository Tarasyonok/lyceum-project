import sys
import sqlite3

from itertools import chain
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Project(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('todo.ui', self)
        self.tasksList.setIconSize(QSize(20, 20))
        self.tasksList.setFont(QFont("Times", 12, QFont.Black))

        self.addBtn.clicked.connect(self.add_task)

        self.tasksList.itemClicked.connect(self.update_box)
        self.tasksList.itemDoubleClicked.connect(self.show_edit_task)

        self.today.clicked.connect(self.load_today)
        self.tomorrow.clicked.connect(self.load_tomorrow)
        self.daily.clicked.connect(self.load_daily)

        self.con = sqlite3.connect("database.sqlite")

        self.load_today()

    def load_tasks(self):
        cur = self.con.cursor()
        if self.curr_plan == 'today':
            result = cur.execute("""SELECT text, isDone from Today""").fetchall()
        else:
            result = cur.execute(f"""SELECT text from {self.curr_plan}""").fetchall()

        self.tasksList.clear()
        for elem in result:
            print(elem)
            item = QListWidgetItem()
            if elem[1] == 0:
                icon = QIcon('checkboxOff.png')
            else:
                icon = QIcon('checkboxOn.png')
            item.setIcon(icon)
            item.setText(elem[0])
            self.tasksList.addItem(item)

    def load_today(self):
        self.curr_plan = 'today'
        self.planLabel.setText("План на сегодня")
        self.load_tasks()

    def load_tomorrow(self):
        self.curr_plan = 'tomorrow'
        self.planLabel.setText("План на завтра")
        self.load_tasks()

    def load_daily(self):
        self.curr_plan = 'daily'
        self.planLabel.setText("Ежедневные дела")
        self.load_tasks()

    def update_box(self, item):
        if self.curr_plan != 'today':
            return
        text = item.text()
        cur = self.con.cursor()
        result = cur.execute("""SELECT isDone from Today WHERE text = ?""", (text,)).fetchone()
        if result[0] == 1:
            icon = QIcon('checkboxOff.png')
            item.setIcon(icon)
            cur.execute("""UPDATE Today SET isDone = 0 WHERE text = ?""", (text,))
            try:
                cur.execute("""UPDATE Today SET isDone = 0 WHERE text = ?""", (text,))
            except:
                pass
        else:
            icon = QIcon('checkboxOn.png')
            item.setIcon(icon)
            cur.execute("""UPDATE Today SET isDone = 1 WHERE text = ?""", (text,))
        self.con.commit()

    def add_task(self):
        new_task = self.taskName.text()
        if new_task == '':
            self.statusBar().showMessage("В поле ввода пусто.")
            return
        item = QListWidgetItem()
        if self.curr_plan == 'today':
            icon = QIcon('checkboxOff.png')
            item.setIcon(icon)
        item.setText(new_task)
        self.tasksList.addItem(item)

        cur = self.con.cursor()

        result = cur.execute(f"""SELECT text from {self.curr_plan}""").fetchall()
        for elem in result:
            if elem[0] == new_task:
                self.statusBar().showMessage("Это дело уже есть в списке.")
                return

        cur.execute(f"INSERT INTO {self.curr_plan}(text) VALUES('{new_task}')")
        if self.curr_plan != 'tomorrow':
            cur.execute(f"INSERT INTO Tomorrow(text) VALUES('{new_task}')")

        self.con.commit()

        self.taskName.setText('')

        # self.update_tasks()

    def show_edit_task(self, item):
        task_text = item.text()
        task_id = self.tasksList.indexFromItem(item).row()
        self.edit = taskEdit(task_id, task_text, parent=self)
        self.edit.show()

class taskEdit(QMainWindow):
    def __init__(self, task_id, task_text, parent=None):
        super().__init__()
        uic.loadUi('taskEdit.ui', self)
        self.task_id = task_id
        print('---------->', self.task_id)
        self.parent = parent
        self.lineEdit.setText(task_text)
        self.deleteBtn.clicked.connect(self.delete_task)
        self.saveBtn.clicked.connect(self.save_changes)

    def save_changes(self):
        text = self.lineEdit.text()
        if text == '':
            self.statusBar().showMessage("В поле ввода пусто.")
        else:
            print(self.parent)
            cur = self.parent.con.cursor()
            print(self.parent.tasksList)
            for i in range(self.parent.tasksList.count()):
                print(self.parent.tasksList.item(i).text())
                if self.parent.tasksList.item(i).text() == text:
                    self.statusBar().showMessage("Это дело уже есть в списке.")
                    return

            self.parent.load_today()
            print(self.parent.curr_plan)
            cur.execute(f"UPDATE {self.parent.curr_plan} SET text = '{text}' WHERE id = {self.task_id}")
            self.parent.con.commit()

            self.parent.statusBar().showMessage("Изменения сохранены.")
            self.hide()

    def delete_task(self):
        cur = self.parent.con.cursor()
        cur.execute(f"DELETE from {self.parent.curr_plan} WHERE id = {self.task_id}")
        self.parent.con.commit()
        self.parent.load_today()
        self.parent.statusBar().showMessage("Дело удалено из списка.")
        self.hide()








app = QApplication(sys.argv)
ex = Project()
ex.show()
sys.exit(app.exec())

# import sys
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore    import *
#
#
# class ExampleWidget(QWidget):
#     def __init__(self, parent=None):
#         super().__init__()
#         self.setWindowTitle('Example Widget ScrollArea')
#         self.initUi()
#
#     def initUi(self):
#         self.area = QScrollArea(self)
#         self.area.setWidgetResizable(True)
#         self.scrollAreaWidgetContents = QLabel(some_long_text, self.area)
#
#         self.area.setWidget(self.scrollAreaWidgetContents)
#         button = QPushButton("Закрыть окно")
#         button.clicked.connect(self.goMainWindow)
#
#         layoutV = QVBoxLayout()
#         layoutV.addWidget(self.area)
#         layoutV.addWidget(button)
#         self.setLayout(layoutV)
#
#     def goMainWindow(self):
#         self.hide()
#
#     def sizeHint(self):
#         return QSize(400, 200)
#
#
# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         start_main_button  = QPushButton('Start', self)
#         start_main_button.move(40, 40)
#         start_main_button.clicked.connect(self.start)
#         self.setGeometry(300, 300, 290, 150)
#         self.setWindowTitle('Test')
#
#     def start(self):
#         self.result_widget = ExampleWidget()
#         self.result_widget.show()
#
#
# some_long_text = """
# Есть всплывающее окно QWidget, вызываемое кнопкой Start на основном виджете.
# В него помещается текст, превышающий размер окна.
# Как я могу добавить в него вертикальную полосу прокрутки, чтобы видеть весь текст?
# Есть всплывающее окно QWidget, вызываемое кнопкой Start на основном виджете.
# В него помещается текст, превышающий размер окна.
# Как я могу добавить в него вертикальную полосу прокрутки, чтобы видеть весь текст?
# Есть всплывающее окно QWidget, вызываемое кнопкой Start на основном виджете.
# В него помещается текст, превышающий размер окна.
# Как я могу добавить в него вертикальную полосу прокрутки, чтобы видеть весь текст?
# Есть всплывающее окно QWidget, вызываемое кнопкой Start на основном виджете. В него помещается текст, превышающий размер окна.
# Как я могу добавить в него вертикальную полосу прокрутки, чтобы видеть весь текст?
# Есть всплывающее окно QWidget, вызываемое кнопкой Start на основном виджете.
# В него помещается текст, превышающий размер окна.
# Как я могу добавить в него вертикальную полосу прокрутки, чтобы видеть весь текст?
# """
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())
