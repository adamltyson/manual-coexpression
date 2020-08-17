from qtpy import QtCore

from pathlib import Path
from glob import glob

# from brainrender.scene import Scene
# from neuro.structures.IO import load_structures_as_df
# from imlib.source.source_files import get_structures_path
#
# from neuro.segmentation.paths import Paths
# from neuro.generic_neuro_tools import transform_image_to_standard_space
#
# from neuro.visualise.napari_tools.layers import (
#     display_channel,
#     prepare_load_nii,
# )
# from neuro.visualise.napari_tools.callbacks import (
#     display_brain_region_name,
#     region_analysis,
#     track_analysis,
#     save_all,
# )
#
# from neuro.segmentation.manual_segmentation.man_seg_tools import (
#     add_existing_region_segmentation,
#     add_existing_track_layers,
#     add_new_track_layer,
#     add_new_region_layer,
#     view_in_brainrender,
# )
# from neuro.gui.elements import (
#     add_button,
#     add_checkbox,
#     add_float_box,
#     add_int_box,
#     add_combobox,
# )
import numpy as np

from qtpy.QtWidgets import (
    QLabel,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QApplication,
    QWidget,
)


from qtpy.QtWidgets import (
    QDoubleSpinBox,
    QPushButton,
    QCheckBox,
    QLabel,
    QSpinBox,
    QComboBox,
)


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
        self.setup_layout()

    def setup_layout(self):
        self.instantiated = False
        layout = QGridLayout()

        self.load_button = add_button(
            "Load image", layout, self.load_image, 0, 0, minimum_width=200,
        )

        self.setLayout(layout)

    def load_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file, _ = QFileDialog.getOpenFileName(
            self, "Select the image you wish to load", "", options=options,
        )
        self.viewer._add_layers_with_plugins(file)
        shape = self.viewer.layers[0].shape
        labels = np.zeros((1, shape[1], shape[2]))
        label_layer = self.viewer.add_labels(
            labels, num_colors=2, name="Cells"
        )
        label_layer.selected_label = 1
        label_layer.brush_size = self.brush_size
        label_layer.mode = "PAINT"
