from PySide6.QtCore import QObject, QTimer, Signal

class PomodoroTimer(QObject):
    tick = Signal(int) # remaining seconds
    finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timeout)
        self.remaining_time = 0
        self.is_running = False
        
    def start(self, minutes):
        self.remaining_time = minutes * 60
        self.timer.start(1000)
        self.is_running = True
        self.tick.emit(self.remaining_time)
        
    def pause(self):
        self.timer.stop()
        self.is_running = False
        
    def resume(self):
        if self.remaining_time > 0:
            self.timer.start(1000)
            self.is_running = True
            
    def stop(self):
        self.timer.stop()
        self.is_running = False
        self.remaining_time = 0
        self.tick.emit(0)
        
    def on_timeout(self):
        self.remaining_time -= 1
        self.tick.emit(self.remaining_time)
        
        if self.remaining_time <= 0:
            self.timer.stop()
            self.is_running = False
            self.finished.emit()

# Global instance can be managed here or in the UI
