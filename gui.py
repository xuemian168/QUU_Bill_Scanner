import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                           QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                           QProgressBar, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from main import extract_info_from_pdf

class WorkerThread(QThread):
    """Worker thread for processing PDF files."""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        try:
            results = []
            pdf_files = [f for f in os.listdir(self.directory) if f.endswith('.pdf')]
            total_files = len(pdf_files)

            if total_files == 0:
                self.error.emit("No PDF files found in the selected directory.")
                return

            for i, pdf_file in enumerate(pdf_files, 1):
                pdf_path = os.path.join(self.directory, pdf_file)
                self.status.emit(f"Processing {pdf_file}...")
                
                try:
                    info = extract_info_from_pdf(pdf_path)
                    if info:
                        results.append(info)
                except Exception as e:
                    self.status.text.emit(f"Error processing {pdf_file}: {str(e)}")
                
                self.progress.emit(int((i / total_files) * 100))

            self.finished.emit(results)
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QUU Water Bill Data Extractor")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add title
        title = QLabel("QUU Water Bill Data Extractor")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Add description
        description = QLabel("Select a folder containing QUU water bill PDFs to process.")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)

        # Add requirements section
        requirements = QLabel("Important Requirements:")
        requirements.setStyleSheet("font-weight: bold; color: #D35400;")
        layout.addWidget(requirements)

        requirements_list = QLabel(
            "• The bill information MUST be on the first page of the PDF\n"
            "• Only standard QUU water bill format is supported\n"
            "• PDF files must not be password-protected or secured\n"
            "• Each PDF should contain only one bill"
        )
        requirements_list.setStyleSheet("color: #D35400;")
        layout.addWidget(requirements_list)

        # Create button layout
        button_layout = QHBoxLayout()
        
        # Select folder button
        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)
        self.select_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #3498db;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        button_layout.addWidget(self.select_button)
        
        # Process button
        self.process_button = QPushButton("Process Bills")
        self.process_button.clicked.connect(self.process_files)
        self.process_button.setEnabled(False)
        self.process_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        button_layout.addWidget(self.process_button)
        
        layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Status text area
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMinimumHeight(200)
        self.status_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.status_text)

        # Selected folder label
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setWordWrap(True)
        self.folder_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(self.folder_label)

        # Add copyright notice
        copyright_label = QLabel("© 2025 ICT.RUN")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 12px;
            padding: 10px;
            border-top: 1px solid #bdc3c7;
            margin-top: 10px;
        """)
        layout.addWidget(copyright_label)

        self.selected_folder = None

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.selected_folder = folder
            pdf_files = [f for f in os.listdir(folder) if f.endswith('.pdf')]
            pdf_count = len(pdf_files)
            
            # Update folder label and status
            self.folder_label.setText(f"Selected folder: {folder}")
            self.status_text.clear()
            self.status_text.append(f"✅ Folder selected successfully!")
            self.status_text.append(f"📁 Found {pdf_count} PDF files in the folder\n")
            
            # Show requirements reminder
            self.status_text.append("⚠️ Important Requirements:")
            self.status_text.append("• The bill information MUST be on the first page of the PDF")
            self.status_text.append("• Only standard QUU water bill format is supported")
            self.status_text.append("• PDF files must not be password-protected or secured")
            self.status_text.append("• Each PDF should contain only one bill\n")
            
            if pdf_count > 0:
                self.status_text.append("Ready to process files. Click 'Process Bills' to start.")
                self.process_button.setEnabled(True)
            else:
                self.status_text.append("❌ No PDF files found in the selected folder!")
                self.process_button.setEnabled(False)
            
            self.progress_bar.setVisible(False)

    def process_files(self):
        if not self.selected_folder:
            return

        self.select_button.setEnabled(False)
        self.process_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_text.clear()
        self.status_text.append("🔄 Starting processing...\n")

        # Create and start worker thread
        self.worker = WorkerThread(self.selected_folder)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.processing_finished)
        self.worker.error.connect(self.show_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_text.append(message)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.select_button.setEnabled(True)
        self.process_button.setEnabled(True)
        self.progress_bar.setVisible(False)

    def processing_finished(self, results):
        if not results:
            self.show_error("No data was extracted from the PDF files.")
            return

        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.selected_folder, f"water_usage_data_{timestamp}.csv")

        try:
            # Save results to CSV
            import csv
            fieldnames = [
                'filename', 'full_address', 'street_number', 'street_name', 
                'suburb', 'postcode', 'total_due', 'due_date', 'water_usage_kl',
                'days_charged', 'current_period_daily_usage', 'last_year_daily_usage'
            ]
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for result in results:
                    writer.writerow(result)

            self.status_text.append(f"\n✅ Processing complete!")
            self.status_text.append(f"📊 Processed {len(results)} files successfully")
            self.status_text.append(f"💾 Results saved to: {output_file}")

            # Show success message with file location
            QMessageBox.information(
                self,
                "Success",
                f"✅ Processing complete!\n\n📊 Processed {len(results)} files.\n💾 Results saved to:\n{output_file}"
            )
        except Exception as e:
            self.show_error(f"Error saving results: {str(e)}")

        self.select_button.setEnabled(True)
        self.process_button.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    
    # Set style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 