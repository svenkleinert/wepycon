import os
import matplotlib as mpl
mpl.use('Qt5Agg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np


class MatplotlibWidget(FigureCanvas):
    def __init__( self, figsize=None, horizontal=True ):
        self.figure = Figure( figsize=figsize )
        super(MatplotlibWidget, self).__init__(self.figure)

        self.ax = self.figure.subplots()

        self.orientation = "h" if horizontal else "v"

        if self.orientation == "h":
            self.ax.set_yticks([])
        else:
            self.ax.set_xticks([])
            self.ax.get_yaxis().set_label_position("right")
            self.ax.get_yaxis().set_ticks_position("right")

        self.figure.tight_layout( pad=0 )


    def plot( self, x, y ):
        if self.orientation == "h":
            self.line,  = self.ax.plot( x, y )
        else:
            self.line,  = self.ax.plot( y, x )
        self.draw()

    def refresh_data( self, y ):
        if self.orientation == "h":
            self.line.set_ydata( y )
        else:
            self.line.set_xdata( y )
        self.draw()
        self.flush_events()

    def set_xlabel( self, label ):
        self.ax.set_xlabel( label )

    def set_ylabel( self, label ):
        self.ax.set_ylabel( label )

    def set_xlim( self, lims ):
        self.ax.set_xlim( lims )

    def set_ylim( self, lims ):
        self.ax.set_ylim( lims )
