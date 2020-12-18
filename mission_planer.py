import sys
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget)
from traj import *


class Terrain(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Terrain")
        self.resize(500, 500)
        self.setStyleSheet("background-color: black;") 

        self.l = 40
        self.pen1 = QtGui.QPen(QtGui.QColor(255,255,255))                # set lineColor
        self.pen1.setWidth(2)
        self.penV = QtGui.QPen(QtGui.QColor(139, 58, 119))                # set lineColor
        self.penV.setWidth(2)                                            # set lineWidth
        self.brush = QtGui.QBrush(QtGui.QColor(255,255,255,255))        # set fillColor  
        self.wps = []
        self.np_wps = np.empty((1, 2))
        #self.polygon = QtGui.QPolygonF() 
        
    def mouseReleaseEvent(self, e):
        self.wps.append(QtCore.QPoint(e.x(), e.y()))
        if self.np_wps.shape[0] == 1:
            self.np_wps = np.array((e.x(), e.y()))
        else:
            self.np_wps = np.vstack((self.np_wps, np.array((e.x(), e.y()))))
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        
        # affichage traj rob
        painter.setPen(self.penV)
        if self.np_wps.shape[0] >= 3: # on ne peut calculer que si il ya plus de 3 wps
            wps_traj, traj_def = triTraj(self.np_wps, self.l)
            for i in range(len(traj_def)):
                if traj_def[i][0] == 'line':
                    p1 = QtCore.QPoint(wps_traj[i, 0], wps_traj[i, 1])
                    p2 = QtCore.QPoint(wps_traj[i+1, 0], wps_traj[i+1, 1])
                    painter.drawLine(p1, p2)
                else:
                    _, x, y, a1, a2 = traj_def[i]
                    r = QtCore.QRect(x - self.l, y - self.l, 2*self.l, 2*self.l)
                    print(a1, a2)
                    if a1 > a2:
                        a2 = a2 - np.sign(a2)*360
                        print('--> ', a1, a2)
                    painter.drawArc(r, a1*16, a2*16)



        # affichage wps luge
        painter.setPen(self.pen1)
        for wp in self.wps:
            painter.drawEllipse(wp, 5, 5)
        for i in range(len(self.wps)-1):
            painter.drawLine(self.wps[i], self.wps[i+1])

        
            


        
        
class Param(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Paramètre")


        # activation du suivi du mouvement de la souris
        self.setMouseTracking(True)
        
    def mouseMoveEvent(self,event):
        print("position = " + str(event.x()) + " " + str(event.y()))
            
app = QApplication.instance() 
if not app:
    app = QApplication(sys.argv)
    
ter = Terrain()
ter.show()

app.exec_()
