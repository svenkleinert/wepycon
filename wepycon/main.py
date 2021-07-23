import sys
from wepycon.gui.MainWidget import MainWidget
from wepycon.gui import QApplication

def main():
    app = QApplication( sys.argv )
    widget = MainWidget()

    widget.show()
    sys.exit(app.exec_())
    return 

if __name__ == "__main__":
   main()
