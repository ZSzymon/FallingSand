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
from timeit import default_timer as timer
from PyQt5.QtCore import (Qt)
from PyQt5.QtGui import QImage, qRgb, QPixmap
from PyQt5.QtWidgets import (QLabel, QSizePolicy)


class MapViewer(QLabel):
    """
    Custom Widget to show and edit (with mouse events) the state of GoL.

    Attributes:
        model         reference to an object of class GameOfLife (the model)
        drawing     bool value to keep track of mouse button long press and movement
        V_margin    dimension of right and left margin in window (widget) coordinates for the image
        H_margin    dimension of top and bottom margin in window (widget) coordinates for the image
        h           board (model state) height
        w           board (model state) height
        lastUpdate  time of the last view update
        pixmap      image representing the state of the game (QPixmap object) (self.pixmap())
    """

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.drawing = False
        self.V_margin = 0
        self.H_margin = 0
        self.h = 0
        self.w = 0
        self.lastUpdate = timer()

    def set_model(self, model):
        """
        Set the reference to the model model.

        Args:uniform_filter
            model     object of class GameOfLife
        """
        self.model = model
        self.updateView()  # update the view to show the first frame

    def updateView(self, view=None):
        """Update the view converting the current state (np.ndarray) to an image (QPixmap) and showing it on screen"""
        map = self.model.get_state() if not view else view
        self.h = map.shape[0]
        self.w = map.shape[1]
        qim = self.toQImage(map)  # first convert to QImage
        qpix = QPixmap.fromImage(qim)  # then convert to QPixmap
        # set the pixmap and resize to fit the widget dimension
        self.setPixmap(qpix.scaled(self.size(), Qt.KeepAspectRatio, Qt.FastTransformation))
        self.lastUpdate = timer()  # update the lastUpdate time
        try:
            self.V_margin = (self.size().width() - self.pixmap().size().width()) / 2
            self.H_margin = (self.size().height() - self.pixmap().size().height()) / 2
        except AttributeError:
            self.V_margin = 0
            self.H_margin = 0

    def toQImage(self, im):
        """
        Utility method to convert a numpy array to a QImage object.

        Args:
            im          numpy array to be converted. It can be a 2D (BW) image or a color image (3 channels + alpha)

        Returns:
            QImage      The image created converting the numpy array
        """
        gray_color_table = [qRgb(i, i, i) for i in range(256)]
        if im is None:
            return QImage()
        if len(im.shape) == 2:  # 1 channel image
            qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
            qim.setColorTable(gray_color_table)
            return qim

    def mousePressEvent(self, event):
        """Slot for mouse press event (Override)"""
        self.handleMouseClickEvent(event, mouseButton=Qt.RightButton, color=0)
        self.handleMouseClickEvent(event, mouseButton=Qt.LeftButton, color=255)

    def getXYPosition(self, event, marginCorrection=True):
        """Utility method to get x, y position from event..

        :param event:
        :param marginCorrection: bool to indicate if marginCorrection is considered.
        :return:  x, y position from event.
        """

        if marginCorrection:
            x = event.pos().x() - self.V_margin
            y = event.pos().y() - self.H_margin
        else:
            x = event.pos().x()
            y = event.pos().y()
        return x, y

    def mouseMoveEvent(self, event):
        """Slot for mouse move event (Override)"""
        self.handleMouseMoveEvent(event, mouseButton=Qt.LeftButton, color=255)
        self.handleMouseMoveEvent(event, mouseButton=Qt.RightButton, color=0)

    def mouseReleaseEvent(self, event):
        """Slot for mouse release event (Override)"""
        # release the self.drawing mode
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
        if event.button() == Qt.RightButton and self.drawing:
            self.drawing = False

    def handleMouseClickEvent(self, event, mouseButton, color):
        """Utility method to handle mouse click event on mapViewer object..

        :param event: event to handle.
        :param mouseButton: Qt mouseButton.
        :param color: The color pixel will be painted.

        """
        if event.button() == mouseButton:
            self.drawing = True
            x, y = self.getXYPosition(event, marginCorrection=True)
            # check if mouse is inside the bounds of the board
            if self.isInBoardBounds(x, y):
                # convert widget coordinate to state indexes
                row, col = self.getRowCol(x, y)
                self.model.set_cell(row, col, color)
                self.updateView()

    def handleMouseMoveEvent(self, event, mouseButton, color):
        """Utility method to handle mouse move event on mapViewer object.

        :param event: event to handle.
        :param mouseButton: Qt mouseButton.
        :param color: The color pixel will be painted.

        """
        if event.buttons() == mouseButton and self.drawing:  # if left click and self.drawing, draw living cells
            x, y = self.getXYPosition(event, marginCorrection=True)
            if self.isInBoardBounds(x, y):
                # convert widget coordinate to state indexes
                row, col = self.getRowCol(x, y)
                self.model.set_cell(row, col, color)
                if (timer() - self.lastUpdate) > 0.04:
                    self.updateView()

    def getRowCol(self, x, y):
        """Utility to get row and column from of pixel based on x, y position

        :param x:
        :param y:
        :return:
        """
        row = int(y * self.h / self.pixmap().height())
        col = int(x * self.w / self.pixmap().width())
        return row, col

    def isInBoardBounds(self, x, y):
        """Utility to indicate if click was inside of pixmap.

        :param x: x position with margin correction
        :param y: y position with margin correction
        :return: bool indicating is this click inside of pixmap.
        """
        return 0 < y < self.pixmap().height() and 0 < x < self.pixmap().width()
