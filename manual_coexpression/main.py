import napari
from manual_coexpression.widget import Widget


def main():
    print("Opening napari viewer")
    with napari.gui_qt():
        viewer = napari.Viewer(title="Manual segmentation")
        widget = Widget(viewer)
        viewer.window.add_dock_widget(widget, name="General", area="right")


if __name__ == "__main__":
    main()
