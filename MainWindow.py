##
## MIT License
##
## Copyright (c) 2022 Żywko Szymon
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
##


import PyQt5
from PyQt5.QtCore import (Qt, pyqtSlot)

from PyQt5.QtWidgets import (QSlider, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QMessageBox,
                             QCheckBox)
from MapViewer import MapViewer
from MyWidgets import PatternMenu, PlayPauseButton, SandGenerateMethodMenu


class MainWindow(QWidget):
    """Main window controller

    Attributes:
        model         reference to an object of class GameOfLife (the model)
        loop        reference to an object of class GolLoop (the main loop of the game)
        viewer      custom widget to show the Game of Life model
        ...some graphical elements
    """

    def __init__(self, model, loop):
        super().__init__()

        self.model = model
        self.loop = loop
        self.init_ui()

    def init_ui(self):
        """Method to initialize the UI: layouts and components"""
        self.setWindowTitle("Falling Sand")
        self.viewer = MapViewer()
        self.viewer.resize(800, 600)
        self.viewer.set_model(self.model)
        self.loop.timeout.connect(self.viewer.updateView)

        self.play_pause_button = PlayPauseButton()

        self.reset = QPushButton()
        self.reset.setText("Reset")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(10)
        self.slider.setMaximum(1000)
        self.slider.setValue(910)
        self.slider.setTickInterval(10)
        self.slider.setTickPosition(QSlider.TicksBelow)

        self.menu_label = QLabel("Known Patterns: ")
        self.menu = PatternMenu()
        self.menu.currentTextChanged.connect(self.change_pattern)

        self.menu_sand_label = QLabel("Sand genarete types")
        self.menu_sand = SandGenerateMethodMenu()
        self.menu_sand.currentTextChanged.connect(self.change_sand_generator)
        self.generate_sand_button = QPushButton("Generate")
        self.generate_sand_button.clicked.connect(self.generate_clicked)

        self.nextStep = QPushButton()
        self.nextStep.setText("Next Step")
        self.nextStep.clicked.connect(self.next_clicked)

        self.prevStep = QPushButton()
        self.prevStep.setText("Previous Step")
        self.prevStep.clicked.connect(self.prev_clicked)

        top_h_box = QHBoxLayout()
        top_h_box.addWidget(self.menu_label)
        top_h_box.addWidget(self.menu)
        top_h_box.addStretch()
        top_h_box.addWidget(self.menu_sand_label)
        top_h_box.addWidget(self.menu_sand)
        top_h_box.addWidget(self.generate_sand_button)

        bottom_h_box = QHBoxLayout()
        bottom_h_box.addWidget(self.play_pause_button)
        bottom_h_box.addWidget(self.reset)
        bottom_h_box.addStretch()
        bottom_h_box.addWidget(QLabel('Speed '))
        bottom_h_box.addWidget(self.slider)
        bottom_h_box.addStretch()

        bottom_h_box.addWidget(self.prevStep)
        bottom_h_box.addWidget(self.nextStep)

        v_box = QVBoxLayout()
        v_box.addLayout(top_h_box)
        v_box.addWidget(self.viewer)
        v_box.addLayout(bottom_h_box)

        self.setLayout(v_box)

        self.play_pause_button.clicked.connect(self.play_pause_clicked)
        self.reset.clicked.connect(self.reset_clicked)
        self.slider.valueChanged.connect(self.slider_changed)

        self.setMinimumSize(800, 600)
        self.viewer.updateView()
        self.show()

    def play_pause_clicked(self):
        """Slot for the play/pause button click event. It starts or pauses the loop"""
        self.loop.play_pause()
        self.viewer.updateView()

    def stopSimulation(self):
        self.loop.play_pause()
        self.play_pause_button.changeText()

    def next_clicked(self):
        self.model.next()
        self.viewer.updateView()

    def prev_clicked(self):
        view = self.model.prev()
        self.viewer.updateView(view)

    def generate_clicked(self):
        self.model.sandGenerator()
        self.viewer.updateView()

    def reset_clicked(self):
        """Slot for the reset button click event. Resets the model, pauses the loop and updates the view"""
        if self.loop.is_going():
            self.loop.play_pause()
            self.play_pause_button.changeText()
        self.model.resetButtonAction()
        self.viewer.updateView()

    def slider_changed(self):
        """Slot for the speed slider value changed signal. Changes the loop timeout time based on the speed"""
        speed = 1010 - self.slider.value()
        self.loop.set_speed(speed)

    def resizeEvent(self, ev):
        """Slot for window resize event (Override)"""
        # self.viewer.updateView()
        super().resizeEvent(ev)

    def change_sand_generator(self, text):
        if self.loop.is_going():
            self.loop.play_pause()
            self.play_pause_button.changeText()
        if text == 'Top Edge':
            self.model.topEdgeGenerator()
            pass
        if text == 'Central top two cells':
            self.model.centralEdgeGenerator()
            pass

    def change_pattern(self, text):
        """Slot for the ComboBox changed state signal. Loads the selected known pattern"""
        if self.loop.is_going():
            self.loop.play_pause()
            self.play_pause_button.changeText()

        is_loaded_correctly = self.model.read_from_file(text)
        if is_loaded_correctly is False:
            QMessageBox.about(self, "File Error", "File selected is not valid")
        #self.model.sandGenerator()
        self.viewer.updateView()
