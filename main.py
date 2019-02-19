import sys
from main_window import *
from proxy_style import *
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    faces_number = -1
    draw_rectangles = False

    if len(sys.argv) == 2:
        if sys.argv[1].lower() == "true":
            draw_rectangles = True
        else:
            draw_rectangles = False
    elif len(sys.argv) == 3:
        if sys.argv[1].lower() == "true":
            draw_rectangles = True
        else:
            draw_rectangles = False
        try:
            faces_number = int(sys.argv[2])
            if faces_number < 0:
                faces_number = -1
        except:
            faces_number = -1

    app = QApplication(sys.argv)
    myStyle = MyProxyStyle('Fusion')
    app.setStyle(myStyle)

    window = MainWindow(faces_number, draw_rectangles)
    window.show()
    sys.exit(app.exec_())