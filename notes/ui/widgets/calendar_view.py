from PySide6.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel, QHBoxLayout
from PySide6.QtCore import QDate

class CalendarViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        layout.addWidget(self.calendar)
        
        # Selected Date Info
        self.info_label = QLabel("选择日期查看日志")
        layout.addWidget(self.info_label)
        
        # Log List (Placeholder)
        self.log_list = QLabel("暂无日志")
        layout.addWidget(self.log_list)
        
    def on_date_selected(self, date):
        self.info_label.setText(f"选中日期: {date.toString('yyyy-MM-dd')}")
        # Here query logs for the date
