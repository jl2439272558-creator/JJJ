import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'worklog_desktop'))

from PySide6.QtWidgets import QApplication
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from ui.main_window import MainWindow
from ui.styles.themes import ThemeManager
from core.database import init_db

def main():
    # Initialize Database
    init_db()
    
    # Create Application
    app = QApplication(sys.argv)
    app.setApplicationName("WarmWorkLog")
    
    # Single Instance Check
    server_name = "WarmWorkLogSingleInstance"
    socket = QLocalSocket()
    socket.connectToServer(server_name)
    
    if socket.waitForConnected(500):
        # Another instance is running
        print("Another instance is running. Activating it...")
        socket.write(b"SHOW")
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
        sys.exit(0)
    
    # If we are here, we are the primary instance
    # Clean up any leftover server file/pipe from a crash
    QLocalServer.removeServer(server_name)
    
    # Start Local Server
    server = QLocalServer()
    if not server.listen(server_name):
        print(f"Failed to start local server: {server.errorString()}")
    
    # Apply Theme
    ThemeManager.apply_theme(app)
    
    # Create and Show Main Window
    window = MainWindow()
    window.show()
    
    # Handle incoming connections (requests to show window)
    def handle_new_connection():
        client_socket = server.nextPendingConnection()
        if client_socket:
            client_socket.readyRead.connect(lambda: handle_client_data(client_socket))

    def handle_client_data(client_socket):
        data = client_socket.readAll().data()
        if data == b"SHOW":
            # Activate window
            # If minimized/hidden to tray, show it
            window.setWindowState(window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            window.show() # In case it was hidden
            window.raise_() # Bring to front
            window.activateWindow() # Request focus
            
            # If using dock/hidden mode, verify it expands? 
            # MainWindow handles animations, but show() should be enough to trigger visibility
            
    server.newConnection.connect(handle_new_connection)
    
    # Ensure Qt is imported for WindowState constants
    from PySide6.QtCore import Qt
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
