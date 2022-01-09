import os
from settings import DISHES_DIR
import numpy as np
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
SAND = 100
EMPTY = 255
WALL = 0

class FallingSand(QWidget):
    rows: int
    cols: int
    map: np.ndarray
    states: list
    endOfSimulationSignal = pyqtSignal()

    def __init__(self, mode):
        super().__init__()
        self.sandGenerator = self.topEdgeGenerator
        self.init_states()
        self.initial_pattern = 'middleBow'
        self.read_from_file('middleBow')
        self.mode = mode
        self.current_state = 0
        self.was_change = True

    def setPlayPauseButton(self, button):
        self.play_pause = button

    def topEdgeGenerator(self):
        ten_percent = int(self.map.shape[0] / 10)
        rows = ten_percent if ten_percent > 0 else 1
        sands = np.full(self.map[:rows].shape, SAND)
        self.map[:rows] = sands
        self.sandGenerator = self.topEdgeGenerator
        self.sands = sands
        self.add_state(np.copy(self.map))

    def centralEdgeGenerator(self):
        ten_percent_rows = self.map.shape[0] // 10
        ten_percent_cols = self.map.shape[1] // 10
        sands = np.full(self.map[:ten_percent_rows, ten_percent_cols * 4: ten_percent_cols * 6].shape, SAND)
        self.map[:ten_percent_rows, ten_percent_cols * 4: ten_percent_cols * 6] = sands
        self.sandGenerator = self.centralEdgeGenerator
        self.sands = sands
        self.add_state(np.copy(self.map))

    def init_states(self):
        self.states = []
        self.current_state = 0

    def reset(self):
        self.read_from_file(self.initial_pattern)
        pass

    def resetButtonAction(self):
        self.read_from_file(self.initial_pattern)

    def getCellIfExist(self, row, col):
        if 0 <= row < self.map.shape[0] and 0 <= col < self.map.shape[1]:
            return self.map[row, col]
        return None

    def get_left_right_cells(self, row, col):
        return self.getCellIfExist(row, col - 1), self.getCellIfExist(row, col + 1)

    def get_diagonal_left_right_cells(self, row, col):
        return self.getCellIfExist(row + 1, col - 1), self.getCellIfExist(row + 1, col + 1)

    def is_cell(self, cell, cellType):
        if cell is not None and cell == cellType:
            return True
        return False

    def prev(self):
        if self.current_state > 0:
            self.current_state -= 1

    def next(self):
        if self.current_state + 1 >= len(self.states):
            self.calculate_next_state()
        else:
            self.current_state += 1

    def handleSandMoveFor(self, row, col, newMap):
        below_cell = self.getCellIfExist(row + 1, col)
        left_below_cell, right_below_cell = self.get_diagonal_left_right_cells(row, col)
        left_cell, right_cell = self.get_left_right_cells(row, col)
        if self.is_cell(below_cell, EMPTY):
            newMap[row, col] = EMPTY
            newMap[row + 1, col] = SAND
            self.was_change = True
        elif self.is_cell(below_cell, SAND):
            if self.is_cell(left_cell, EMPTY) and self.is_cell(left_below_cell, EMPTY):
                newMap[row, col] = EMPTY
                newMap[row + 1, col - 1] = SAND
                self.was_change = True
            elif self.is_cell(right_cell, EMPTY) and self.is_cell(right_below_cell, EMPTY):
                newMap[row, col] = EMPTY
                newMap[row + 1, col + 1] = SAND
                self.was_change = True
        return self.was_change, newMap

    def calculate_next_state(self):
        """
        This method is the engine of the simulation. Calculates and updates the next state of the simulation following the rules.
        if below cell is empty then move sand down.
        if below cell is wall and below left cell in empty then move sand left-down
        if below cell is wall and below right cell in empty then move sand right-down
        """
        rows, cols = self.map.shape
        newMap = np.copy(self.states[-1])
        # iterate from end.
        self.was_change = False
        for row in range(rows - 1, -1, -1):
            for col in range(cols - 1, -1, -1):
                cell = self.map[row, col]
                if cell == SAND:
                    self.was_change, newMap = self.handleSandMoveFor(row, col, newMap)
        if self.was_change:
            self.map = np.copy(newMap)
            self.add_state(np.copy(self.map))
        else:
            self.endOfSimulationSignal.emit()

    def read_from_file(self, filename):
        try:
            filepath = os.path.join(DISHES_DIR, filename)
            with open(filepath, 'r') as file:
                lines = file.readlines()
            if not lines:
                return
            for i, line in enumerate(lines):
                lines[i] = line.replace(' ', '').replace('\n', '')

            self.rows = len(lines)
            self.cols = len(lines[0])
            self.map = np.zeros((self.rows, self.cols), dtype=np.uint8)
            for row, line in enumerate(lines):
                for col, element in enumerate(line):
                    if element == "x":
                        self.map[row, col] = WALL
                    if element == ".":
                        self.map[row, col] = EMPTY
                    if element == "o":
                        self.map[row, col] = SAND
            self.init_states()
            self.states.append(np.copy(self.map))
            self.initial_state = np.copy(self.map)
            self.initial_pattern = filename
            return True
        except Exception:
            return False

    def get_state(self):
        return self.states[self.current_state]

    def add_state(self, state):
        self.states.append(state)
        self.current_state = len(self.states) - 1

    def set_cell(self, i, j, value):
        self.map[i, j] = value
        self.add_state(np.copy(self.map))
