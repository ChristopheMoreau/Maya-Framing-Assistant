# -*- coding: utf-8 -*-
# mayaFramingHelper.py
# script by CHRISTOPHE MOREAU moreau.vfx@gmail.com
# 03/2022

from PySide2 import QtWidgets
from PySide2.QtUiTools import QUiLoader
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
import maya.cmds as cmds
import maya.mel as mel
from os import listdir
import os
import sys


# listing *.png from picture's folder
def getListPic():
    pathImage = str(sys.path[0]) + r"/pictures"
    lst = listdir(pathImage)
    listPic = []
    for x in lst:
        if x.endswith(".png"):
            listPic.append(os.path.splitext(x)[0])
    return listPic


# listing user cameras from scene
def getListCamera():
    listCamera = [c for c in cmds.ls(type='camera') if not cmds.camera(c, q=True, sc=True)]
    listCamera = cmds.listRelatives(listCamera, parent=True, fullPath=0)

    if listCamera:
        pass
    else:
        listCamera = 'noCamera'
    return listCamera


# get the actual camera viewport
def viewerToUse():
    currentViewPort = ''
    currentCamera = ''
    for viewPort in cmds.getPanel(type="modelPanel"):
        curCamera = cmds.modelEditor(viewPort, q=1, av=1, cam=1)
        nomCam = list(curCamera.split('|'))
        camera = nomCam[len(nomCam) - 2]
        if camera in getListCamera():
            currentViewPort = viewPort
            currentCamera = camera

    return currentViewPort, currentCamera


# get connected image plane to the given camera
def updateImagePlaneList(camName):
    imagePlane = ''
    if cmds.listRelatives(camName, type='imagePlane', ad=True, c=True):
        imagePlaneShape = cmds.listRelatives(camName, type='imagePlane', ad=True, c=True)
        imagePlane = cmds.listRelatives(imagePlaneShape, parent=True)
    else:
        pass
    return imagePlane


def getCameraFromViewport(viewport):
    curCamera = cmds.modelEditor(viewport, q=1, av=1, cam=1)
    return curCamera


class MainWindow(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # using the UIFILEPATH
        UIFILEPATH = str(sys.path[0]) + str(r'/gui/mainWindow.ui')
        # print(UIFILEPATH)
        self.UI = QUiLoader().load(UIFILEPATH)
        # Get the window title from the ui file
        self.setWindowTitle('Framing Helper')
        # Main widget
        self.setCentralWidget(self.UI)

        # setting the fixed size of window
        # self.setFixedSize(285, 460)

        # Path to png picture
        self.pathImage = str(sys.path[0]) + r"/pictures"

        # Update Camera at launch
        self.activateOptions(2)
        # Connection to actions
        self.UI.refreshButton.clicked.connect(self.updateCameraList)
        self.UI.listCam.activated.connect(self.changeCamera)
        self.UI.pb_create.clicked.connect(self.createPushButton)
        self.UI.showManip.clicked.connect(self.showManip)
        self.UI.dollyZoomCheckBox.clicked.connect(self.dollyZoomCheck)
        self.UI.listPic.setCurrentRow(0)
        self.UI.listPic.itemClicked.connect(self.userChangePic)
        self.UI.listPic.addItems(getListPic())
        self.UI.preview.setPixmap(self.pathImage + '//' + self.UI.listPic.item(0).text() + '.png')
        self.UI.colorGain.valueChanged.connect(self.colorGainValue)
        self.UI.overScan.sliderMoved.connect(self.overScanValue)
        self.UI.overScan.valueChanged.connect(self.overScanValue)
        self.UI.rotateButton.clicked.connect(self.rotateImagePlane)
        self.UI.gate.clicked.connect(self.resolutionGate)
        self.UI.fit.clicked.connect(self.fitSettings)
        self.UI.aspectRatio.clicked.connect(self.aspectRatio)
        self.UI.hdFormat.stateChanged.connect(self.renderSettings)
        self.UI.scopeFormat.stateChanged.connect(self.renderSettings)
        self.UI.flatFormat.stateChanged.connect(self.renderSettings)

        self.UI.focalLength.sliderMoved.connect(self.focalLength)
        self.UI.focalLength.valueChanged.connect(self.focalLength)
        self.UI.focalLength.sliderPressed.connect(self.initFocusDistance)
        self.UI.focalLengthValue.returnPressed.connect(self.focalLengthSet)

        # Focal Length Preset
        self.UI.pushButton12.clicked.connect(self.focalPreset)
        self.UI.pushButton24.clicked.connect(self.focalPreset)
        self.UI.pushButton35.clicked.connect(self.focalPreset)
        self.UI.pushButton50.clicked.connect(self.focalPreset)
        self.UI.pushButton85.clicked.connect(self.focalPreset)
        self.UI.pushButton100.clicked.connect(self.focalPreset)
        self.UI.pushButton135.clicked.connect(self.focalPreset)
        self.UI.pushButton150.clicked.connect(self.focalPreset)
        self.UI.pushButton175.clicked.connect(self.focalPreset)
        self.UI.pushButton200.clicked.connect(self.focalPreset)

        # Global Variables
        self.imagePlane = ''
        self.selectedPic = str(self.UI.listPic.item(0).text())
        self.camAppertureY = 0.0
        self.Distance = 0.0
        self.Focal = 0.0
        self.currentCameraShape = ''
        self.imagePlaneShape = ''
        self.mainCameraViewer = ''
        self.viewerToUse = viewerToUse()[0]
        self.cameraToUse = viewerToUse()[1]

        if self.UI.imagePlane.text():
            self.imagePlaneShape = str(cmds.listRelatives(self.UI.imagePlane.text(), ad=0, s=1)[0])
        self.initCameraCenterOfInterest = 0
        self.initCameraFieldOfView = 0
        # Get render settings format
        self.getWidth = cmds.getAttr("defaultResolution.width")
        self.getHeight = cmds.getAttr("defaultResolution.height")
        if self.getHeight == 1080 and self.getWidth == 1920:
            # HD
            self.UI.hdFormat.setChecked(True)
        if self.getHeight == 1080 and self.getWidth == 1998:
            # FLAT
            self.UI.flatFormat.setChecked(True)
        if self.getHeight == 858 and self.getWidth == 2048:
            # SCOPE
            self.UI.scopeFormat.setChecked(True)

    def focalLengthGet(self):
        getFocal = cmds.getAttr(self.UI.listCam.currentText() + '.focalLength')
        self.UI.focalLength.setValue(getFocal)
        self.UI.focalLengthValue.setText(str(int(getFocal)))
        return getFocal

    def focalLengthSet(self):
        if self.UI.focalLengthValue.text():
            Value = self.UI.focalLengthValue.text()
        else:
            Value = self.focalLengthGet()

        self.UI.focalLength.setValue(float(Value))

    def focalLength(self, Value):
        cmds.setAttr(self.UI.listCam.currentText() + '.focalLength', Value)
        camera = self.UI.listCam.currentText()
        self.UI.focalLengthValue.setText(str(Value))

        if self.UI.dollyZoomCheckBox.isChecked():
            distance = (self.initCameraCenterOfInterest * Value) / self.Focal
            cmds.dolly(camera, abs=1, d=distance)
        else:
            self.UI.focalLengthValue.setText(str(Value))

    def initFocusDistance(self):
        self.initCameraCenterOfInterest = cmds.getAttr(self.UI.listCam.currentText() + '.centerOfInterest')
        self.Focal = self.UI.focalLength.value()

    def focalPreset(self):
        value = self.sender()
        self.UI.focalLength.setValue(float(value.text()))
        self.UI.focalLengthValue.setText(str(value.text()))
        cmds.setAttr(self.UI.listCam.currentText() + '.focalLength', float(value.text()))

    def dollyZoomCheck(self, status):
        if status:
            self.UI.showManip.setEnabled(status)
            self.initFocusDistance()
        else:
            self.UI.showManip.setEnabled(status)

    def disableCreateButton(self):
        self.activateOptions(0)

    def showManip(self):
        cmds.select(clear=True)
        cmds.select(self.currentCameraShape)
        if cmds.currentCtx() == 'moveSuperContext':
            mel.eval('ShowManipulatorTool')
        else:
            mel.eval('MoveTool')

    # Update the the camera list in the dropDown menu
    def updateCameraList(self):
        testCam = ''
        idx = 0
        if self.UI.listCam.currentText():
            idx = self.UI.listCam.currentIndex()
            testCam = self.UI.listCam.currentText()
        else:
            testCam = self.cameraToUse

        self.UI.listCam.clear()
        self.UI.listCam.addItems(getListCamera())
        self.UI.refreshButton.setText('> UPDATE <')
        self.activateOptions(1)
        listOfCam = getListCamera()
        if testCam in listOfCam:
            idx = listOfCam.index(testCam)

        self.activateOptions(1)
        currentCamIdx = idx
        self.changeCamera(currentCamIdx)

    # What to do when user change the Camera
    def changeCamera(self, Index):
        # get current camera
        self.UI.imagePlane.setText('')
        self.UI.listCam.setCurrentIndex(Index)

        if self.UI.listCam.currentText():
            # Setting Global Variable of the current camera from UI
            self.currentCameraShape = cmds.listRelatives(self.UI.listCam.currentText())
            getImagePlane = updateImagePlaneList(self.currentCameraShape)
            if getImagePlane != '':
                self.UI.imagePlane.setText(str(updateImagePlaneList(self.currentCameraShape)[0]))
                self.updateImagePreview()
                self.UI.imagePlaneFrame.setEnabled(1)
                self.UI.pb_create.setText('Delete')
            else:
                self.UI.listPic.setCurrentRow(0)
                self.UI.imagePlaneFrame.setEnabled(0)
                self.UI.pb_create.setText('Create Image Plane')

            self.focalLengthGet()
            self.focalLengthSet()
            getOverScan = cmds.getAttr(self.UI.listCam.currentText() + '.overscan')
            self.UI.overScan.setValue((getOverScan - 1) * 100)

        if Index != -1:
            cmds.lookThru(self.viewerToUse, self.UI.listCam.currentText())

        self.selectedPic = str(self.UI.listPic.currentItem().text())
        self.UI.preview.setPixmap(self.pathImage + '//' + str(self.UI.listPic.currentItem().text()) + '.png')

    def updateImagePreview(self):
        self.imagePlaneShape = str(cmds.listRelatives(self.UI.imagePlane.text(), ad=0, s=1)[0])
        imagePlaneShape = str(cmds.listRelatives(self.UI.imagePlane.text(), ad=0, s=1)[0])
        getActualIP = int(cmds.getAttr(imagePlaneShape + ".imagePlaneName"))
        self.UI.listPic.setCurrentRow(getActualIP)
        selectedPic = str(self.UI.listPic.currentItem().text())
        self.UI.preview.setPixmap(self.pathImage + '//' + selectedPic + '.png')
        getcolorGain = float('%.3f' % cmds.getAttr(str(imagePlaneShape) + '.colorGainR'))
        self.UI.colorGain.setValue(getcolorGain * 100)

    def imagePlaneChange(self):
        # self.changeCamera()
        self.imagePlaneShape = str(cmds.listRelatives(self.UI.imagePlane.text(), ad=0, s=1)[0])
        if self.UI.imagePlane.text() and self.UI.listPic.currentItem():
            imagePlaneShape = str(cmds.listRelatives(self.UI.imagePlane.text(), ad=0, s=1)[0])
            getActualIP = int(cmds.getAttr(imagePlaneShape + ".imagePlaneName"))
            self.UI.listPic.setCurrentRow(getActualIP)
            self.selectedPic = str(self.UI.listPic.currentItem().text())
            self.UI.preview.setPixmap(self.pathImage + '//' + self.selectedPic + '.png')
            getcolorGain = float('%.3f' % cmds.getAttr(str(imagePlaneShape) + '.colorGainR'))
            self.UI.colorGain.setValue(getcolorGain * 100)
            self.activateOptions(1)
            if self.selectedPic == 'Golden_Ratio' or self.selectedPic == 'Golden_Ratio_Mirror':
                self.UI.aspectRatio.setEnabled(0)
                self.UI.aspectRatio.setChecked(0)
                self.aspectRatio(0)
            else:
                self.UI.aspectRatio.setEnabled(1)
                self.UI.aspectRatio.setChecked(1)
                self.aspectRatio(1)

    def getImagePlane(self, camName):
        if cmds.listRelatives(camName, type='imagePlane', ad=True, c=True):
            getImagePlane = [c for c in cmds.listRelatives(camName, type='imagePlane', ad=True, c=True)]
            getImagePlane = [c for c in cmds.listRelatives(getImagePlane, parent=True)]
            self.UI.imagePlane.addItems(getImagePlane)
            self.imagePlaneShape = str(cmds.listRelatives(self.UI.imagePlane.text(), ad=0, s=1)[0])
            self.activateOptions(1)
        else:
            self.activateOptions(0)

    def userChangePic(self):
        selectedItem = abs(self.UI.listPic.currentRow())
        self.selectedPic = str(self.UI.listPic.currentItem().text())
        self.UI.preview.setPixmap(self.pathImage + '//' + self.selectedPic + '.png')
        if self.UI.imagePlane.text():
            imagePlaneShape = str(cmds.listRelatives(self.UI.imagePlane.text(), ad=0, s=1)[0])
            cmds.setAttr(str(imagePlaneShape + '.imageName'), str(self.pathImage + '//' + self.selectedPic + '.png'),
                         type="string")
            cmds.setAttr(str(imagePlaneShape) + '.imagePlaneName', selectedItem)
            getcolorGain = float('%.3f' % cmds.getAttr(str(imagePlaneShape) + '.colorGainR'))
            self.UI.colorGain.setValue(getcolorGain * 100)
            self.imagePlaneChange()

    def createPushButton(self):
        if self.UI.pb_create.text() == 'Delete':
            self.deleteCurrent()
            self.UI.pb_create.setText('Create Image Plane')
        else:
            cmds.imagePlane(camera=self.UI.listCam.currentText(), showInAllViews=False,
                            fileName=str(self.pathImage) + '//' + self.selectedPic + '.png')
            self.imagePlaneShape = cmds.listRelatives(ad=0, s=1)[0]
            selectedItem = self.UI.listPic.currentRow()
            cmds.select(self.imagePlaneShape)
            cmds.addAttr(ln="imagePlaneName", dv=0)
            cmds.setAttr(str(self.imagePlaneShape) + '.imagePlaneName', selectedItem)
            self.imagePlaneSettings()
            self.cameraSettings()
            self.camAppertureY = cmds.getAttr(self.UI.listCam.currentText() + '.verticalFilmAperture')
            self.resolutionGate(True)
            cmds.select(clear=True)
            self.UI.imagePlane.setText(str(updateImagePlaneList(self.currentCameraShape)[0]))
            self.activateOptions(1)
            self.UI.imagePlaneFrame.setEnabled(1)
            self.UI.pb_create.setText('Delete')
            self.imagePlaneChange()

    def activateOptions(self, value):
        if value:
            self.UI.listCam.setEnabled(value)
            self.UI.listPic.setEnabled(value)
            self.UI.preview.setEnabled(value)
        else:
            self.UI.imagePlaneFrame.setEnabled(value)

        if value == 2:
            value = 0
            self.UI.imagePlaneFrame.setEnabled(value)
            self.UI.listCam.setEnabled(value)
            self.UI.listPic.setEnabled(value)
            self.UI.preview.setEnabled(value)

    def deleteCurrent(self):
        cmds.select(self.UI.listCam.currentText(), r=1)
        shapes = cmds.listRelatives(ad=0, s=1)
        self.imagePlaneShape = cmds.listRelatives(shapes, ad=True, pa=True)

        # If there's already an image plane on the camera selected on the drop down menu
        if self.imagePlaneShape:
            cmds.delete(self.imagePlaneShape)
            cmds.select(clear=True)
        cmds.select(clear=True)
        self.UI.imagePlane.setText('')
        self.activateOptions(0)
        self.UI.imagePlaneFrame.setEnabled(0)
        self.UI.listPic.setCurrentRow(0)
        self.selectedPic = str(self.UI.listPic.currentItem().text())
        self.UI.preview.setPixmap(self.pathImage + '//' + str(self.UI.listPic.currentItem().text()) + '.png')

    def imagePlaneSettings(self):

        # get camera near clip to avoid image plane is before
        camName = cmds.listRelatives(self.UI.listCam.currentText())[0]
        camNearClip = cmds.getAttr(camName + '.nearClipPlane')

        # set settings
        depthValue = abs(camNearClip * 1.1)
        cmds.setAttr(str(self.imagePlaneShape) + '.depth', depthValue)
        cmds.setAttr(str(self.imagePlaneShape) + '.textureFilter', 1)
        getValue = float(self.UI.colorGain.value())
        cmds.setAttr(str(self.imagePlaneShape) + '.fit', 3)

        if getValue != 1.0:
            cmds.setAttr(str(self.imagePlaneShape) + '.colorGain', getValue / 100, getValue / 100, getValue / 100,
                         type="double3")

        cmds.setAttr(str(self.imagePlaneShape) + '.overrideEnabled', 1)
        cmds.setAttr(str(self.imagePlaneShape) + '.overrideDisplayType', 2)

    def cameraSettings(self):
        cmds.setAttr(str(self.UI.listCam.currentText()) + '.displayResolution', 1)
        cmds.setAttr(str(self.UI.listCam.currentText()) + '.displayGateMask', 1)
        cmds.setAttr(str(self.UI.listCam.currentText()) + '.displayFilmGate', 1)

    def colorGainValue(self):
        getValue = float(self.UI.colorGain.value())
        cmds.setAttr(str(self.imagePlaneShape) + '.colorGain', getValue / 100, getValue / 100, getValue / 100,
                     type="double3")

    def overScanValue(self):
        getValue = float(self.UI.overScan.value())
        cmds.setAttr(str(self.UI.listCam.currentText()) + '.overscan', float('%.3f' % (getValue / 100 + 1)))

    def rotateImagePlane(self, state):
        if state:
            cmds.setAttr(str(self.imagePlaneShape) + '.rotate', 180)
        else:
            cmds.setAttr(str(self.imagePlaneShape) + '.rotate', 0)

    def resolutionGate(self, state):

        if state:
            self.UI.gate.setText('Resolution')
            self.getWidth = cmds.getAttr("defaultResolution.width")
            self.getHeight = cmds.getAttr("defaultResolution.height")
            fitToResGate = (self.getHeight * (
                cmds.getAttr(self.UI.listCam.currentText() + '.horizontalFilmAperture'))) / self.getWidth
            cmds.setAttr(str(self.imagePlaneShape) + '.sizeY', fitToResGate)

        else:
            cmds.setAttr(str(self.imagePlaneShape) + '.sizeY', self.camAppertureY)
            self.UI.gate.setText('Film Gate')

    def aspectRatio(self, state):
        if self.UI.fit.text() == 'Horizontal':
            tempState = 2
        elif self.UI.fit.text() == 'Vertical':
            tempState = 3
        else:
            tempState = 0

        if state:
            cmds.setAttr(str(self.imagePlaneShape) + ".fit", 4)

        else:
            cmds.setAttr(str(self.imagePlaneShape) + ".fit", tempState)

    def fitSettings(self, state):
        if state:
            cmds.setAttr(str(self.imagePlaneShape) + ".fit", 2)
            self.UI.fit.setText('Horizontal')
        else:
            cmds.setAttr(str(self.imagePlaneShape) + ".fit", 3)
            self.UI.fit.setText('Vertical')

    def renderSettings(self, setFormat):

        if setFormat == 2 and self.UI.hdFormat.isChecked():
            cmds.setAttr("defaultResolution.height", 1080)
            cmds.setAttr("defaultResolution.width", 1920)
            cmds.setAttr("defaultResolution.deviceAspectRatio", 1.778)
            self.UI.flatFormat.setChecked(False)
            self.UI.scopeFormat.setChecked(False)

        if setFormat == 2 and self.UI.flatFormat.isChecked():
            cmds.setAttr("defaultResolution.height", 1080)
            cmds.setAttr("defaultResolution.width", 1998)
            cmds.setAttr("defaultResolution.deviceAspectRatio", 1.850)
            self.UI.hdFormat.setChecked(False)
            self.UI.scopeFormat.setChecked(False)

        if setFormat == 2 and self.UI.scopeFormat.isChecked():
            cmds.setAttr("defaultResolution.height", 858)
            cmds.setAttr("defaultResolution.width", 2048)
            cmds.setAttr("defaultResolution.deviceAspectRatio", 2.387)
            self.UI.hdFormat.setChecked(False)
            self.UI.flatFormat.setChecked(False)


# Start the main window
def main():
    window = MainWindow()

    # Verify if at least 1 user camera exists in the scene
    if getListCamera() != 'noCamera':
        pass

    # If not, a popup ask the user to create one
    else:
        res = cmds.confirmDialog(title='Warning', message='There is no user Camera in the scene, please create one.',
                                 button=['Ok', 'Create Camera'],
                                 defaultButton='Ok',
                                 cancelButton='createCam',
                                 dismissString='Ok')
        if res == 'Create Camera':
            cmds.camera()
            cmds.setAttr("cameraShape1.displayCameraFrustum", 1)
            cmds.setAttr("cameraShape1.nearClipPlane", 5)
            cmds.setAttr("cameraShape1.farClipPlane", 20000)
        else:
            pass

    window.show()
    window.updateCameraList()


if __name__ == '__main__':
    main()
