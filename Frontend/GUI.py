import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values

env_vars = dotenv_values(os.path.join(os.path.dirname(__file__), '.env'))
AssistantName = env_vars.get('AssistantName', 'Jarvis')
current_dir = os.path.dirname(os.path.abspath(__file__))  # Fix: Get correct current directory
old_chat_message = ""
TempDirPath = os.path.join(current_dir, "Files")  # Fix: Use os.path.join for paths
GraphicsDirPath = os.path.join(current_dir, "Graphics")  # Fix: Use os.path.join for paths

# Create necessary directories if they don't exist
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'which', 'whose', 'whom', 'can you']
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['?', '.', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
            
    else: 
        if query_words[-1][-1] in ['?', '.', '!']:
            new_query += "."
        else:
            new_query += "."
        
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(os.path.join(TempDirPath, "Mic.data"), "w", encoding='utf-8') as file:
        file.write(Command)
        
def GetMicrophoneStatus():
    try:
        with open(os.path.join(TempDirPath, "Mic.data"), "r", encoding='utf-8') as file:
            Status = file.read()
        return Status
    except FileNotFoundError:
        # Create file if it doesn't exist
        with open(os.path.join(TempDirPath, "Mic.data"), "w", encoding='utf-8') as file:
            file.write("False")
        return "False"

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)
        
def GetAssistantStatus():
    try:
        with open(os.path.join(TempDirPath, "Status.data"), "r", encoding='utf-8') as file:
            Status = file.read()
        return Status
    except FileNotFoundError:
        # Create file if it doesn't exist
        with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
            file.write("")
        return ""

def MicButtonInitialed():
    SetMicrophoneStatus("True")
    
def MicButtonClosed():
    SetMicrophoneStatus("False")

def GraphicsDirectoryPath(Filename):
    return os.path.join(GraphicsDirPath, os.path.basename(Filename))

def TempDirectoryPath(Filename):
    """Return the full path to a file in the Temp directory."""
    # Make sure TempDirPath is defined at module level
    return os.path.join(TempDirPath, Filename)

def ShowTextToScreen(Text):
    with open(os.path.join(TempDirPath, "Responses.data"), "w", encoding='utf-8') as file:
        file.write(Text)

class ChatSection(QWidget):
    
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        
        # Fix: Corrected method name
        self.setStyleSheet("background-color: black;")
        
        # self.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        
        # Fix: Corrected method name
        text_color_text.setForeground(text_color)
        
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        
        # Fix: Use correct path for Jarvis.gif
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)
        
        # Fix: Corrected variable name
        self.label = QLabel("")
        
        self.label.setStyleSheet("color: white; font-size:16px; margin-right:195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)
        layout.addWidget(self.gif_label)
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogtext)
        self.timer.start(5)
        self.chat_text_edit.viewport().installEventFilter(self)
        
        # Add icon_label and toggled properties
        self.icon_label = QLabel(self)
        self.toggled = True
        
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            
            QScrollBar::handle:vertical {
                background: white;
                min-height: 0px;
                }
            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
                }
            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
                }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
                }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                }
        """)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                
                if None==messages:
                    pass
                elif len(messages)<1:
                    pass
                elif str(old_chat_message)==str(messages):
                    pass
                else:
                    self.addMessage(message=messages, color='White')
                    old_chat_message = messages
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write("")
                
    def SpeechRecogtext(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open(TempDirectoryPath('Status.data'), "w", encoding='utf-8') as file:
                file.write("")
            
    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)
        
    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.jpg'), 60, 60)
            MicButtonInitialed()
            
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.jpg'), 60, 60)
            MicButtonClosed()
            
        self.toggled = not self.toggled
        
    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)
        
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        gif_label = QLabel()
        
        # Fix: Use correct path for Jarvis.gif
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.icon_label = QLabel()
        
        # Fix: Use correct path for Mic_on.jpg
        pixmap = QPixmap(GraphicsDirectoryPath('Mic_on.jpg'))
        
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)
        self.setFixedWidth(screen_width)
        self.setFixedHeight(screen_height)
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogtext)
        self.timer.start(5)
        
    def SpeechRecogtext(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open(TempDirectoryPath('Status.data'), "w", encoding='utf-8') as file:
                file.write("")
            
    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)
        
    def toggle_icon(self, event = None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.jpg'), 60, 60)
            MicButtonInitialed()
            
        else:
            # Fix: Changed to Mic_off.jpg
            self.load_icon(GraphicsDirectoryPath('Mic_off.jpg'), 60, 60)
            MicButtonClosed()
            
        self.toggled = not self.toggled
        
class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedWidth(screen_width)
        self.setFixedHeight(screen_height)
        
class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget
        
    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        home_button = QPushButton()
        
        # Fix: Use correct path for home.jpg
        home_icon = QIcon(GraphicsDirectoryPath('home.jpg'))
        
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("height: 40px; line-height: 40px; background-color: white; color: black;")
        message_button = QPushButton()
        
        # Fix: Use correct path for Chats.jpg
        message_icon = QIcon(GraphicsDirectoryPath('Chats.jpg'))
        
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet("height: 40px; line-height: 40px; background-color: white; color: black;")
        minimize_button = QPushButton()
        
        # Fix: Use correct path for Minimize2.jpg
        minimize_icon = QIcon(GraphicsDirectoryPath('Minimize2.jpg'))
        
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color: white")
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button = QPushButton()
        
        # Fix: Use correct paths for maximize/minimize icons
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.jpg'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.jpg'))
        
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setStyleSheet("background-color: white")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button = QPushButton()    
        
        # Fix: Use correct path for Close.jpg
        close_icon = QIcon(GraphicsDirectoryPath('Close.jpg'))
        
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color: white")
        close_button.clicked.connect(self.closeWindow)
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")
        title_label = QLabel(f" {str(AssistantName).capitalize()} AI   ")
        title_label.setStyleSheet("color: black; font-size: 18px;; background-color:white")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)
        
    def minimizeWindow(self):
        self.parent().showMinimized()
        
    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)
            
    def closeWindow(self):
        self.parent().close()
        
    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()
            
    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)
            
    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen
        
    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
            
        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)
        
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    GraphicalUserInterface()