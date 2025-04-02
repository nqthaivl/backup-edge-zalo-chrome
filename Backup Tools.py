import sys
import os
import shutil
import platform
import json
import psutil
import subprocess
import ctypes
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QProgressBar, QComboBox, QLineEdit, 
                            QFileDialog, QCheckBox, QGridLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon

class BackupWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, backup_type, params):
        super().__init__()
        self.backup_type = backup_type
        self.params = params

    def run(self):
        try:
            if self.backup_type == "zalo":
                self.backup_zalo()
            elif self.backup_type == "chrome_backup":
                self.backup_chrome()
            elif self.backup_type == "chrome_restore":
                self.restore_chrome()
            elif self.backup_type == "edge_backup":
                self.backup_edge()
            elif self.backup_type == "edge_restore":
                self.restore_edge()
            elif self.backup_type == "general":
                self.backup_general()
        except Exception as e:
            self.error.emit(str(e))

    def backup_zalo(self):
        dest_drive = self.params["dest_drive"]
        user_profile = os.environ['USERPROFILE']
        zalo_path = os.path.join(user_profile, 'AppData', 'Local', 'ZaloPC')
        
        if not os.path.exists(zalo_path):
            self.error.emit(f"Không tìm thấy thư mục ZaloPC tại: {zalo_path}")
            return
            
        backup_folder = os.path.join(dest_drive, 'ZaloPC_Backup')
        os.makedirs(backup_folder, exist_ok=True)
        
        total_files = sum(len(files) for _, _, files in os.walk(zalo_path))
        processed_files = 0
        
        for root, _, files in os.walk(zalo_path):
            for file in files:
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(src_file, zalo_path)
                dest_file = os.path.join(backup_folder, rel_path)
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.copy2(src_file, dest_file)
                processed_files += 1
                self.progress.emit(int(processed_files / total_files * 100))
        
        self.adjust_zalo_path(zalo_path, backup_folder)
        self.finished.emit(f"Sao lưu Zalo hoàn tất! Đã lưu tại: {backup_folder}")

    def adjust_zalo_path(self, orig_path, backup_path):
        os.system('taskkill /IM Zalo.exe /F')
        if os.path.exists(orig_path):
            if os.path.islink(orig_path):
                os.unlink(orig_path)
            else:
                shutil.rmtree(orig_path)
        subprocess.run(['cmd', '/c', 'mklink', '/D', orig_path, backup_path], check=True)

    def backup_chrome(self):
        src_path = self.params["src_path"]
        dest_path = self.params["dest_path"]
        profile = self.params["profile"]
        
        backup_folder = os.path.join(dest_path, f'chrome_backup_{profile}')
        os.makedirs(backup_folder, exist_ok=True)
        
        profile_path = os.path.join(src_path, profile)
        essential_files = ['Bookmarks', 'Login Data', 'History', 'Preferences']
        total_files = len([f for f in essential_files if os.path.exists(os.path.join(profile_path, f))])
        processed_files = 0
        
        for file in essential_files:
            src_file = os.path.join(profile_path, file)
            if os.path.exists(src_file):
                shutil.copy2(src_file, os.path.join(backup_folder, file))
                processed_files += 1
                self.progress.emit(int(processed_files / total_files * 100))
        
        self.finished.emit(f"Sao lưu hồ sơ Chrome {profile} hoàn tất!")

    def restore_chrome(self):
        backup_path = self.params["backup_path"]
        dest_path = self.params["dest_path"]
        profile = self.params["profile"]
        
        profile_path = os.path.join(dest_path, profile)
        essential_files = ['Bookmarks', 'Login Data', 'History', 'Preferences']
        total_files = len([f for f in essential_files if os.path.exists(os.path.join(backup_path, f))])
        processed_files = 0
        
        for file in essential_files:
            src_file = os.path.join(backup_path, file)
            if os.path.exists(src_file):
                dest_file = os.path.join(profile_path, file)
                if os.path.exists(dest_file):
                    os.remove(dest_file)
                shutil.copy2(src_file, dest_file)
                processed_files += 1
                self.progress.emit(int(processed_files / total_files * 100))
        
        self.finished.emit(f"Khôi phục hồ sơ Chrome {profile} thành công!")

    def backup_edge(self):
        src_path = self.params["src_path"]
        dest_path = self.params["dest_path"]
        profile = self.params["profile"]
        
        backup_folder = os.path.join(dest_path, f'edge_backup_{profile}')
        os.makedirs(backup_folder, exist_ok=True)
        
        profile_path = os.path.join(src_path, profile)
        essential_files = ['Bookmarks', 'Login Data', 'History', 'Preferences']
        total_files = len([f for f in essential_files if os.path.exists(os.path.join(profile_path, f))])
        processed_files = 0
        
        for file in essential_files:
            src_file = os.path.join(profile_path, file)
            if os.path.exists(src_file):
                shutil.copy2(src_file, os.path.join(backup_folder, file))
                processed_files += 1
                self.progress.emit(int(processed_files / total_files * 100))
        
        self.finished.emit(f"Sao lưu hồ sơ Edge {profile} hoàn tất!")

    def restore_edge(self):
        backup_path = self.params["backup_path"]
        dest_path = self.params["dest_path"]
        profile = self.params["profile"]
        
        profile_path = os.path.join(dest_path, profile)
        essential_files = ['Bookmarks', 'Login Data', 'History', 'Preferences']
        total_files = len([f for f in essential_files if os.path.exists(os.path.join(backup_path, f))])
        processed_files = 0
        
        for file in essential_files:
            src_file = os.path.join(backup_path, file)
            if os.path.exists(src_file):
                dest_file = os.path.join(profile_path, file)
                if os.path.exists(dest_file):
                    os.remove(dest_file)
                shutil.copy2(src_file, dest_file)
                processed_files += 1
                self.progress.emit(int(processed_files / total_files * 100))
        
        self.finished.emit(f"Khôi phục hồ sơ Edge {profile} thành công!")

    def backup_general(self):
        dest_path = self.params["dest_path"]
        folders = self.params["folders"]
        
        total_files = 0
        for _, src in folders:
            if os.path.exists(src):
                total_files += sum(len(files) for _, _, files in os.walk(src))
        
        processed_files = 0
        for name, src in folders:
            if os.path.exists(src):
                dest = os.path.join(dest_path, name)
                os.makedirs(dest, exist_ok=True)
                for root, _, files in os.walk(src):
                    for file in files:
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, src)
                        dest_file = os.path.join(dest, rel_path)
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                        shutil.copy2(src_file, dest_file)
                        processed_files += 1
                        self.progress.emit(int(processed_files / total_files * 100))
        
        self.finished.emit("Sao lưu chung hoàn tất!")

class BackupTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Công Cụ Sao Lưu Zalo & Edge")
        self.setGeometry(100, 100, 600, 250)
        self.setStyleSheet("background-color: #f0f4f8;")
        
        # Thêm icon cho cửa sổ chính với đường dẫn tuyệt đối
        icon_path = os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.chrome_tab = QWidget()
        self.edge_tab = QWidget()
        self.zalo_tab = QWidget()  # Chuyển tab Zalo xuống sau Edge
        self.general_tab = QWidget()
        
        # Thay đổi thứ tự thêm tab
        self.tabs.addTab(self.chrome_tab, "Sao Lưu Chrome")
        self.tabs.addTab(self.edge_tab, "Sao Lưu Edge")
        self.tabs.addTab(self.zalo_tab, "Sao Lưu Zalo")
        self.tabs.addTab(self.general_tab, "Sao Lưu Chung")
        
        self.init_chrome_ui()
        self.init_edge_ui()
        self.init_zalo_ui()  # Gọi sau Edge
        self.init_general_ui()
        
        footer = QWidget()
        footer_layout = QHBoxLayout()
        footer.setStyleSheet("background-color: #f5f6f5;")
        footer_label = QLabel("© 2025 1TouchPro - Mọi quyền được bảo lưu")
        footer_label.setStyleSheet("font: 8pt 'Segoe UI'; color: #888888;")
        phuocit_label = QLabel("https://1touch.pro")
        phuocit_label.setStyleSheet("font: italic 8pt 'Segoe UI'; color: #ff5555;")
        footer_layout.addWidget(footer_label)
        footer_layout.addStretch()
        footer_layout.addWidget(phuocit_label)
        footer.setLayout(footer_layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(footer)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def init_zalo_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Sao Lưu Dữ Liệu Zalo")
        title.setStyleSheet("font: bold 16pt 'Helvetica'; color: white; background-color: #4a90e2;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.zalo_dest = QLineEdit("D:\\")
        layout.addWidget(QLabel("Ổ Đĩa Đích:"))
        layout.addWidget(self.zalo_dest)
        
        select_btn = QPushButton("Chọn")
        select_btn.clicked.connect(self.select_zalo_dest)
        select_btn.setStyleSheet("background-color: #4a90e2; color: white;")
        select_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        layout.addWidget(select_btn)
        
        self.zalo_progress = QProgressBar()
        layout.addWidget(QLabel("Tiến Trình:"))
        layout.addWidget(self.zalo_progress)
        
        start_btn = QPushButton("BẮT ĐẦU SAO LƯU")
        start_btn.clicked.connect(self.start_zalo_backup)
        start_btn.setStyleSheet("background-color: #4a90e2; color: white; font: bold 12pt 'Helvetica';")
        start_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        layout.addWidget(start_btn)
        
        layout.addStretch()
        self.zalo_tab.setLayout(layout)

    def init_chrome_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Sao Lưu & Khôi Phục Chrome")
        title.setStyleSheet("font: bold 16pt 'Helvetica'; color: white; background-color: #4a90e2;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        backup_frame = QWidget()
        backup_layout = QGridLayout()
        
        self.chrome_profiles = self.get_chrome_profiles()
        self.chrome_profile_combo = QComboBox()
        self.chrome_profile_combo.addItems(list(self.chrome_profiles.values()))
        backup_layout.addWidget(QLabel("Chọn Hồ Sơ:"), 0, 0)
        backup_layout.addWidget(self.chrome_profile_combo, 0, 1)
        
        self.chrome_backup_dest = QLineEdit()
        backup_layout.addWidget(QLabel("Thư Mục Sao Lưu:"), 1, 0)
        backup_layout.addWidget(self.chrome_backup_dest, 1, 1)
        select_backup_btn = QPushButton("Chọn")
        select_backup_btn.clicked.connect(self.select_chrome_backup_dest)
        select_backup_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        backup_layout.addWidget(select_backup_btn, 1, 2)
        
        backup_btn = QPushButton("Sao Lưu Ngay")
        backup_btn.clicked.connect(self.start_chrome_backup)
        backup_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        backup_layout.addWidget(backup_btn, 2, 0, 1, 3)
        backup_frame.setLayout(backup_layout)
        layout.addWidget(backup_frame)
        
        restore_frame = QWidget()
        restore_layout = QGridLayout()
        
        self.chrome_restore_src = QLineEdit()
        restore_layout.addWidget(QLabel("Thư Mục Sao Lưu:"), 0, 0)
        restore_layout.addWidget(self.chrome_restore_src, 0, 1)
        select_restore_btn = QPushButton("Chọn")
        select_restore_btn.clicked.connect(self.select_chrome_restore_src)
        select_restore_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        restore_layout.addWidget(select_restore_btn, 0, 2)
        
        self.chrome_restore_combo = QComboBox()
        restore_layout.addWidget(QLabel("Khôi Phục Vào:"), 1, 0)
        restore_layout.addWidget(self.chrome_restore_combo, 1, 1)
        self.chrome_restore_combo.addItems(list(self.chrome_profiles.values()))
        
        restore_btn = QPushButton("Khôi Phục Ngay")
        restore_btn.clicked.connect(self.start_chrome_restore)
        restore_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        restore_layout.addWidget(restore_btn, 2, 0, 1, 3)
        restore_frame.setLayout(restore_layout)
        layout.addWidget(restore_frame)
        
        self.chrome_progress = QProgressBar()
        layout.addWidget(QLabel("Tiến Trình:"))
        layout.addWidget(self.chrome_progress)
        
        layout.addStretch()
        self.chrome_tab.setLayout(layout)

    def init_edge_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Sao Lưu & Khôi Phục Edge")
        title.setStyleSheet("font: bold 16pt 'Helvetica'; color: white; background-color: #4a90e2;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        backup_frame = QWidget()
        backup_layout = QGridLayout()
        
        self.edge_profiles = self.get_edge_profiles()
        self.edge_profile_combo = QComboBox()
        self.edge_profile_combo.addItems(list(self.edge_profiles.values()))
        backup_layout.addWidget(QLabel("Chọn Hồ Sơ:"), 0, 0)
        backup_layout.addWidget(self.edge_profile_combo, 0, 1)
        
        self.edge_backup_dest = QLineEdit()
        backup_layout.addWidget(QLabel("Thư Mục Sao Lưu:"), 1, 0)
        backup_layout.addWidget(self.edge_backup_dest, 1, 1)
        select_backup_btn = QPushButton("Chọn")
        select_backup_btn.clicked.connect(self.select_edge_backup_dest)
        select_backup_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        backup_layout.addWidget(select_backup_btn, 1, 2)
        
        backup_btn = QPushButton("Sao Lưu Ngay")
        backup_btn.clicked.connect(self.start_edge_backup)
        backup_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        backup_layout.addWidget(backup_btn, 2, 0, 1, 3)
        backup_frame.setLayout(backup_layout)
        layout.addWidget(backup_frame)
        
        restore_frame = QWidget()
        restore_layout = QGridLayout()
        
        self.edge_restore_src = QLineEdit()
        restore_layout.addWidget(QLabel("Thư Mục Sao Lưu:"), 0, 0)
        restore_layout.addWidget(self.edge_restore_src, 0, 1)
        select_restore_btn = QPushButton("Chọn")
        select_restore_btn.clicked.connect(self.select_edge_restore_src)
        select_restore_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        restore_layout.addWidget(select_restore_btn, 0, 2)
        
        self.edge_restore_combo = QComboBox()
        restore_layout.addWidget(QLabel("Khôi Phục Vào:"), 1, 0)
        restore_layout.addWidget(self.edge_restore_combo, 1, 1)
        self.edge_restore_combo.addItems(list(self.edge_profiles.values()))
        
        restore_btn = QPushButton("Khôi Phục Ngay")
        restore_btn.clicked.connect(self.start_edge_restore)
        restore_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        restore_layout.addWidget(restore_btn, 2, 0, 1, 3)
        restore_frame.setLayout(restore_layout)
        layout.addWidget(restore_frame)
        
        self.edge_progress = QProgressBar()
        layout.addWidget(QLabel("Tiến Trình:"))
        layout.addWidget(self.edge_progress)
        
        layout.addStretch()
        self.edge_tab.setLayout(layout)

    def init_general_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Sao Lưu Dữ Liệu Chung")
        title.setStyleSheet("font: bold 16pt 'Helvetica'; color: white; background-color: #4a90e2;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.general_dest = QLineEdit()
        layout.addWidget(QLabel("Thư Mục Đích:"))
        layout.addWidget(self.general_dest)
        
        select_btn = QPushButton("Chọn")
        select_btn.clicked.connect(self.select_general_dest)
        select_btn.setStyleSheet("background-color: #4a90e2; color: white;")
        select_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        layout.addWidget(select_btn)
        
        grid = QGridLayout()
        self.desktop_cb = QCheckBox("Màn Hình Desktop")
        self.documents_cb = QCheckBox("Tài Liệu")
        self.downloads_cb = QCheckBox("Tải Xuống")
        self.pictures_cb = QCheckBox("Hình Ảnh")
        self.videos_cb = QCheckBox("Video")
        self.favorites_cb = QCheckBox("Yêu Thích")
        self.custom_cb = QCheckBox("Tùy Chọn")
        self.custom_path = QLineEdit()
        self.custom_select_btn = QPushButton("Chọn")
        self.custom_select_btn.clicked.connect(self.select_custom_path)
        self.custom_select_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        
        grid.addWidget(self.desktop_cb, 0, 0)
        grid.addWidget(self.documents_cb, 0, 1)
        grid.addWidget(self.downloads_cb, 1, 0)
        grid.addWidget(self.pictures_cb, 1, 1)
        grid.addWidget(self.videos_cb, 2, 0)
        grid.addWidget(self.favorites_cb, 2, 1)
        grid.addWidget(self.custom_cb, 3, 0)
        grid.addWidget(self.custom_path, 3, 1)
        grid.addWidget(self.custom_select_btn, 3, 2)
        layout.addLayout(grid)
        
        self.general_progress = QProgressBar()
        layout.addWidget(QLabel("Tiến Trình:"))
        layout.addWidget(self.general_progress)
        
        self.status_label = QLabel("Trạng Thái: Chưa Bắt Đầu")
        layout.addWidget(self.status_label)
        
        start_btn = QPushButton("BẮT ĐẦU")
        start_btn.clicked.connect(self.start_general_backup)
        start_btn.setStyleSheet("background-color: #4a90e2; color: white; font: bold 12pt 'Helvetica';")
        start_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'icon.ico')))
        layout.addWidget(start_btn)
        
        layout.addStretch()
        self.general_tab.setLayout(layout)

    def select_zalo_dest(self):
        dest = QFileDialog.getExistingDirectory(self, "Chọn Ổ Đĩa Đích")
        if dest:
            self.zalo_dest.setText(dest)

    def select_chrome_backup_dest(self):
        dest = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Sao Lưu")
        if dest:
            self.chrome_backup_dest.setText(dest)

    def select_chrome_restore_src(self):
        src = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Sao Lưu")
        if src:
            self.chrome_restore_src.setText(src)

    def select_edge_backup_dest(self):
        dest = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Sao Lưu")
        if dest:
            self.edge_backup_dest.setText(dest)

    def select_edge_restore_src(self):
        src = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Sao Lưu")
        if src:
            self.edge_restore_src.setText(src)

    def select_general_dest(self):
        dest = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Đích")
        if dest:
            self.general_dest.setText(dest)

    def select_custom_path(self):
        path = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Tùy Chọn")
        if path:
            self.custom_path.setText(path)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def start_zalo_backup(self):
        if not self.is_admin():
            QMessageBox.critical(self, "Cảnh Báo", "Vui lòng chạy với quyền Quản Trị viên!")
            return
        if not self.zalo_dest.text():
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn ổ đĩa đích!")
            return
            
        self.worker = BackupWorker("zalo", {"dest_drive": self.zalo_dest.text()})
        self.worker.progress.connect(self.zalo_progress.setValue)
        self.worker.finished.connect(lambda msg: QMessageBox.information(self, "Thành Công", msg))
        self.worker.error.connect(lambda msg: QMessageBox.critical(self, "Lỗi", msg))
        self.worker.start()

    def start_chrome_backup(self):
        if not self.chrome_backup_dest.text():
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn thư mục sao lưu!")
            return
            
        profile = list(self.chrome_profiles.keys())[self.chrome_profile_combo.currentIndex()]
        self.worker = BackupWorker("chrome_backup", {
            "src_path": self.get_chrome_data_path(),
            "dest_path": self.chrome_backup_dest.text(),
            "profile": profile
        })
        self.worker.progress.connect(self.chrome_progress.setValue)
        self.worker.finished.connect(lambda msg: QMessageBox.information(self, "Thành Công", msg))
        self.worker.error.connect(lambda msg: QMessageBox.critical(self, "Lỗi", msg))
        self.worker.start()

    def start_chrome_restore(self):
        if not self.chrome_restore_src.text():
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn thư mục sao lưu!")
            return
            
        profile = list(self.chrome_profiles.keys())[self.chrome_restore_combo.currentIndex()]
        self.worker = BackupWorker("chrome_restore", {
            "backup_path": self.chrome_restore_src.text(),
            "dest_path": self.get_chrome_data_path(),
            "profile": profile
        })
        self.worker.progress.connect(self.chrome_progress.setValue)
        self.worker.finished.connect(lambda msg: QMessageBox.information(self, "Thành Công", msg))
        self.worker.error.connect(lambda msg: QMessageBox.critical(self, "Lỗi", msg))
        self.worker.start()

    def start_edge_backup(self):
        if not self.edge_backup_dest.text():
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn thư mục sao lưu!")
            return
            
        profile = list(self.edge_profiles.keys())[self.edge_profile_combo.currentIndex()]
        self.worker = BackupWorker("edge_backup", {
            "src_path": self.get_edge_data_path(),
            "dest_path": self.edge_backup_dest.text(),
            "profile": profile
        })
        self.worker.progress.connect(self.edge_progress.setValue)
        self.worker.finished.connect(lambda msg: QMessageBox.information(self, "Thành Công", msg))
        self.worker.error.connect(lambda msg: QMessageBox.critical(self, "Lỗi", msg))
        self.worker.start()

    def start_edge_restore(self):
        if not self.edge_restore_src.text():
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn thư mục sao lưu!")
            return
            
        profile = list(self.edge_profiles.keys())[self.edge_restore_combo.currentIndex()]
        self.worker = BackupWorker("edge_restore", {
            "backup_path": self.edge_restore_src.text(),
            "dest_path": self.get_edge_data_path(),
            "profile": profile
        })
        self.worker.progress.connect(self.edge_progress.setValue)
        self.worker.finished.connect(lambda msg: QMessageBox.information(self, "Thành Công", msg))
        self.worker.error.connect(lambda msg: QMessageBox.critical(self, "Lỗi", msg))
        self.worker.start()

    def start_general_backup(self):
        if not self.general_dest.text():
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn thư mục đích!")
            return
            
        folders = []
        home = os.path.expanduser('~')
        if self.desktop_cb.isChecked():
            folders.append(("Desktop", os.path.join(home, "Desktop")))
        if self.documents_cb.isChecked():
            folders.append(("Documents", os.path.join(home, "Documents")))
        if self.downloads_cb.isChecked():
            folders.append(("Downloads", os.path.join(home, "Downloads")))
        if self.pictures_cb.isChecked():
            folders.append(("Pictures", os.path.join(home, "Pictures")))
        if self.videos_cb.isChecked():
            folders.append(("Videos", os.path.join(home, "Videos")))
        if self.favorites_cb.isChecked():
            folders.append(("Favorites", os.path.join(home, "Favorites")))
        if self.custom_cb.isChecked() and self.custom_path.text():
            folders.append((os.path.basename(self.custom_path.text()), self.custom_path.text()))
            
        if not folders:
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn ít nhất một thư mục để sao lưu!")
            return
            
        self.status_label.setText("Trạng Thái: Đang Sao Lưu...")
        self.worker = BackupWorker("general", {
            "dest_path": self.general_dest.text(),
            "folders": folders
        })
        self.worker.progress.connect(self.general_progress.setValue)
        self.worker.finished.connect(lambda msg: [self.status_label.setText("Trạng Thái: Hoàn Tất"), QMessageBox.information(self, "Thành Công", msg)])
        self.worker.error.connect(lambda msg: [self.status_label.setText("Trạng Thái: Lỗi"), QMessageBox.critical(self, "Lỗi", msg)])
        self.worker.start()

    def get_chrome_data_path(self):
        if platform.system() == "Windows":
            return os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
        return ""

    def get_edge_data_path(self):
        if platform.system() == "Windows":
            return os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data')
        return ""

    def get_chrome_profiles(self):
        profiles = {}
        user_data_path = self.get_chrome_data_path()
        local_state_path = os.path.join(user_data_path, 'Local State')
        
        if os.path.exists(local_state_path):
            try:
                with open(local_state_path, 'r', encoding='utf-8') as f:
                    local_state = json.load(f)
                    info_cache = local_state.get('profile', {}).get('info_cache', {})
                    for profile_id, info in info_cache.items():
                        profiles[profile_id] = info.get('name', profile_id)
            except:
                pass
        
        if not profiles:
            if os.path.exists(user_data_path):
                for item in os.listdir(user_data_path):
                    if os.path.isdir(os.path.join(user_data_path, item)) and (item.startswith('Profile ') or item == 'Default'):
                        profiles[item] = item
            if not profiles:
                profiles['Default'] = 'Default'
        
        return profiles

    def get_edge_profiles(self):
        profiles = {}
        user_data_path = self.get_edge_data_path()
        local_state_path = os.path.join(user_data_path, 'Local State')
        
        if os.path.exists(local_state_path):
            try:
                with open(local_state_path, 'r', encoding='utf-8') as f:
                    local_state = json.load(f)
                    info_cache = local_state.get('profile', {}).get('info_cache', {})
                    for profile_id, info in info_cache.items():
                        profiles[profile_id] = info.get('name', profile_id)
            except:
                pass
        
        if not profiles:
            if os.path.exists(user_data_path):
                for item in os.listdir(user_data_path):
                    if os.path.isdir(os.path.join(user_data_path, item)) and (item.startswith('Profile ') or item == 'Default'):
                        profiles[item] = item
            if not profiles:
                profiles['Default'] = 'Default'
        
        return profiles

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackupTool()
    window.show()
    sys.exit(app.exec_())