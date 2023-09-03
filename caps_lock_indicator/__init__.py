# pip install PyQt6 pynput
from platform import system
from sys import argv, exit

from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QPalette, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from pynput import keyboard


class Listener(QThread):
    caps = pyqtSignal(bool)

    def __init__(self, main_window):
        super().__init__()
        self.listener = keyboard.Listener(
            on_press=self.press, on_release=self.release)
        self.started.connect(self.listener.start)
        self.main_window = main_window

    def press(self, key):
        if key == keyboard.Key.caps_lock:
            self.caps.emit(True)
        elif not self.main_window.isHidden():
            self.main_window.show()

    def release(self, key):
        if key == keyboard.Key.caps_lock:
            self.caps.emit(False)
        elif not self.main_window.isHidden():
            self.main_window.hide()


class CapsLockDetector(QLabel):
    capsStatus = False

    def __init__(self, main_window):
        super().__init__()
        self.listener = Listener(main_window)
        self.listener.caps.connect(self.handleCaps)
        self.listener.start()
        self.main_window = main_window

    def handleCaps(self, pressed):
        if not pressed or not self.capsStatus:
            self.updateCapsLockStatus()

    def updateCapsLockStatus(self):
        new_status = None
        if system() == "Windows":
            import ctypes
            hllDll = ctypes.WinDLL("User32.dll")
            VK_CAPITAL = 0x14
            new_status = hllDll.GetKeyState(VK_CAPITAL) not in [0, 65408]
        elif system() == "Linux":
            import subprocess
            new_status = subprocess.check_output('xset q | grep "Caps Lock"', shell=True).split()[3] == b'on'
            print(new_status)

        self.main_window.show()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("color: white;")
        font = QFont("Consolas", 30)
        self.setFont(font)
        self.setText("Caps lock: " + ("OFF" if not new_status else "ON"))
        self.capsStatus = new_status


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        caps_detector = CapsLockDetector(self)
        self.setCentralWidget(caps_detector)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setGeometry(0, 0, 400, 120)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(10, 10, 10))
        self.setPalette(palette)

        screen_geometry = QApplication.primaryScreen().geometry()
        self.move(screen_geometry.x(), screen_geometry.y())
        self.show()

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        self.hide()


app = QApplication(argv)
windows = MainWindow()
windows.hide()
exit(app.exec())
