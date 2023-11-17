import sys
import pathlib
import PyQt5.QtWidgets

from PyQt5 import uic
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QWidget, QTableView

import Default
import Search
import Download
import DataBase

import yandex_music.exceptions


class ShowDataBase(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(pathlib.Path(r'.ui_files\database.ui'), self)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(880, 700)
        self.setWindowTitle('Tracks')
        self.show_db()
        self.Clear_Button.clicked.connect(self.clear)

    def show_db(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(r'data\Downloaded_tracks.sqlite')
        db.open()

        view = QTableView(self)
        model = QSqlTableModel(self, db)
        model.setTable('Tracks')
        model.select()

        view.setModel(model)
        view.move(10, 10)
        view.resize(860, 600)

    @classmethod
    def clear(cls):
        DataBase.clear_db()


class Settings(QWidget):
    def __init__(self, parent=None, dont_open_settings=True):
        super(Settings, self).__init__()
        uic.loadUi(pathlib.Path(r'.ui_files\settings.ui'), self)
        self.setWindowTitle('Enter your token')
        # self.setIconSize(QSize(100, 100))
        # self.setWindowIcon(QIcon(str(pathlib.Path(r'.ui_files\icon.png'))))

        self.parent = parent
        self.dont_open_settings = dont_open_settings

        self.client = Default.Default()
        self.path = self.client.set_default_download_path()

        self.check_valid_token()

    def check_valid_token(self):
        if not self.client.config_enabled() or not self.dont_open_settings:
            self.edit_token()
        else:
            self.home()

    def edit_token(self):
        self.show()
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(880, 700)

        self.Confirm_Button.clicked.connect(self.confirm)
        self.Path_Button.clicked.connect(self.chance_directory)
        self.Path.setText(str(self.path))

    def home(self, token=None, path=None, reshape=False):
        try:
            self.client.init_config(token, path, reset_config=reshape)
            self.hide()
            self.parent.client = self.client
        except yandex_music.exceptions.UnauthorizedError:
            print('no token???')

    def confirm(self):
        self.home(self.Token.text(), self.path, reshape=True)
        self.Token.setText('')

    def chance_directory(self):
        self.path = QFileDialog.getExistingDirectory(self, 'Such directory', str(self.path))
        if self.path == '':
            self.path = str(self.client.set_default_download_path())
        self.Path.setText(str(self.path))


class Homepage(PyQt5.QtWidgets.QMainWindow):
    def __init__(self):
        super(Homepage, self).__init__()
        uic.loadUi(pathlib.Path(r'.ui_files\homepage.ui'), self)
        self.setWindowTitle('Music Search')
        self.setIconSize(QSize(100, 100))
        self.setWindowIcon(QIcon(str(pathlib.Path(r'.ui_files\icon.png'))))

        self.settings = None
        self.client = None
        self.current_track = None
        self.db = None

        self.init_ui()
        self.edit_config()

    def init_ui(self):
        self.show()
        self.Error.hide()
        self.setFixedSize(880, 700)

        self.Edit_token.clicked.connect(self.edit_config)
        self.Search_Button.clicked.connect(self.request)
        self.Data_Base.clicked.connect(self.show_db)

    def edit_config(self, dont_open_settings=True):
        self.settings = Settings(self, dont_open_settings)

    def request(self):
        self.search(self.find_string.text())
        self.find_string.setText('')

    def show_db(self):
        self.db = ShowDataBase()
        self.db.show()

    def search(self, request):
        self.Error.hide()
        track_list = SearchResult(self.client, request, self)
        track_list.show()


class SearchResult(PyQt5.QtWidgets.QMainWindow):
    def __init__(self, client, request, parent=None):
        super(SearchResult, self).__init__(parent)
        uic.loadUi(pathlib.Path(r'.ui_files\track_list.ui'), self)
        self.setWindowTitle('Track list')
        self.setIconSize(QSize(100, 100))
        self.setWindowIcon(QIcon(str(pathlib.Path(r'.ui_files\icon.png'))))

        self.settings = None

        self.request = request
        self.parent = parent
        self.client = client
        self.search_result = self.search(self.request)
        self.track_list = [self.Track1, self.Track2, self.Track3, self.Track4, self.Track5]
        self.cover_list = [self.Cover1, self.Cover2, self.Cover3, self.Cover4, self.Cover5]

        self.init_ui()

    def init_ui(self):
        self.setFixedSize(880, 700)
        self.parent.hide()

        self.find_string.setText(self.request)

        self.Track1.mousePressEvent = self.track1
        self.Track2.mousePressEvent = self.track2
        self.Track3.mousePressEvent = self.track3
        self.Track4.mousePressEvent = self.track4
        self.Track5.mousePressEvent = self.track5

        for track_index in range(len(self.track_list)):
            self.show_tracks(track_index)

        self.Home.clicked.connect(self.home)

    def search(self, request):
        try:
            search_result = Search.search(self.client, request)
            if len(search_result) == 0:
                self.parent.Error.show()
                self.parent.Error.setText('По вашему запросу ничего не найдено')
                raise IndexError('По вашему запросу ничего не найдено')
            return search_result
        except yandex_music.exceptions.BadRequestError:
            self.parent.Error.show()
            self.parent.Error.setText('По вашему запросу ничего не найдено')
            raise IndexError('По вашему запросу ничего не найдено')
        except TypeError:
            self.parent.Error.show()
            self.parent.Error.setText('По вашему запросу ничего не найдено')
            raise IndexError('По вашему запросу ничего не найдено')

    def show_tracks(self, track_index):  # show track and cover
        if len(self.search_result) > track_index:
            pixmap = QPixmap()
            pixmap.loadFromData(self.search_result[track_index]['image_bin_light'])
            self.cover_list[track_index].setPixmap(pixmap)
            self.track_list[track_index].setText(self.search_result[track_index]['title'])
            self.track_list[track_index].setStyleSheet(
                "color: blue; font-family: Poppins; font-size: 30px; "
                "font-style: normal; font-weight: 400; line-height: normal; text-decoration: underline;")
        else:
            self.track_list[track_index].hide()
            self.cover_list[track_index].hide()

    def track1(self, event):  # get current index 1
        if event.button() == Qt.LeftButton:
            self.download(self.search_result[0])

    def track2(self, event):  # get current index 2
        if event.button() == Qt.LeftButton:
            self.download(self.search_result[1])

    def track3(self, event):  # get current index 3
        if event.button() == Qt.LeftButton:
            self.download(self.search_result[2])

    def track4(self, event):  # get current index 4
        if event.button() == Qt.LeftButton:
            self.download(self.search_result[3])

    def track5(self, event):  # get current index 5
        if event.button() == Qt.LeftButton:
            self.download(self.search_result[4])

    def download(self, track):  # show track
        tracks = Track(self.client, track, self.request, self)
        tracks.show()

    def find_track(self):
        self.parent.search(self.find_string.text())
        self.home()

    def home(self):
        self.parent.show()
        self.close()


class Track(PyQt5.QtWidgets.QMainWindow):
    def __init__(self, client, track, request, parent=None):
        super(Track, self).__init__(parent)
        uic.loadUi(pathlib.Path(r'.ui_files\track.ui'), self)
        self.setWindowTitle('Track')
        self.setIconSize(QSize(100, 100))
        self.setWindowIcon(QIcon(str(pathlib.Path(r'.ui_files\icon.png'))))

        self.request = request
        self.parent = parent
        self.client = client
        self.track = track
        self.path = self.client.download_path()

        self.init_ui()

    def init_ui(self):
        self.setFixedSize(880, 700)
        self.find_string.setText(self.request)
        self.parent.close()

        self.Title.setText(f"track title: {self.track['title']}")
        pixmap = QPixmap()
        pixmap.loadFromData(self.track['image_bin_huge'])
        self.Cover_image.setPixmap(pixmap)

        self.Track.clicked.connect(self.download)
        self.Cover.clicked.connect(self.download)
        self.Lyric.clicked.connect(self.download)
        self.Home.clicked.connect(self.home)

    def download(self):
        if self.path is None:  # such directory to save
            self.chance_directory()

        self.path = self.client.download_path()  # get save directory

        prompt = self.sender().text()  # which button was clicked

        if prompt == 'Track':
            Download.download_track(self.client, self.track, self.path)  # download music

        elif prompt == 'Cover':
            Download.download_cover(self.client, self.track, self.path)  # download image

        elif prompt == 'Lyric':
            Download.download_lyric(self.client, self.track, self.path)  # download text

    def find_track(self):
        self.parent.find_track()
        self.home()

    def home(self):
        self.parent.show()
        self.parent.home()
        self.close()


def except_hooks(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hooks
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    ms = Homepage()
    sys.exit(app.exec_())
