from PySide2 import QtWidgets
from fcfun import fc_isperp

def set_place(self,x,y,z):
    self.pos_x.setValue(x)
    self.pos_y.setValue(y)
    self.pos_z.setValue(z)

#  _________________________________________________________________
# |                                                                 |
# |                         Ortonormal Axis                         |
# |_________________________________________________________________|
def ortonormal_axis(axis_1, axis_2, axis_3):
    if ((fc_isperp(axis_1,axis_2)==0) or (fc_isperp(axis_2,axis_3)==0) or (fc_isperp(axis_1,axis_3)==0)):
        axis_message()
        return False
    else:
        return True
    
def axis_message():
    axis_message = QtWidgets.QMessageBox()
    axis_message.setText("Please, check the input axes")
    axis_message.setInformativeText("The axes must be perpendicular to each other")
    axis_message.setStandardButtons(QtWidgets.QMessageBox.Ok)
    axis_message.setDefaultButton(QtWidgets.QMessageBox.Ok)
    axis_message.exec_()
