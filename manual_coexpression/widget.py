import numpy as np

from qtpy.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QWidget,
)


from qtpy.QtWidgets import (
    QPushButton,
    QLabel,
    QComboBox,
)

from skimage.measure import label

import pandas as pd
from pathlib import Path


def add_combobox(layout, label, items, row, column=0):
    combobox = QComboBox()
    combobox.addItems(items)
    layout.addWidget(QLabel(label), row, column)
    layout.addWidget(combobox, row, column + 1)
    return combobox


def add_button(
    label,
    layout,
    connected_function,
    row,
    column,
    visibility=True,
    minimum_width=0,
):
    button = QPushButton(label)
    button.setVisible(visibility)
    button.setMinimumWidth(minimum_width)
    layout.addWidget(button, row, column)
    button.clicked.connect(connected_function)
    return button


def add_new_label_layer(
    viewer,
    base_image,
    name="region",
    selected_label=1,
    num_colors=10,
    brush_size=30,
):
    """
    Takes an existing napari viewer, and adds a blank label layer
    (same shape as base_image)
    :param viewer: Napari viewer instance
    :param np.array base_image: Underlying image (for the labels to be
    referencing)
    :param str name: Name of the new labels layer
    :param int selected_label: Label ID to be preselected
    :param int num_colors: How many colors (labels)
    :param int brush_size: Default size of the label brush
    :return label_layer: napari labels layer
    """
    labels = np.empty_like(base_image)
    label_layer = viewer.add_labels(labels, num_colors=num_colors, name=name)
    label_layer.selected_label = selected_label
    label_layer.brush_size = brush_size
    return label_layer


class Widget(QWidget):
    def __init__(
        self, viewer, brush_size=30,
    ):
        super(Widget, self).__init__()

        self.viewer = viewer
        self.brush_size = brush_size

        self.label_layer = []

        self.setup_layout()

    def setup_layout(self):
        self.instantiated = False
        layout = QGridLayout()

        self.load_button = add_button(
            "Load image", layout, self.load_image, 0, 0, minimum_width=200,
        )
        self.load_button = add_button(
            "Analyse", layout, self.analyse, 1, 0, minimum_width=200,
        )
        self.setLayout(layout)

    def load_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.file, _ = QFileDialog.getOpenFileName(
            self, "Select the image you wish to load", "", options=options,
        )
        print(f"Loading file: {self.file}")
        self.viewer._add_layers_with_plugins(self.file)
        shape = self.viewer.layers[0].shape
        labels = np.zeros((1, shape[1], shape[2]))
        self.label_layer = self.viewer.add_labels(
            labels, num_colors=2, name="Cells"
        )
        self.label_layer.selected_label = 1
        self.label_layer.brush_size = self.brush_size
        self.label_layer.mode = "PAINT"

    def analyse(self):
        print("Analysing")
        label_image = label(np.squeeze(self.label_layer.data))

        results = pd.DataFrame()
        for layer in self.viewer.layers:
            if layer._type_string == "image":
                projection = np.array(np.max(layer.data, axis=0))

                cells = []
                for cell_number in range(0, label_image.max()):
                    mean_intensity = np.mean(
                        projection[label_image == cell_number]
                    )
                    cells.append(mean_intensity)

                results[layer.name] = cells

        filename = Path(self.file).parent / (
            str(Path(self.file).stem) + "_quantification.csv"
        )
        print(f"Saving to: {filename}")
        results.to_csv(filename)
        print("Finished!")
