from PySide2.QtGui import QColor
import maya.cmds as mc
import maya.mel as mel

from PySide2.QtWidgets import (QListWidget,
                               QVBoxLayout,
                               QHBoxLayout,
                               QPushButton,
                               QMessageBox,
                               QSlider,
                               QLabel)

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
        self.controllerSize = 1
    
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
        self.eyeGrp = mc.group(self.leftEye, self.rightEye, name="Eye_Grp")

        for eye in [self.leftEye, self.rightEye]:
            ctrl =  mc.circle(name=eye + "_Ctrl", radius=0.3 * self.controllerSize)[0]
            grp = mc.group(ctrl, name=eye + "_Ctrl_Grp")
            mc.matchTransform(grp, eye)
            mc.aimConstraint(ctrl, eye, aimVector = (0,0,1), upVector=(0,1,0), worldUpType = "scene")
        
        leftEyeLoc = mc.xform(self.leftEye, query=True, translation=True, worldSpace=False)
        rightEyeLoc = mc.xform(self.rightEye, query=True, translation=True, worldSpace=False)
        eyeGrpRot = mc.xform(self.eyeGrp, query=True, rotation=True, worldSpace=False)
        cX = (leftEyeLoc[0] + rightEyeLoc[0]) / 2
        cY = (leftEyeLoc[1] + rightEyeLoc[1]) / 2
        cZ = (leftEyeLoc[2] + rightEyeLoc[2]) / 2

        mainCtrl = mc.circle(name = "Main_EyeCtrl", radius=1 * self.controllerSize)[0]
        mainGrp = mc.group(mainCtrl, name="Main_Ctrl_Grp")

        mc.xform(mainGrp, translation = (cX,cY,cZ), rotation=(eyeGrpRot[0], eyeGrpRot[1], eyeGrpRot[2]))
        mc.parent(self.leftEye + "_Ctrl_Grp", self.rightEye + "_Ctrl_Grp", mainCtrl)
        mc.xform(mainGrp, translation = (cX,cY,cZ + 5))

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
        
        clearMeshBtn = QPushButton("Clear Meshes")
        clearMeshBtn.clicked.connect(self.ClearMeshesBtnClicked)
        self.masterLayout.addWidget(clearMeshBtn)

        ctrlSizeSliderLayout = QHBoxLayout()
        ctrlSizeSlider = QSlider()
        ctrlSizeSlider.setValue(self.rigger.controllerSize)
        ctrlSizeSlider.valueChanged.connect(self.CtrlSizeValueChanged)
        ctrlSizeSlider.setRange(0.01, 10)
        ctrlSizeSlider.setOrientation(Qt.Horizontal)
        ctrlSizeSliderLayout.addWidget(ctrlSizeSlider)
        self.ctrlSizeLabel = QLabel(f"{self.rigger.controllerSize}")
        self.masterLayout.addWidget(self.ctrlSizeLabel)
        self.masterLayout.addLayout(ctrlSizeSliderLayout)

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

    @TryAction
    def ClearMeshesBtnClicked(self):
        self.meshList.clear()

    def CtrlSizeValueChanged(self, newValue):
        self.rigger.controllerSize = newValue
        self.ctrlSizeLabel.setText(f"{self.rigger.controllerSize}")

def Run():
    eyeRiggerToolWidget = EyeRiggerToolWidget()
    eyeRiggerToolWidget.show()

Run()