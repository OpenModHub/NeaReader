import sys
from PySide6.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem, QLabel, QVBoxLayout, QWidget, QProgressBar, QMessageBox
from PySide6.QtGui import QTransform, QFont
from PySide6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
import os
sys.path.append(os.getcwd())
import NeaImager as neaim
# from qt_material import apply_stylesheet

current_folder = os.getcwd()
ui_file = os.path.join(current_folder,'App\HyperImager.ui')

uiclass, baseclass = pg.Qt.loadUiType(ui_file)

class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        # Load UI
        self.setupUi(self)
        # Add other UI elements
        self.channelcombobox.addItems(['O0A raw', 'O0P raw', 'O1A raw', 'O1P raw', 'O2A raw', 'O2P raw', 'O3A raw', 'O3P raw',
                             'O4A raw', 'O4P raw', 'O5A raw', 'O5P raw', 'Z raw', 'Z C', 'M0A raw', 'M0P raw',
                             'M1A raw', 'M1P raw', ])
        self.channelcombobox.setCurrentIndex(4)
        self.measinfo_treeWidget.setColumnCount(2)
        self.measinfo_treeWidget.setHeaderLabels(["Property", "Value"])
        self.nextButton.setText("\U0001F87A")
        self.prevButton.setText("\U0001F878")
        self.linelevelComboBox.addItems(['Mean','Median','Median of differences'])
        # setup stylesheet
        # apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)

        # Additional arguments
        self.measurement = neaim.NeaImage()
        self.correctedMeasList = []
        self.current_file_name = None
        self.colorMapName = 'CET-D3'

        # Assign function to buttons
        self.openfile.clicked.connect(self.choose_file)
        self.loadchannel.clicked.connect(self.load_meas)
        self.load_info.clicked.connect(self.choose_info_file)
        self.nextButton.clicked.connect(self.nextCorrectionPage)
        self.prevButton.clicked.connect(self.prevCorrectionPage)
        self.applyLineLevel.clicked.connect(self.levelTheLines)
        self.applyBgFit.clicked.connect(self.fitTheBackground)

        # Create default plot
        testdata = np.fromfunction(lambda i, j: (1+0.3*np.sin(i)) * (i)**2 + (j)**2, (100, 100))
        testdata = testdata * (1 + 0.2 * np.random.random(testdata.shape) )
        testdata = testdata.transpose()

        # Create plot widget
        pg.setConfigOptions(imageAxisOrder='row-major')
        self.imItem = pg.ImageItem(image=testdata)                                                  # create an ImageItem
        self.plotContainer.addItem(self.imItem)                                                         # add it to the PlotWidget
        self.cbar = self.plotContainer.addColorBar(self.imItem,colorMap=self.colorMapName,rounding=0.01)        # Create a colorBarItem and add to the PlotWidget
        self.plotContainer.setBackground('w')
        axPen = pg.mkPen(color=(23, 54, 93), style=Qt.SolidLine, width = 1)
        axFont = QFont()
        axFont.setPointSize(12)
        axList = ['bottom','left','top','right']
        for ax in axList:
            self.plotContainer.getAxis(ax).setPen(axPen)
            self.plotContainer.getAxis(ax).setTextPen(axPen)
            self.plotContainer.getAxis(ax).label.setFont(axFont)
            if ax == 'top' or ax == 'right':
                 self.plotContainer.getAxis(ax).setStyle(tickFont=axFont, tickLength = 0)
            else:
                 self.plotContainer.getAxis(ax).setStyle(tickFont=axFont, tickLength = 5)

        self.plotContainer.getAxis('bottom').setLabel('X position / μm')
        self.plotContainer.getAxis('left').setLabel('Y position / μm')
        self.plotContainer.showAxes(True)
        self.plotContainer.setAspectLocked(True)

    def choose_file(self):
            fname = QFileDialog.getOpenFileName(self, "Choose GWY file","","Gwyddion files (*.gwy)")
            self.current_file_name = fname[0]
            self.measurement.filename = fname[0]

    def choose_info_file(self):
            if self.measurement is not None:
                fname = QFileDialog.getOpenFileName(self, "Choose NeaSpec info file","","Text files (*.txt)")
                self.measurement.parameters = self.measurement.read_info_file(fname[0])
                self.tree_from_dict(data=self.measurement.parameters,parent=self.measinfo_treeWidget)
            else:
                pass #TODO: Error pop-up window

    def load_meas(self):
            channelname = self.channelcombobox.currentText()
            self.measurement.read_from_gwyfile(self.current_file_name,channelname)
            self.correctedMeasList = [self.measurement]
            print(f'Amp: {self.measurement.isamp}, Phase: {self.measurement.isphase}, Topo: {self.measurement.istopo}')
            if self.measurement.istopo:
                 self.colorMapName = 'CET-L1'
            elif self.measurement.isphase:
                self.colorMapName = 'CET-D1A'
            elif self.measurement.isamp:
                 self.colorMapName = 'CET-L3'
            else:
                 self.colorMapName = 'CET-D3'

            self.update_image(self.measurement)
            print(np.shape(self.measurement.data),'datapoints were loaded')

    def update_image(self,m):
        self.imItem.setImage(image = m.data)
        self.cbar.setColorMap(pg.colormap.get(self.colorMapName))
        self.cbar.setLevels(values = (np.min(m.data),np.max(m.data)))

    def levelTheLines(self):
        choosen_type = self.linelevelComboBox.currentText()
        match choosen_type:
            case 'Median':
                  mtype = 'median'
            case 'Mean':
                  mtype = 'average'
            case 'Median of differences':
                  mtype = 'difference'
        m_levelled = neaim.LineLevel(inputobj = self.measurement, mtype = mtype)
        self.correctedMeasList.append(m_levelled)
        self.update_image(self.correctedMeasList[-1])

    def fitTheBackground(self):
        xdegree = self.bgDegreeXspinBox.value()
        ydegree = self.bgDegreeYspinBox.value()
        m_bg,f_bg = neaim.BackgroundPolyFit(inputobj = self.correctedMeasList[-1], xorder=xdegree, yorder=ydegree)
        self.correctedMeasList.append(m_bg)
        self.update_image(self.correctedMeasList[-1])

    # UI function staff
    def tree_from_dict(self, data=None, parent=None):
        for key, value in data.items():
            item = QTreeWidgetItem(parent)
            item.setText(0, key)
            item.setText(1, str(value))
    
    def nextCorrectionPage(self):
        self.CorrectionsQStack.setCurrentIndex(self.CorrectionsQStack.currentIndex() + 1)

    def prevCorrectionPage(self):
        self.CorrectionsQStack.setCurrentIndex(self.CorrectionsQStack.currentIndex() - 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())