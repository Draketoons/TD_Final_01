from PySide2.QtGui import QColor
import maya.cmds as mc
import maya.mel as mel

from PySide2.QtWidgets import (QWidget,
                               QListWidget,
                               QVBoxLayout,
                               QHBoxLayout,
                               QLabel,
                               QPushButton,
                               QLineEdit,
                               QMessageBox)

from PySide2.QtCore import Qt
from MayaUtils import QMayaWindow
from MayaUtils import *

def TryAction(action):
    def wrapper(*args, **kwargs):
        try: 
            action(*args, **kwargs)
        except Exception as e:
            QMessageBox().critical(None, "Error", f"{e}")
    return wrapper

class EyeRigger:
    def __init__(self):
        self.controllerSize = 5
    
    def AddMeshes(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("No meshes selected! please select two meshes")
        
        meshes = set()

        for sel in selection:
            if IsMesh(sel):
                meshes.add(sel)
        
        if len(meshes) < 2:
            raise Exception("Less than two meshes selected! please select only 2 meshes")
        
        if len(meshes) > 2:
            raise Exception("More than two meshes selected! please select only 2 meshes")
        
        self.meshes = list(meshes)

    def RigEyes(self):
        if len(self.meshes) < 2 | len(self.meshes) > 2:
            raise Exception("Mesh list is less then or more than 2 meshes")
        
        self.leftEye = self.meshes[0]
        self.rightEye = self.meshes[1]

        for eye in [self.leftEye, self.rightEye]:
            ctrl =  mc.circle(name=eye + "_Ctrl", radius=0.3)[0]
            grp = mc.group(ctrl, name=eye + "_Ctrl_Grp")
            mc.matchTransform(grp, eye)
            mc.aimConstraint(ctrl, eye, aimVector = (0,0,1), upVector=(0,1,0), worldUpType = "scene")

        mainCtrl = mc.circle(name = "Main_EyeCtrl", radius=0.5)[0]
        mainGrp = mc.group(ctrl, name="Main_Ctrl_Grp")
        mc.matchTransform(mainGrp, self.leftEye)

        mc.parent(self.leftEye + "_CTRL_GRP", self.rightEye + "_CTRL_GRP", mainCtrl)
        print("Rig Set!")


class EyeRiggerToolWidget(QMayaWindow):
    def __init__(self):
        super().__init__()
        self.rigger = EyeRigger()
        self.setWindowTitle("Basic Eye Rigger")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.meshList = QListWidget()
        self.masterLayout.addWidget(self.meshList)
        addMeshBtn = QPushButton("Add Meshses")
        addMeshBtn.clicked.connect(self.AddMeshBtnClicked)
        self.masterLayout.addWidget(addMeshBtn)

        rigEyesBtn = QPushButton("Rig Eyes")
        rigEyesBtn.clicked.connect(self.RiggEyesBtnClicked)
        self.masterLayout.addWidget(rigEyesBtn)

        print("EyeRigger: Initializing...")
    
    @TryAction
    def AddMeshBtnClicked(self):
        self.rigger.AddMeshes()
        self.meshList.clear()
        self.meshList.addItems(self.rigger.meshes)

    @TryAction
    def RiggEyesBtnClicked(self):
        self.rigger.RigEyes()

def Run():
    eyeRiggerToolWidget = EyeRiggerToolWidget()
    eyeRiggerToolWidget.show()

Run()