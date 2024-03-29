import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QComboBox,
)
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QImage, QPixmap
from pathlib import Path

import matplotlib.pyplot as plt
import japanize_matplotlib
from analysis_methods.just_plot import just_plot
from analysis_methods.additive_method import additive_method
from analysis_methods.arima import arima
from analysis_methods.ETS_model import ETS_model
from analysis_methods.cluster import cluster
from analysis_methods.LLR import LLR
from analysis_methods.anomaly_detection import anomaly_detection


class DataAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Data Analyzer")
        self.showFullScreen()
        # Get the screen dimensions
        screen = app.primaryScreen()
        screen_width = screen.size().width()
        screen_height = screen.size().height()
        # Calculate sizes based on a 7:3 ratio
        total_width = screen_width
        total_height = screen_height
        graph_width = int(total_width * 0.7)  # 70% of the total width

        # Title label
        heading = QLabel("Data Analyzer", self)
        heading.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        heading.setObjectName("heading")

        # Uploading csv file
        self.data = None
        self.clustered_data = None
        self.selected_dataset = None
        self.file_label = QLabel("No file selected")
        self.import_button = QPushButton("Import File", self)
        self.import_button.clicked.connect(self.import_file)

        # Cluster or one plot selection using QComboBox
        self.mode_label = QLabel("Choose cluster or each column:")
        self.mode_combobox = QComboBox(self)
        self.mode_combobox.addItems(["", "Cluster", "Each column"])
        self.mode_combobox.currentIndexChanged.connect(self.populate_column_combobox)
        # Analysis method selection using QComboBox
        self.method_label = QLabel("Select Analysis Method:")
        self.method_combobox = QComboBox(self)
        # Column name selection using QComboBox
        self.column_label = QLabel("Select Column Name:")
        self.column_combobox = QComboBox(self)

        # Button to start analysis
        self.start_analysis_button = QPushButton("Start Analysis", self)
        self.start_analysis_button.clicked.connect(self.start_analysis)

        # QLabel to display the graph
        self.graph1_label = QLabel(self)
        self.graph1_label.setFixedSize(graph_width, total_height)

        # QLabel to display system messages
        self.error_msg_label = QLabel("System message:")
        self.error_msg = QLabel("No message")
        self.error_msg.setObjectName("error_msg")

        # Main layout setup
        main_layout = QVBoxLayout(self)

        # Top layout for heading
        top_layout = QVBoxLayout()
        top_layout.addWidget(heading)
        main_layout.addLayout(top_layout)

        # Bottom layout for file import, method selection, and analysis button
        bottom_layout = QHBoxLayout()
        # Left side layout for graphs
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.graph1_label)
        bottom_layout.addLayout(left_layout)
        # Right side layout for file import, method selection, and analysis button
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.file_label)
        right_layout.addWidget(self.import_button)
        right_layout.addStretch(1)
        right_layout.addWidget(self.mode_label)
        right_layout.addWidget(self.mode_combobox)
        right_layout.addStretch(1)
        right_layout.addWidget(self.column_label)
        right_layout.addWidget(self.column_combobox)
        right_layout.addStretch(1)
        right_layout.addWidget(self.method_label)
        right_layout.addWidget(self.method_combobox)
        right_layout.addStretch(1)
        right_layout.addWidget(self.start_analysis_button)
        right_layout.addStretch(1)
        right_layout.addWidget(self.error_msg_label)
        right_layout.addWidget(self.error_msg)
        right_layout.addStretch(1)
        bottom_layout.addLayout(right_layout)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def import_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open File", "", "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            file_name = Path(file_path).name
            self.file_label.setText(f"File Name: {file_name}")
            # Read CSV file using pandas
            try:
                # Store the data as an attribute
                self.data = pd.read_csv(file_path)

                # Show cluster plot
                self.clustered_data, plot = cluster(self.data)
                self.show_matplotlib_plot(plot)

                # Populate the column combobox
                self.populate_column_combobox(self.mode_combobox.currentIndex())

                self.method_combobox.clear()
                # Determine if the file meets the condition for selecting "Cluster" mode
                if self.data.columns[0] == "hour":
                    # Set mode_combobox to "Cluster"
                    self.mode_combobox.setCurrentIndex(1)
                    self.method_combobox.addItems(
                        [
                            "Just Plot",
                            "Additive method",
                            "Local Linear Regression",
                            "Anomaly Detection",
                        ]
                    )
                else:
                    self.method_combobox.addItems(
                        [
                            "Just Plot",
                            "Additive method",
                            "Arima method",
                            "ETS model",
                            "Local Linear Regression",
                            "Anomaly Detection",
                        ]
                    )

            except Exception as e:
                # Handle any potential errors during reading the CSV file
                print(f"Error reading CSV file: {e}")

    def populate_column_combobox(self, index):
        if index == 2:
            self.column_combobox.clear()
            if self.data is not None:
                self.selected_dataset = self.data
                if self.data.columns[0] != "hour":
                    self.column_combobox.addItems(self.data.columns[1:])
        elif index == 1:
            self.column_combobox.clear()
            if self.clustered_data is not None:
                self.selected_dataset = self.clustered_data
                self.column_combobox.addItems(self.clustered_data.columns[1:])
        else:
            self.column_combobox.clear()
        # column_combobox.clear()
        # column_combobox.addItems(data.columns[1:])

    def start_analysis(self):
        # Get the selected analysis method and column name from the combobox
        selected_method = self.method_combobox.currentText()
        selected_column = self.column_combobox.currentText()

        # Reset index
        self.data.reset_index(drop=True, inplace=True)

        # Map the selected method to the corresponding function
        method_mapping = {
            "Just Plot": just_plot,
            "Additive method": additive_method,
            "Arima method": arima,
            "ETS model": ETS_model,
            "Local Linear Regression": LLR,
            "Anomaly Detection": anomaly_detection,
        }

        analysis_method = method_mapping.get(selected_method)

        if analysis_method:
            # Perform analysis directly in the main thread
            plot, msg = analysis_method(self.selected_dataset, selected_column)
            self.error_msg.setText(msg)
            self.analysis_complete(plot)

    def analysis_complete(self, plot):
        if plot:
            if isinstance(plot, plt.Figure):
                self.show_matplotlib_plot(plot)
            else:
                print("Invalid plot type")

    def show_matplotlib_plot(self, plot):
        # Clear existing plots
        self.graph1_label.clear()

        # Display the plots in the QLabel widgets
        self.graph1_label.setPixmap(self.plot_to_pixmap(plot))

    def plot_to_pixmap(self, plot):
        # Create a figure and render it to a pixmap
        figure = plot.figure
        canvas = figure.canvas
        canvas.draw()  # Ensure the figure is drawn

        # Convert the rendered figure to a NumPy array
        width, height = figure.get_size_inches() * figure.get_dpi()
        buf = canvas.buffer_rgba()
        img = np.frombuffer(buf, dtype=np.uint8).reshape(int(height), int(width), 4)

        # Create a QImage from the NumPy array
        qimage = QImage(img.data, int(width), int(height), QImage.Format_RGBA8888)

        # Create a QPixmap from the QImage
        pixmap = QPixmap.fromImage(qimage)

        return pixmap

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(Path("styles.qss").read_text())

    window = DataAnalyzerApp()
    window.show()
    sys.exit(app.exec_())
