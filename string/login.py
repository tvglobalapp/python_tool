
from PyQt5 import uic, QtWidgets, QtGui
import sys
import jira.client
from jira.client import JIRA
from stringjira import MyWindowClass

dev_address = "http://hlm.lge.com/issue/"

class LoginClass(QtWidgets.QMainWindow, uic.loadUiType('D://login.ui')[0]):
    def __init__(self, parent=None):

        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle("String JIRA Creator")
        self.LoginButton.clicked.connect(self.Login)

    def Login(self):

        try:
            username = self.IdEdit.text()
            password = self.PasswordEdit.text()

            options = {'server':dev_address}
            myMain.account = JIRA(options, basic_auth=(username, password))

            Success()
            return ("Success")

        except:
            self.ResultLabel.show();
            return ("fail")


def Success():
    myLogin.close()
    myMain.show()

app = QtWidgets.QApplication(sys.argv)
myLogin = LoginClass(None)
myLogin.show()
myLogin.ResultLabel.hide()
myMain = MyWindowClass()
myMain.progressBar.hide()
myMain.hide()
sys.exit(app.exec_())
