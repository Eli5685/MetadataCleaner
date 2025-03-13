#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QFileDialog, QTextEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QProcess

class MetadataCleaner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.exiftool_path = self.find_exiftool()
        self.initUI()
        
    def find_exiftool(self):
        """Проверка наличия ExifTool в системе или по заданному пути"""
        # Проверяем по указанному пути
        specific_path = "c:\\exiftool\\exiftool.exe"
        if os.path.exists(specific_path):
            return specific_path
            
        # Пробуем альтернативные пути
        alt_paths = [
            "c:\\exiftool\\exiftool(-k).exe",  # В Windows иногда файл называется так
            "c:\\exiftool\\exiftool.exe",
            "c:\\exiftool"
        ]
        
        for path in alt_paths:
            if os.path.exists(path):
                return path
                
        # Проверяем, доступен ли ExifTool в системном пути
        try:
            result = subprocess.run(['exiftool', '-ver'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
            if result.returncode == 0:
                return 'exiftool'
        except FileNotFoundError:
            # ExifTool не найден
            QMessageBox.warning(self, "Предупреждение", 
                               "ExifTool не найден в системе. Пожалуйста, убедитесь, что файл exiftool.exe находится в папке c:\\exiftool или добавьте ExifTool в переменную PATH.")
            return None
    
    def initUI(self):
        self.setWindowTitle('Очистка метаданных')
        self.setGeometry(300, 300, 800, 600)
        
        # Основной виджет и компоновка
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Информация о программе
        info_label = QLabel('Программа для просмотра и удаления метаданных из фото и видео файлов')
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Кнопки выбора файла и очистки метаданных
        button_layout = QHBoxLayout()
        
        self.select_button = QPushButton('Выбрать файл')
        self.select_button.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_button)
        
        self.clear_button = QPushButton('Очистить метаданные')
        self.clear_button.clicked.connect(self.clear_metadata)
        self.clear_button.setEnabled(False)
        button_layout.addWidget(self.clear_button)
        
        self.detailed_button = QPushButton('Показать подробные метаданные')
        self.detailed_button.clicked.connect(self.show_detailed_metadata)
        self.detailed_button.setEnabled(False)
        button_layout.addWidget(self.detailed_button)
        
        main_layout.addLayout(button_layout)
        
        # Информация о выбранном файле
        self.file_info = QLabel('Файл не выбран')
        main_layout.addWidget(self.file_info)
        
        # Информация о статусе ExifTool
        self.exiftool_info = QLabel()
        if self.exiftool_path:
            self.exiftool_info.setText(f'ExifTool найден: {self.exiftool_path}')
        else:
            self.exiftool_info.setText('ExifTool не найден. Установите ExifTool для работы с метаданными.')
            self.exiftool_info.setStyleSheet('color: red;')
        self.exiftool_info.setWordWrap(True)
        main_layout.addWidget(self.exiftool_info)
        
        # Область для отображения метаданных
        self.metadata_display = QTextEdit()
        self.metadata_display.setReadOnly(True)
        main_layout.addWidget(self.metadata_display)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def select_file(self):
        """Выбор файла и отображение его метаданных"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            'Выберите файл',
            '',
            'Изображения и видео (*.jpg *.jpeg *.png *.tiff *.mp4 *.mov *.avi)'
        )
        
        if file_path:
            self.current_file = file_path
            self.file_info.setText(f'Выбран файл: {os.path.basename(file_path)}')
            self.show_metadata(file_path)
            self.clear_button.setEnabled(True)
            self.detailed_button.setEnabled(True)
    
    def show_metadata(self, file_path):
        """Отображение метаданных выбранного файла"""
        if not self.exiftool_path:
            self.metadata_display.setText('ExifTool не найден. Установите ExifTool для работы с метаданными.')
            return
            
        try:
            # Запускаем ExifTool для получения метаданных
            process = QProcess()
            # Если путь содержит имя exe-файла, используем его напрямую 
            if self.exiftool_path.endswith('.exe'):
                process.start(self.exiftool_path, [file_path])
            else:
                # Иначе предполагаем, что это команда или путь к каталогу
                if os.path.isdir(self.exiftool_path):
                    # Если это путь к каталогу, ищем exiftool.exe в нем
                    exe_path = os.path.join(self.exiftool_path, 'exiftool.exe')
                    alt_exe_path = os.path.join(self.exiftool_path, 'exiftool(-k).exe')
                    
                    if os.path.exists(exe_path):
                        process.start(exe_path, [file_path])
                    elif os.path.exists(alt_exe_path):
                        process.start(alt_exe_path, [file_path])
                    else:
                        self.metadata_display.setText(f'ExifTool не найден в указанном каталоге: {self.exiftool_path}')
                        return
                else:
                    # Если это просто команда (как 'exiftool')
                    process.start(self.exiftool_path, [file_path])
                    
            process.waitForFinished()
            
            output = process.readAllStandardOutput().data().decode('utf-8')
            if output:
                self.metadata_display.setText(output)
            else:
                self.metadata_display.setText('Метаданные не найдены или произошла ошибка.')
        except Exception as e:
            self.metadata_display.setText(f'Ошибка при чтении метаданных: {str(e)}')
    
    def show_detailed_metadata(self):
        """Показать подробные метаданные"""
        if not self.current_file or not self.exiftool_path:
            return
            
        try:
            # Запускаем ExifTool с параметрами для отображения всех метаданных
            process = QProcess()
            
            # Подготовка команды
            exe_path = self.exiftool_path
            
            if os.path.isdir(self.exiftool_path):
                standard_exe = os.path.join(self.exiftool_path, 'exiftool.exe')
                alt_exe = os.path.join(self.exiftool_path, 'exiftool(-k).exe')
                
                if os.path.exists(standard_exe):
                    exe_path = standard_exe
                elif os.path.exists(alt_exe):
                    exe_path = alt_exe
                else:
                    self.metadata_display.setText(f'ExifTool не найден в указанном каталоге: {self.exiftool_path}')
                    return
            
            # Параметры для отображения всех метаданных, включая бинарные данные в шестнадцатеричном формате
            process.start(exe_path, ['-a', '-u', '-g1', self.current_file])
            process.waitForFinished()
            
            output = process.readAllStandardOutput().data().decode('utf-8')
            if output:
                self.metadata_display.setText(output)
            else:
                self.metadata_display.setText('Метаданные не найдены или произошла ошибка.')
        except Exception as e:
            self.metadata_display.setText(f'Ошибка при чтении подробных метаданных: {str(e)}')
    
    def clear_metadata(self):
        """Очистка метаданных из выбранного файла"""
        if not self.current_file or not self.exiftool_path:
            return
            
        reply = QMessageBox.question(
            self, 
            'Подтверждение', 
            'Вы уверены, что хотите удалить все метаданные из файла?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Запускаем ExifTool для удаления всех метаданных
                process = QProcess()
                
                # Подготовка команды в зависимости от типа пути
                exe_path = self.exiftool_path
                
                # Если путь - это каталог, найти exiftool.exe в нем
                if os.path.isdir(self.exiftool_path):
                    standard_exe = os.path.join(self.exiftool_path, 'exiftool.exe')
                    alt_exe = os.path.join(self.exiftool_path, 'exiftool(-k).exe')
                    
                    if os.path.exists(standard_exe):
                        exe_path = standard_exe
                    elif os.path.exists(alt_exe):
                        exe_path = alt_exe
                    else:
                        QMessageBox.critical(self, 'Ошибка', f'ExifTool не найден в указанном каталоге: {self.exiftool_path}')
                        return
                
                # Параметр -all= удаляет все метаданные
                process.start(exe_path, ['-all=', '-overwrite_original', self.current_file])
                process.waitForFinished()
                
                error = process.readAllStandardError().data().decode('utf-8')
                if error and 'error' in error.lower():
                    QMessageBox.critical(self, 'Ошибка', f'Ошибка при очистке метаданных: {error}')
                else:
                    QMessageBox.information(self, 'Успех', 'Метаданные успешно удалены!')
                    # Обновляем отображение метаданных
                    self.show_metadata(self.current_file)
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Ошибка при очистке метаданных: {str(e)}')

def main():
    app = QApplication(sys.argv)
    window = MetadataCleaner()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 