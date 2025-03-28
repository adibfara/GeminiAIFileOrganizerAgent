import os
import shutil
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout

from ai_organizer import AIOrganizer


class DropArea(QWidget):
    current_folder = None
    files = []
    folders = []
    organizer_response = None

    def __init__(self):
        super().__init__()
        self.ai_organizer = AIOrganizer()
        self.setAcceptDrops(True)
        self.setWindowTitle("دستیار فولدرها - AdibCodes")
        self.setGeometry(100, 100, 800, 900)

        self.layout = QVBoxLayout()

        self.text_area = self.text()
        self.intro_text = self.text()
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.analyze)
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply)
        self.button_group  = self.init_button_group()
        self.intro_text.append("فولدرت رو اینجا بنداز")

        self.new_folders_area = self.text(5)
        self.renamed_files_area = self.text(5)


        folder_group = QWidget()
        group_layout = QVBoxLayout(folder_group)

        new_folders_widget = self.arrange_vertically(self.label("New Folders:"), self.new_folders_area)
        renamed_widget = self.arrange_vertically(self.label("Renamed Files:"), self.renamed_files_area)
        horizontal_widget = self.arrange_horizontally(new_folders_widget, renamed_widget)
        group_layout.addWidget(horizontal_widget)
        group_layout.addWidget(self.button_group)
        folder_group.setVisible(False)

        self.layout.addWidget(folder_group)
        self.layout.addWidget(self.intro_text)
        self.intro_text.setAlignment(Qt.AlignCenter)

        self.folder_group = folder_group

        self.setLayout(self.layout)
        self.center_on_primary_screen()

    def arrange_vertically(self, *items):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        for item in items:
            layout.addWidget(item)

        return widget

    def arrange_horizontally(self, *items):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        for item in items:
            layout.addWidget(item)

        return widget

    def init_button_group(self):
        button_row = QWidget()
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(0, 0, 0, 0)


        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.apply_button)
        return button_row
    def center_on_primary_screen(self):
        screen = QApplication.screens()[-1]
        rect = screen.availableGeometry()
        self.move(rect.topRight())

    def text(self, lines=0, set_height = False):
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setStyleSheet("background: transparent; border: none;")
        text_area.viewport().setAutoFillBackground(False)
        if lines:
            text_area.setFixedHeight(750)
        return text_area

    def button(self, text):
        button = QPushButton()
        button.setText(text)
        button.setVisible(False)
        return button

    def label(self, title):
        label = QTextEdit()
        label.setReadOnly(True)
        label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        label.setFixedHeight(30)
        label.setText(title)
        label.setAlignment(Qt.AlignLeft)
        label.setStyleSheet("background: transparent; border: none; font-weight: bold;")
        return label

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.text_area.clear()
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.current_folder = path
                self.update_files_folder()
                break

    def update_files_folder(self):
        self.intro_text.clear()
        path = Path(self.current_folder)
        folders = []
        files = []
        for file in path.iterdir():
            if file.is_file():
                files.append(str(file.name))
            else:
                folders.append(str(file.name))
        self.files = files
        self.folders = folders

        self.text_area.append(f"Folder: {path.name}")
        self.text_area.append("Files:")
        for file in files:
            self.text_area.append(file)
        self.text_area.append("Folders:")
        for folder in folders:
            self.text_area.append(folder)

        self.folder_group.setVisible(True)


    def set_new_folders(self, folders):
        self.new_folders_area.clear()
        self.new_folders_area.append(folders)

    def set_renamed_files(self, files):
        self.renamed_files_area.clear()
        self.renamed_files_area.append(files)

    def analyze(self):
        organizer_response = self.ai_organizer.organize(self.files, self.folders)
        self.organizer_response = organizer_response
        self.set_renamed_files("\n".join(rename.formatted() for rename in organizer_response.renames))
        self.set_new_folders("\n".join(folder.formatted() for folder in organizer_response.grouped_items))
        print(organizer_response)

    def apply(self):
        if not self.organizer_response: return

        for rename in self.organizer_response.renames:
            current_path = os.path.join(self.current_folder, rename.from_name)
            new_path = os.path.join(self.current_folder, rename.to_name)
            if os.path.exists(current_path):
                print(f"Renaming:\n${current_path}\n${new_path}")
                os.rename(current_path, new_path)

        for new_folder in self.organizer_response.new_folders_renamed():
            new_folder_path = os.path.join(self.current_folder, new_folder.name)
            os.makedirs(new_folder_path, exist_ok=True)

            for file in new_folder.files:
                file_path = os.path.join(self.current_folder, file)
                new_file_path = os.path.join(new_folder_path, file)
                if not os.path.exists(new_file_path):
                    print(f"Moving:\n${file_path}\n${new_file_path}")
                    shutil.move(file_path, new_file_path)





app = QApplication([])
window = DropArea()
window.show()
app.exec_()
