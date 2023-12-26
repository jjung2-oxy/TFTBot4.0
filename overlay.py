import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Overlay(QMainWindow):
    def __init__(self, app, screen_scaling=1, opacity=1, parent=None):
        # APP INIT
        super().__init__(parent)
        self.app = app
        self.screen_scaling = screen_scaling
        self.opacity = opacity    

        # WINDOW ATTRIBUTES
        self.drawCloseButton()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.show()
        self.activateWindow()
        self.raise_()

        # UPDATE SIGNAL VARS
        self.string_dict = {}

    def update_overlay(self, stat_dict):
        self.string_dict = stat_dict
        self.update()

    def paintEvent(self, event=None):
        try: 
            painter = QPainter(self)
            self.drawNewTextBox(painter, self.string_dict)
        except Exception as e:
            print(f"Error in paintEvent: {e}", file=sys.stderr)

    def drawCloseButton(self):
        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width(), screen.height() - 200)
        self.move(0, 0)
        self.pushButton = QPushButton(self)
        self.pushButton.setGeometry(screen.width() - 100, 10, 80, 30)
        self.pushButton.setText("Close")
        self.pushButton.clicked.connect(self.close)

    def drawNewTextBox(self, painter, stats_dict):

        # Set the font for the text
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        painter.setOpacity(1.0)
        painter.setBrush(Qt.black)
        painter.setPen(QPen(Qt.white))

        # Calculate the required height and maximum width of the textbox
        font_metrics = QFontMetrics(font)
        max_text_width = 0
        textbox_x, textbox_y = 10, 10
        text_y_offset = 20
        y = textbox_y + text_y_offset

        textbox_height = text_y_offset  # Start with the offset as initial height
        for cost, champs in stats_dict.items():
            line = f"Top champions for cost {cost}:"
            max_text_width = max(max_text_width, font_metrics.width(line))
            textbox_height += text_y_offset  # Add space for the cost header
            for name, count in champs:
                remaining_champs = self.champPool[f'{cost}_cost'] - count
                line = f"  {name} - {count} tallied, {remaining_champs} remaining"
                max_text_width = max(max_text_width, font_metrics.width(line))
                textbox_height += text_y_offset  # Add space for each champion

        # Adjust the width of the textbox
        textbox_width = max_text_width + 20  # Add some padding

        # Draw the textbox
        painter.drawRect(textbox_x, textbox_y, textbox_width, textbox_height)

        # Draw the text inside the textbox
        y = textbox_y + text_y_offset
        for cost, champs in stats_dict.items():
            painter.drawText(textbox_x + 10, y, f"Top champions for cost {cost}:")
            y += text_y_offset
            for name, count in champs:
                remaining_champs = self.champPool[f'{cost}_cost'] - count
                painter.drawText(textbox_x + 10, y, f"  {name} - {count} tallied, {remaining_champs} remaining")
                y += text_y_offset

    def run(self):
        return self.app.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create the QApplication instance first
    overlay = Overlay()
    sys.exit(app.exec_())
