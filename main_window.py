from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QWidget, QStatusBar, \
    QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup, QPushButton, QDesktopWidget, QSizePolicy
from cam import *
import stickers
from detection import *


class MainWindow(QMainWindow):
    """
    Represents main window that extends QMainWindow and that is used for interaction with user.
    """
    def __init__(self, faces_number, draw_rectangles, parent=None):
        """Initializes main window.

        :param self: self
        :param faces_number: number of expected faces in frame
        :param draw_rectangles: indicator whether rectangles that bound detected faces should be drawn
        :param parent: parent of window
        """
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("FaceSnap")
        self.setWindowIcon(QIcon("stickers/icon.png"))
        self.faces_number = faces_number
        self.draw_rectangles = draw_rectangles
        self.file_name = ""
        self.chosen_filter = ""
        self.processing = False

        self.layout = QVBoxLayout()  # layout for the central widget
        widget = QWidget(self)  # central widget
        widget.setLayout(self.layout)
        self.setGeometry(0, 0, 650, 550)
        self.center_on_screen()

        self.existing_video_layout = QHBoxLayout()  # layout for existing video
        self.existing_video_widget = QWidget()
        self.existing_video_widget.setLayout(self.existing_video_layout)

        self.cam_video_layout = QHBoxLayout()       # layout for recorder video
        self.cam_video_widget = QWidget()
        self.cam_video_widget.setLayout(self.cam_video_layout)

        self.choice_group = QButtonGroup(widget)    # radio button group for input file choice
        self.filter_group = QButtonGroup(widget)    # radio button group for filter choice

        self.existing_video_radio = QRadioButton("Choose existing video")
        self.existing_video_button = QPushButton("Choose video file")

        self.cam_video_radio = QRadioButton("Capture video with camera")
        self.cam_video_button = QPushButton("Record video")

        self.mask_button = QRadioButton()
        self.cat_button = QRadioButton()
        self.ears_button = QRadioButton()
        self.flowers_button = QRadioButton()
        self.mustache_button = QRadioButton()
        self.glasses_button = QRadioButton()
        self.mouse_button = QRadioButton()
        self.pirate_button = QRadioButton()
        self.rainbow_button = QRadioButton()

        self.init_video_choice()
        self.init_filter_choice()

        self.process_button = QPushButton("Process video")
        self.process_button.clicked.connect(self.process_chosen_video)
        self.layout.addWidget(QWidget())
        self.layout.addWidget(QWidget())
        self.layout.addWidget(QWidget())
        self.layout.addWidget(self.process_button)
        self.layout.addWidget(QWidget())
        self.status = QStatusBar()
        self.layout.addWidget(self.status)
        self.setCentralWidget(widget)

    def center_on_screen(self):
        """Centers window on screen.

        :param self: self
        """
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 4 + 20) - (self.frameSize().height() / 2))

    def init_video_choice(self):
        """Initializes radio button group for video choice.

        :param self: self
        """
        self.cam_video_radio.clicked.connect(self.cam_video_chosen)
        self.choice_group.addButton(self.cam_video_radio)

        self.existing_video_radio.clicked.connect(self.existing_video_chosen)
        self.choice_group.addButton(self.existing_video_radio)

        self.existing_video_button.clicked.connect(self.open_file)
        self.existing_video_layout.addWidget(self.existing_video_radio)
        self.existing_video_layout.addWidget(self.existing_video_button)

        self.cam_video_button.clicked.connect(self.record_video)
        self.cam_video_layout.addWidget(self.cam_video_radio)
        self.cam_video_layout.addWidget(self.cam_video_button)

        self.layout.addWidget(self.existing_video_widget)
        self.layout.addWidget(self.cam_video_widget)

        self.existing_video_radio.click()

    def init_filter_choice(self):
        """Initializes radio button group for filter choice.

        :param self: self
        """
        self.layout.addWidget(QWidget())
        self.layout.addWidget(QWidget())

        sticker_rows = QVBoxLayout()
        first_row_layout = QHBoxLayout()
        first_row_widget = QWidget()
        first_row_widget.setLayout(first_row_layout)
        second_row_layout = QHBoxLayout()
        second_row_widget = QWidget()
        second_row_widget.setLayout(second_row_layout)
        third_row_layout = QHBoxLayout()
        third_row_widget = QWidget()
        third_row_widget.setLayout(third_row_layout)

        sticker_rows.addWidget(first_row_widget)
        sticker_rows.addWidget(second_row_widget)
        sticker_rows.addWidget(third_row_widget)
        filter_widget = QWidget()
        filter_widget.setLayout(sticker_rows)

        self.init_first_row_filters(first_row_layout)
        self.init_second_row_filters(second_row_layout)
        self.init_third_row_filters(third_row_layout)

        self.layout.addWidget(filter_widget)

    def init_first_row_filters(self, first_row_layout):
        """Initializes first row of radio button group for filter choice.

        :param self: self
        :param first_row_layout: layout for first row of filters
        """
        self.mask_button.clicked.connect(self.filter_chosen)
        self.filter_group.addButton(self.mask_button)
        self.mask_button.setIcon(QIcon(stickers.mask_sticker()))
        first_row_layout.addWidget(self.mask_button)    # add mask to widget

        first_row_layout.addWidget(QWidget())           # add empty space

        self.cat_button.clicked.connect(self.filter_chosen)
        self.filter_group.addButton(self.cat_button)
        self.cat_button.setIcon(QIcon(stickers.cat_sticker()))
        first_row_layout.addWidget(self.cat_button)     # add cat to widget

        first_row_layout.addWidget(QWidget())           # add empty space

        self.ears_button.clicked.connect(self.filter_chosen)
        self.filter_group.addButton(self.ears_button)
        self.ears_button.setIcon(QIcon(stickers.ears_sticker()))
        first_row_layout.addWidget(self.ears_button)    # add ears to widget

    def init_second_row_filters(self, second_row_layout):
        """Initializes second row of radio button group for filter choice.

        :param self: self
        :param second_row_layout: layout for second row of filters
        """
        self.flowers_button.clicked.connect(self.filter_chosen)
        self.filter_group.addButton(self.flowers_button)
        self.flowers_button.setIcon(QIcon(stickers.flowers_sticker()))
        second_row_layout.addWidget(self.flowers_button)   # add flowers to widget

        second_row_layout.addWidget(QWidget())             # add empty space

        self.mustache_button.clicked.connect(self.filter_chosen)
        self.filter_group.addButton(self.mustache_button)
        self.mustache_button.setIcon(QIcon(stickers.mustache_sticker()))
        second_row_layout.addWidget(self.mustache_button)   # add mustache to widget

        second_row_layout.addWidget(QWidget())              # add empty space

        self.glasses_button.clicked.connect(self.filter_chosen)
        self.filter_group.addButton(self.glasses_button)
        self.glasses_button.setIcon(QIcon(stickers.glasses_sticker()))
        second_row_layout.addWidget(self.glasses_button)    # add glasses to widget

    def init_third_row_filters(self, third_row_layout):
        """Initializes third row of radio button group for filter choice.

        :param self: self
        :param third_row_layout: layout for third row of filters
        """
        self.mouse_button.clicked.connect(self.filter_chosen)
        self.filter_group.addButton(self.mouse_button)
        self.mouse_button.setIcon(QIcon(stickers.mouse_sticker()))
        third_row_layout.addWidget(self.mouse_button)       # add mouse to wiget

        third_row_layout.addWidget(QWidget())               # add empty space

        self.pirate_button.clicked.connect(self.filter_chosen)
        self.filter_group.addButton(self.pirate_button)
        self.pirate_button.setIcon(QIcon(stickers.pirate_sticker()))
        third_row_layout.addWidget(self.pirate_button)      # add pirate to widget

        third_row_layout.addWidget(QWidget())               # add empty space

        self.rainbow_button.clicked.connect(self.filter_chosen)
        self.filter_group.addButton(self.rainbow_button)
        self.rainbow_button.setIcon(QIcon(stickers.rainbow_sticker()))
        third_row_layout.addWidget(self.rainbow_button)     # add rainbow to widget

    def filter_chosen(self):
        """Detects which filter is chosen.

        :param self: self
        """
        if self.mask_button.isChecked():
            self.chosen_filter = "mask"
        elif self.cat_button.isChecked():
            self.chosen_filter = "cat"
        elif self.ears_button.isChecked():
            self.chosen_filter = "ears"
        elif self.flowers_button.isChecked():
            self.chosen_filter = "flowers"
        elif self.mustache_button.isChecked():
            self.chosen_filter = "mustache"
        elif self.glasses_button.isChecked():
            self.chosen_filter = "glasses"
        elif self.mouse_button.isChecked():
            self.chosen_filter = "mouse"
        elif self.pirate_button.isChecked():
            self.chosen_filter = "pirate"
        elif self.rainbow_button.isChecked():
            self.chosen_filter = "rainbow"
        else:
            self.chosen_filter = ""

    def process_chosen_video(self):
        """Starts processing chosen video and informs user about process success.

        :param self: self
        """
        if self.file_name == "":
            print("Video for processing is not chosen!")
            self.status.showMessage("Video for processing is not chosen!")
        else:
            if self.processing:
                self.status.showMessage("Processing video in progress!")
            else:
                self.processing = True
                self.status.showMessage("Processing video in progress!")
                if process_video(self.file_name, self.faces_number, self.draw_rectangles, self.chosen_filter, self):
                    self.status.showMessage("Processing video is successful!")
                    self.processing = False
                else:
                    self.status.showMessage("Error opening video!")
                    self.processing = False

    def existing_video_chosen(self):
        """Disables cam video button and enables existing video button.

        :param self: self
        """
        self.cam_video_button.setEnabled(False)
        self.existing_video_button.setEnabled(True)

    def cam_video_chosen(self):
        """Enables cam video button and disables existing video button.

        :param self: self
        """
        self.cam_video_button.setEnabled(True)
        self.existing_video_button.setEnabled(False)

    def open_file(self):
        """Opens dialog for file choice.

        :param self: self
        """
        self.file_name, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath())
        if self.file_name != "":
            print(self.file_name)
            self.status.showMessage("Video successfully chosen!")

    def record_video(self):
        """Opens dialog for directory choice where file is saved.

        :param self: self
        """
        self.file_name = str(QFileDialog.getExistingDirectory(self, "Select Directory Where Video Will Be Saved",
                                                              QDir.homePath()))
        if self.file_name != '':
            self.file_name += "/output_video.avi"
            print(self.file_name)
            self.file_name = record_from_camera(self.file_name, self)
            self.status.showMessage("Video successfully recorded!")