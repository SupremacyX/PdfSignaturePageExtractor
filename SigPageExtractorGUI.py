import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QFileDialog, QDialog, QLabel, QLineEdit, QHBoxLayout,
    QMessageBox
)
from SignaturePageExtractor import split_pdf_by_page

class PageRangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_page = None
        self.end_page = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("选择页码范围")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        
        # 起始页输入框及标签
        hbox_start = QHBoxLayout()
        label_start = QLabel("起始页:")
        self.start_input = QLineEdit()
        self.start_input.setText("1")
        hbox_start.addWidget(label_start)
        hbox_start.addWidget(self.start_input)
        
        # 结束页输入框及标签
        hbox_end = QHBoxLayout()
        label_end = QLabel("结束页:")
        self.end_input = QLineEdit()
        self.end_input.setText("1")
        hbox_end.addWidget(label_end)
        hbox_end.addWidget(self.end_input)
        
        # 确认按钮
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.clicked.connect(self.confirm)
        
        layout.addLayout(hbox_start)
        layout.addLayout(hbox_end)
        layout.addWidget(self.confirm_btn)
        
        self.setLayout(layout)
        
    def confirm(self):
        self.start_page = self.start_input.text()
        self.end_page = self.end_input.text()
        self.accept()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.pdf_file = ""
        self.output_dir = ""
        self.start_page = ""
        self.end_page = ""
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("PDF处理工具")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
        
        # 选择文件按钮
        self.btn_select_file = QPushButton("选择文件")
        self.btn_select_file.clicked.connect(self.select_file)
        
        # 选择目录按钮
        self.btn_select_dir = QPushButton("选择目录")
        self.btn_select_dir.clicked.connect(self.select_directory)
        
        # 开始运行按钮
        self.btn_start = QPushButton("开始运行")
        self.btn_start.clicked.connect(self.start_run)
        
        layout.addWidget(self.btn_select_file)
        layout.addWidget(self.btn_select_dir)
        layout.addWidget(self.btn_start)
        
        self.setLayout(layout)
        
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择PDF文件", "", "PDF Files (*.pdf)")
        if file_path:
            self.pdf_file = file_path
            print("选择的PDF文件:", self.pdf_file)
            # 选择文件后弹出页码输入对话框
            dialog = PageRangeDialog(self)
            if dialog.exec_():
                self.start_page = dialog.start_page
                self.end_page = dialog.end_page
                print("起始页:", self.start_page, "结束页:", self.end_page)
                
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录", "")
        if directory:
            self.output_dir = directory
            print("选择的输出目录:", self.output_dir)
            
    def start_run(self):
        if not self.pdf_file:
            QMessageBox.warning(self, "错误", "请先选择PDF文件")
            return
        if not self.output_dir:
            QMessageBox.warning(self, "错误", "请先选择输出目录")
            return
        if not self.start_page or not self.end_page:
            QMessageBox.warning(self, "错误", "请先选择页码范围")
            return
        
        # 这里可以添加后续处理逻辑，例如PDF拆分
        print("开始运行！")
        print("PDF文件:", self.pdf_file)
        print("输出目录:", self.output_dir)
        print("起始页:", self.start_page)
        print("结束页:", self.end_page)
        try:                    
            split_pdf_by_page(self.pdf_file, int(self.start_page), int(self.end_page), self.output_dir)
            QMessageBox.information(self, "成功", f"处理完成！\n输出目录：{self.output_dir}")            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"处理失败：{str(e)}")
        finally:
            sys.exit(app.exec_())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Comment out or remove this line if you don't need static files
    # app.mount("/static", StaticFiles(directory="static"), name="static")
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
