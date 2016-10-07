#!/usr/bin/env python
# Copyright (c) 2007-8 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from CollectionSetFactory import *
import os
from CollectionTreeWidgetSupportDialogs import *
from CollectionTreeWidgetSupportGraphicItems import *
import hashlib
import re

        

        
class CollectionTreeWidget(QWidget):

    
        
    def __init__(self, leftFlow=0, parent=None, atributi=None, layeredCollectionSet=None, inputFileName=None, showDiscards=False, min_abs_sup=None, min_rel_sup=None):
        super(CollectionTreeWidget, self).__init__(parent)
        self.treeDrawn=False
        self.atributi=atributi
        self.lcs=None
        self.dirty=False
        self.inputDataSetName=None
        self.inputFileName=None
        self.dialogOpen=False
        self.sceneHeight=800
        self.sceneWidth=1000
        #self.updown=True
        if inputFileName is not None: initializeLcs(inputFileName, min_abs_sup)
            #print self.lcs
        else: self.lcs=layeredCollectionSet
        
        
        
        #self.min_abs_sup=min_abs_sup
        #self.requested_min_rel_sup=min_rel_sup
        #self.min_rel_sup=None
        
        
        
            
        self.scene = QGraphicsScene(self)
        
        self.scene.setSceneRect(0, 0, 5000, 800)
        self.view = QGraphicsView()
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        #self.view.setFocusPolicy(Qt.NoFocus)
        self.view.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.showDiscards=showDiscards
        self.cvorovi=[]
        self.veze=[]
        
        
        self.inputDataSetNameLabel=QLabel()
        self.attributesNoLabel=QLabel()
        self.transactionsNoLabel=QLabel()
        self.collectionNoLabel=QLabel()
        self.maxcollectionNoLabel=QLabel()
        self.supportLabel=QLabel()
        self.IRPLabel=QLabel()
        self.PILLabel=QLabel()
        #self.addedValueLabel=QLabel()
        #self.addedValueNSLabel=QLabel()
        self.tweakTopLabels()

        inputDatasetBox=QGroupBox("Input Dataset")
        inputDatasetBox.setFlat(False)
        inputDatasetLayout=QVBoxLayout()
        inputDatasetLayout.setAlignment(Qt.AlignLeft)
        inputDatasetLayout.addWidget(self.inputDataSetNameLabel)
        inputDatasetLayout.addWidget(self.attributesNoLabel)
        inputDatasetLayout.addWidget(self.transactionsNoLabel)
        inputDatasetLayout.addWidget(self.collectionNoLabel)
        inputDatasetLayout.addWidget(self.maxcollectionNoLabel)
        inputDatasetLayout.addWidget(self.supportLabel)
        inputDatasetLayout.addWidget(self.IRPLabel)
        inputDatasetLayout.addWidget(self.PILLabel)
        #inputDatasetLayout.addWidget(self.addedValueLabel)
        #inputDatasetLayout.addWidget(self.addedValueNSLabel)
        self.chooseDatasetSupportButton=QPushButton(" &Load dataset/support...")
        #resettreeButton.setFocusPolicy(Qt.NoFocus)
        inputDatasetLayout.addWidget(self.chooseDatasetSupportButton)
        inputDatasetBox.setLayout(inputDatasetLayout)

        treeBox=QGroupBox("Tree characteristics")
        treeBox.setFlat(False)
        treeBoxLayout=QVBoxLayout()
        treeBoxLayout.setAlignment(Qt.AlignTop)
        treeBoxLayout.setAlignment(Qt.AlignLeft)
        smallHLayout=QHBoxLayout()
        smallHLayout.addWidget(QLabel("Strategy:"))
        self.treestratComboBox=QComboBox()
        self.treestratComboBox.addItem("Top down")
        self.treestratComboBox.addItem("Bottom up")
        self.treestratComboBox.addItem("Top down constr.")
        self.treestratComboBox.addItem("Bottom up constr.")
        self.treestratComboBox.setCurrentIndex(1)
        self.treestratComboBox.setEnabled(False)
        smallHLayout.addWidget(self.treestratComboBox)
        treeBoxLayout.addLayout(smallHLayout)
        rootCollectionText="Root collection: <i>default</i>"
        
        self.rootCollectionLabel=QLabel(rootCollectionText)
        treeBoxLayout.addSpacing(5)
        treeBoxLayout.addWidget(self.rootCollectionLabel)
        treeBoxLayout.addSpacing(10)

        smallHLayout2=QHBoxLayout()

        self.closedCollectionRoot=None        
        
        self.resetTreeButton=QPushButton("&Reset positions")
        self.resetTreeButton.setFocusPolicy(Qt.NoFocus)
        
        self.resetTreeButton.setEnabled(False)
        self.resetTreeButton.setToolTip("Start tree from default collection")
        smallHLayout2.addWidget(self.resetTreeButton)
       
        treeBoxLayout.addLayout(smallHLayout2)
        
        treeBox.setLayout(treeBoxLayout)

        tweakSupportBox=QGroupBox("Tweak Support")
        tweakSupportBoxLayout=QVBoxLayout()
        tweakSupportBoxSmallLayout1=QHBoxLayout()
        tweakSupportBoxSmallLayout2=QHBoxLayout()
        changeSupLabel=QLabel("Change abs. sup.:")
        self.changeAbsSupSpinBox = QSpinBox()
        changeSupLabel.setBuddy(self.changeAbsSupSpinBox)
        self.changeSupOkButton = QPushButton("&OK")
        tweakSupportBoxSmallLayout1.addWidget(changeSupLabel)
        tweakSupportBoxSmallLayout1.addWidget(self.changeAbsSupSpinBox)
        tweakSupportBoxSmallLayout1.addWidget(self.changeSupOkButton)
        self.changeSupLeftButton = QPushButton("<--")
        self.changeSupRightButton = QPushButton("-->")
        tweakSupportBoxSmallLayout2.addStretch()
        self.leftSupportLabel=QLabel()
        self.rightSupportLabel=QLabel()
        tweakSupportBoxSmallLayout2.addWidget(self.leftSupportLabel)
        tweakSupportBoxSmallLayout2.addWidget(self.changeSupLeftButton)
        tweakSupportBoxSmallLayout2.addWidget(self.changeSupRightButton)
        tweakSupportBoxSmallLayout2.addWidget(self.rightSupportLabel)
        tweakSupportBoxSmallLayout2.addStretch()
        self.changeAbsSupSpinBox.setEnabled(False)
        self.changeSupOkButton.setEnabled(False)
        self.changeSupLeftButton.setEnabled(False)
        self.changeSupLeftButton.setToolTip("Pre-initialized lower absolute support")
        self.changeSupRightButton.setEnabled(False)
        self.changeSupRightButton.setToolTip("Pre-initialized higher absolute support")
        
        tweakSupportBoxLayout.addLayout(tweakSupportBoxSmallLayout1)
        tweakSupportBoxLayout.addLayout(tweakSupportBoxSmallLayout2)
        tweakSupportBox.setLayout(tweakSupportBoxLayout)

        
        leftLayout=QVBoxLayout()
        leftLayout.addSpacing(30)
        leftLayout.addWidget(inputDatasetBox)
        leftLayout.addSpacing(30)
        leftLayout.addWidget(treeBox)
        leftLayout.addSpacing(30)
        leftLayout.addWidget(tweakSupportBox)
        leftLayout.setAlignment(Qt.AlignTop)
        
         
        zoomSlider = QSlider(Qt.Horizontal)
        zoomSlider.setRange(5, 200)
        zoomSlider.setValue(100)
        legendButton = QPushButton("&Legend")
        legendButton.setFocusPolicy(Qt.NoFocus)
        self.paintRandomBackgroundColor()

        
        self.view.setScene(self.scene)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.view)
        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(zoomSlider)
        bottomLayout.addWidget(legendButton)
        mainLayout.addLayout(bottomLayout)
        
        widgetLayout=QHBoxLayout()
        widgetLayout.addLayout(leftLayout)
        widgetLayout.addLayout(mainLayout)
        
        self.setLayout(widgetLayout)

        self.connect(self.chooseDatasetSupportButton, SIGNAL("clicked()"),
                     self.openChooseDatasetSupportDialog)
        self.connect(self.resetTreeButton, SIGNAL("clicked()"),
                     self.resetTree)
       
        self.connect(self.treestratComboBox, SIGNAL("activated(int)"),
                     self.changeTreeStrategy)
        self.connect(zoomSlider, SIGNAL("valueChanged(int)"),self.zoom)
        self.connect(legendButton, SIGNAL("clicked()"), self.popLegend)
        self.connect(self.changeSupLeftButton, SIGNAL("clicked()"), self.absSupSpinBoxChangedByLeftArrow)
        self.connect(self.changeSupRightButton, SIGNAL("clicked()"), self.absSupSpinBoxChangedByRightArrow)
        self.connect(self.changeAbsSupSpinBox, SIGNAL("valueChanged(int)"), self.absSupSpinBoxChanged)
        self.connect(self.changeSupOkButton, SIGNAL("clicked()"),
                     self.absSupChangedByButton)

        
        if self.lcs is not None: self.paint_tree()


    def absSupSpinBoxChanged(self, value):
        if (value>0): self.changeAbsSupSpinBox.setPrefix("+")
        else: self.changeAbsSupSpinBox.setPrefix("")

    def absSupSpinBoxChangedByRightArrow(self):
        self.absSupChanged(int(self.rightSupportLabel.text()))

    def absSupSpinBoxChangedByLeftArrow(self):
        self.absSupChanged(int(self.leftSupportLabel.text()))  

    def absSupChangedByButton(self):
        self.absSupChanged(self.lcs.min_abs_sup+self.changeAbsSupSpinBox.value())
        
  

    def absSupChanged(self, value):
        self.saveCurrentScene()
        splash_pix = QPixmap('.\\resources\\icons\\initializing.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.show()
        splash.showMessage("")
        treeStrat=None
        currentStratIndex=self.treestratComboBox.currentIndex()
        if currentStratIndex==0: treeStrat=TOP_DOWN
        elif currentStratIndex==1: treeStrat=BOTTOM_UP
        elif currentStratIndex==2: treeStrat=TOP_DOWN_CONSTRAINED
        elif currentStratIndex==3: treeStrat=BOTTOM_UP_CONSTRAINED
        self.initializeLcs(self.inputFileName, value, treeStrat=treeStrat, root=self.closedCollectionRoot)
        self.tweakTopLabels()
        self.tweakSupportLabels()
        splash.hide()
        self.paint_tree()        

    def tweakSupportLabels(self):
        current_sets=os.listdir(".\\resources\\stored_lcs")
        supports = [int(x[(len(self.inputDataSetName)+5):x.find(".lcs")]) for x in current_sets if x.find(self.inputDataSetName)!=-1]
        try:
            supports.sort()
            current_support_index=supports.index(self.lcs.min_abs_sup)
            if current_support_index!=0:
                self.leftSupportLabel.setText(str(supports[current_support_index-1]))
                self.changeSupLeftButton.setEnabled(True)
            else:
                self.leftSupportLabel.setText("")
                self.changeSupLeftButton.setEnabled(False)
            if current_support_index!=len(supports)-1:
                self.rightSupportLabel.setText(str(supports[current_support_index+1]))
                self.changeSupRightButton.setEnabled(True)
            else:
                self.rightSupportLabel.setText("")
                self.changeSupRightButton.setEnabled(False)
        except ValueError:
            self.leftSupportLabel.setText("")
            self.changeSupLeftButton.setEnabled(False)
            self.rightSupportLabel.setText("")
            self.changeSupRightButton.setEnabled(False)
        
        

    def initializeLcs(self, inputFileName, min_abs_sup, treeStrat=BOTTOM_UP, root=None):
        self.inputFileName=inputFileName
        self.lcs=CollectionSetFactory.initializeLcsWithApriori(inputFileName, min_abs_sup=min_abs_sup)
        CollectionSetFactory.build_tree(self.lcs, strategy=treeStrat, root=root)
        self.atributi=self.lcs.attributes
        self.inputDataSetName=os.path.split(inputFileName)[1]
        self.inputDataSetName=self.inputDataSetName[:self.inputDataSetName.rindex(".")]
        
    def paintRandomBackgroundColor(self):
        import random
        random.seed()
        broj=random.randint(0,6)
        if (broj==0): self.changeBackgroundColor(color=QColor(255,150,150))
        elif (broj==1): self.changeBackgroundColor(color=QColor(150,255,150))
        elif (broj==2): self.changeBackgroundColor(color=QColor(150,150,255))
        elif (broj==3): self.changeBackgroundColor(color=QColor(255,200,100))
        else: self.changeBackgroundColor()

    def chooseMaxClosedCollectionAsRoot(self):
        maxDialog=ChooseMaxClosedCollectionDialog(self, self.lcs)
        if maxDialog.exec_():
            #print "Izabrao si:", maxDialog.chosenCollection
            self.closedCollectionRoot=maxDialog.chosenCollection
            
        else:
            self.closedCollectionRoot=None
        
        
    def changeTreeStrategy(self, value):
        if (self.inputDataSetName is not None):
            if (value==0):    # top down
                self.saveCurrentScene()
                self.closedCollectionRoot=None
                CollectionSetFactory.build_tree(self.lcs,strategy=TOP_DOWN)
                #self.resetRootButton.setEnabled(True)
                #self.changeRootButton.setEnabled(True)
                self.rootCollectionLabel.setText("Root collection: <i>default</i>")
                self.paint_tree()
            elif (value==1):    # bottom up
                self.saveCurrentScene()
                self.closedCollectionRoot=None
                CollectionSetFactory.build_tree(self.lcs,strategy=BOTTOM_UP)
                #self.resetRootButton.setEnabled(False)
                #self.changeRootButton.setEnabled(False)
                self.rootCollectionLabel.setText("Root collection: <i>default</i>")
                self.paint_tree()
            elif (value==2):    # top down constr.
                self.saveCurrentScene()
                self.chooseMaxClosedCollectionAsRoot()
                if (self.closedCollectionRoot is not None):
                    CollectionSetFactory.build_tree(self.lcs,strategy=TOP_DOWN_CONSTRAINED, root=self.closedCollectionRoot)
                    self.rootCollectionLabel.setText("Root collection: "+str(self.closedCollectionRoot))
                    self.paint_tree(root=self.closedCollectionRoot)
                else:
                    self.treestratComboBox.setCurrentIndex(0)
                    self.changeTreeStrategy(0)
            elif (value==3):    # bottom up constr.
                self.saveCurrentScene()
                self.chooseMaxClosedCollectionAsRoot()
                if (self.closedCollectionRoot is not None):
                    CollectionSetFactory.build_tree(self.lcs,strategy=BOTTOM_UP_CONSTRAINED, root=self.closedCollectionRoot)
                    self.rootCollectionLabel.setText("Root collection: "+str(self.closedCollectionRoot))
                    self.paint_tree(root=self.closedCollectionRoot)
                else:
                    self.treestratComboBox.setCurrentIndex(1)
                    self.changeTreeStrategy(1)
        self.tweakTopLabels()

    def resetTree(self):
        self.dirty=False
        for cvor in self.cvorovi: cvor.offsetOnce=False
        self.paint_tree(doNotLoad=True)
        
            
        
    def tweakTopLabels(self):
        if (self.inputDataSetName is not None):
            self.inputDataSetNameLabel.setText("<font size=+2><b>"+self.inputDataSetName+"</b></font>")
            countAttributes=len(self.atributi)
            self.attributesNoLabel.setText("Attributes:\t"+str(countAttributes))
            if self.lcs is not None: self.transactionsNoLabel.setText("Transactions:\t"+str(self.lcs.transactionsTotal))
            countCollections=0
            if self.lcs is not None:
                for razina in self.lcs.layers:
                    countCollections+=len(razina)
            self.collectionNoLabel.setText("Collections:\t"+str(countCollections))
            if (self.lcs.maximalsFlagged):
                self.maxcollectionNoLabel.setText("Max. collections: "+str(len(self.lcs.maximals)))
            else:
                self.maxcollectionNoLabel.setText("")
            if (self.lcs.min_abs_sup is not None and self.lcs.min_rel_sup is not None):
                self.supportLabel.setText("Min. support:\t<b><font size=+1>"+str(self.lcs.min_abs_sup)+"</font></b>\t    ("+str("%.2f" % (100*self.lcs.min_rel_sup))+"%)")
            if (self.lcs.IRPcalculated==True):
                self.IRPLabel.setText("Total IRP:\t"+str(self.lcs.totalIRP))
            else:  self.IRPLabel.setText("")
            if (self.lcs.totalBoundAddedValueCalculated==True):
                #self.addedValueLabel.setText("Total add.val.:\t"+str(self.lcs.totalBoundAddedValue))+"   ("+str("%.2f" % (100*1.*self.lcs.totalBoundAddedValue/self.lcs.totalAddedValue))+"% of"+str(self.lcs.totalAddedValue)+")"
                #self.addedValueLabel.setText("Total AV:\t"+str(self.lcs.totalBoundAddedValue)+"   ("+str("%.2f" % (100*1.*self.lcs.totalBoundAddedValue/self.lcs.totalAddedValue))+"% of "+str(self.lcs.totalAddedValue)+")")
                self.PILLabel.setText("Pot. inf. loss:\t"+str("%.2f" % (100*1.*(self.lcs.totalAddedValue-self.lcs.totalBoundAddedValue)/self.lcs.totalAddedValue))+"%")
                #self.addedValueNSLabel.setText("Total NS AV:\t"+str(self.lcs.totalBoundAddedValueNoSingletons)+"   ("+str("%.2f" % (100*1.*self.lcs.totalBoundAddedValueNoSingletons/self.lcs.totalAddedValueNoSingletons))+"% of "+str(self.lcs.totalAddedValueNoSingletons)+")")
            else:
                self.PILLabel.setText("")
                #self.addedValueLabel.setText("")
                #self.addedValueNSLabel.setText("")
                    
        else:
            self.inputDataSetNameLabel.setText("<font size=+2><b>NO DATASET</b></font>")
            self.attributesNoLabel.setText("No attributes.")
            self.transactionsNoLabel.setText("No transactions.")
            self.collectionNoLabel.setText("No collections.")
            self.maxcollectionNoLabel.setText("")
   

    def openChooseDatasetSupportDialog(self):
        #test=False
        #filename = QFileDialog.getOpenFileName(self, 'Open file','/home')
        #print "Hello!"
        dialog=ChooseDatasetSupportDialog(self)
        
        #self.dialogOpen=True
        if dialog.exec_():
            if (self.dirty==True): self.saveCurrentScene()
            #self.inputFileName=str(dialog.datasetComboBox.itemText(dialog.datasetComboBox.currentIndex()))
            inputName=str(dialog.datasetComboBox.itemText(dialog.datasetComboBox.currentIndex()))
            inputAbsSup=dialog.minAbsSupSpinBox.value()
            a=None
            if (dialog.tcs is not None) and (len(dialog.tcs.transactions)>100) and (CollectionSetFactory.alreadyInitialized(inputName, inputAbsSup)==False):
                #print "Tute sam"
                msgBox=QMessageBox()
                msgBox.setWindowTitle("Warning: initialization required")
                msgBox.setText("The closed connections for this dataset and support have not yet been initialized.")
                msgBox.setInformativeText("Do you want to initialize them now? (this might take a while)")
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Cancel)
                a=msgBox.exec_()
            if ((a is None) or a==QMessageBox.Ok):
                print a
                splash_pix = QPixmap('.\\resources\\icons\\initializing.png')
                splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
                splash.setMask(splash_pix.mask())
                splash.show()
                splash.showMessage("")
                self.initializeLcs(inputName, inputAbsSup)
                self.tweakTopLabels()
                self.tweakSupportLabels()
                self.treestratComboBox.setCurrentIndex(1)
                splash.hide()
            #else: print a
            self.paint_tree()
                
                    
              

        """
        if (self.lcs is not None and test):
            dialog = ChooseClosedCollectionDialog.ChooseClosedCollectionDialog(self.lcs, self)
            if dialog.exec_():
                pass
                #self.lcs = dialog.numberFormat()
        """
        #self.paint_tree()
    
    
    def changeBackgroundColor(self, color=QColor(220,200,250)):
       
        height=self.sceneHeight
        width=self.sceneWidth
        gradient = QLinearGradient(QPointF(width/2, 0), QPointF(width/2, height))
        gradient.setColorAt(0, Qt.white)
        gradient.setColorAt(1, color)
        self.view.setBackgroundBrush(QBrush(gradient))
        
    

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        colorSubmenu=QMenu("Change background color:", menu)
       
        menu.addMenu(colorSubmenu)
        redBackgroundAction = colorSubmenu.addAction("&Red")
        greenBackgroundAction = colorSubmenu.addAction("&Green")
        blueBackgroundAction = colorSubmenu.addAction("&Blue")
        yellowBackgroundAction = colorSubmenu.addAction("&Yellow")
        orangeBackgroundAction = colorSubmenu.addAction("&Orange")
        purpleBackgroundAction = colorSubmenu.addAction("&Purple")
        cyanBackgroundAction = colorSubmenu.addAction("&Cyan")
        magentaBackgroundAction = colorSubmenu.addAction("&Magenta")
        import functools
        redBackgroundFunction=functools.partial(self.changeBackgroundColor, QColor(255,150,150))
        greenBackgroundFunction=functools.partial(self.changeBackgroundColor, QColor(150,255,150))
        blueBackgroundFunction=functools.partial(self.changeBackgroundColor, QColor(150,150,255))
        yellowBackgroundFunction=functools.partial(self.changeBackgroundColor, QColor(255,255,150))
        orangeBackgroundFunction=functools.partial(self.changeBackgroundColor, QColor(255,200,100))
        purpleBackgroundFunction=functools.partial(self.changeBackgroundColor)
        cyanBackgroundFunction=functools.partial(self.changeBackgroundColor, QColor(100,255,255))
        magentaBackgroundFunction=functools.partial(self.changeBackgroundColor, QColor(255,100,255))
        self.connect(redBackgroundAction, SIGNAL("triggered()"), redBackgroundFunction)
        self.connect(greenBackgroundAction, SIGNAL("triggered()"), greenBackgroundFunction)
        self.connect(blueBackgroundAction, SIGNAL("triggered()"), blueBackgroundFunction)
        self.connect(yellowBackgroundAction, SIGNAL("triggered()"), yellowBackgroundFunction)
        self.connect(orangeBackgroundAction, SIGNAL("triggered()"), orangeBackgroundFunction)
        self.connect(purpleBackgroundAction, SIGNAL("triggered()"), purpleBackgroundFunction)
        self.connect(cyanBackgroundAction, SIGNAL("triggered()"), cyanBackgroundFunction)
        self.connect(magentaBackgroundAction, SIGNAL("triggered()"), magentaBackgroundFunction)
      
        menu.exec_(event.globalPos())
        
    def saveCurrentScene(self):
        if (self.inputDataSetName is not None):
            import pickle
            sceneCoordinates=[]
            graphName=os.getcwd()+"\\resources\\graphs\\"+self.inputDataSetName+"_sup_"+str(self.lcs.min_abs_sup)+"_"+str(self.lcs.treeStrat)+".gph"
            graphName=os.getcwd()+"\\resources\\graphs\\"+self.inputDataSetName+"_sup_"+str(self.lcs.min_abs_sup)+"_"+str(self.lcs.treeStrat)
            if (self.closedCollectionRoot is not None):
                newThing = hashlib.md5(str(self.closedCollectionRoot)).digest().encode("base64")[1:10]
                newThing = re.sub('[^0-9a-zA-Z]+', '_', newThing)
                graphName+="_"+newThing
            graphName+=".gph"
            print "Snimam graf u datoteku: ", graphName
            for cvor in self.cvorovi:sceneCoordinates.append(cvor.pos())
            f=open(graphName,"w")
            p=pickle.Pickler(f)
            p.dump(sceneCoordinates)
            f.close()
            self.dirty=False
            
    def closeEvent(self,v):
        #print "Hello!"
        self.saveCurrentScene()

        
    def popLegend(self):
        if self.atributi is None: return
        legendaString=""
        slovo=65
        for atribut in self.atributi:
            legendaString+=chr(slovo)
            legendaString+=" - "
            legendaString+=atribut
            legendaString+="\n"
            slovo+=1
        QMessageBox.information(self,
                                "Legend",
                                legendaString)

        
    def zoom(self, value):
        factor = value / 100.0
        matrix = self.view.matrix()
        matrix.reset()
        matrix.scale(factor, factor)
        self.view.setMatrix(matrix)
        
    def valueChanged(self):
        
        self.update()


    def values(self):
        pass
       


    def minimumSizeHint(self):
        return QSize(400,400)


    def resizeEvent(self, event=None):
        pass
       

    def paint_links(self):
         while(len(self.veze)):
             self.scene.removeItem(self.veze.pop())
         for cvor in self.cvorovi:
                if (len(cvor.collection.links)!=0):
                    for link in cvor.collection.links:
                        if (link.destination.graphicsItem is not None):
                            newline=self.scene.addLine(QLineF(cvor.pos(), link.destination.graphicsItem.pos()), QPen(Qt.black))
                            newline.setZValue(1)
                            self.veze.append(newline)
        
    def paint_tree(self, event=None, broj_razina=10, custom=True, pozadina=Qt.magenta, showBoxes=True, doNotLoad=False, root=None):

        #CollectionSetFactory.print_tree(self.lcs)
        
        items = self.scene.items()
        if len(items)!=0:
            self.veze=[]
            self.cvorovi=[]
            for item in items:
                self.scene.removeItem(item)
            

        
        if (self.lcs is not None and self.lcs.treeBuilt==True):
            self.resetTreeButton.setEnabled(True)
            self.treestratComboBox.setEnabled(True)
            self.chooseDatasetSupportButton.setText("&Change dataset/support...")
            self.changeAbsSupSpinBox.setEnabled(True)
            self.changeSupOkButton.setEnabled(True)
            self.changeAbsSupSpinBox.setValue(0)
            self.changeAbsSupSpinBox.setMinimum(1-self.lcs.min_abs_sup)
            self.changeAbsSupSpinBox.setMaximum(self.lcs.transactionsTotal-self.lcs.min_abs_sup)
           
            
            CollectionSetFactory.sort_layers(self.lcs,how=BY_SUPPORT)
            CollectionSetFactory.sort_layers(self.lcs,how=BY_BOUNDNESS)
            #print self.lcs
            if (self.lcs.layers_total==0): return            
            self.current_level=self.lcs.layers_total-1
            if root is not None:  self.current_level=root.elements_total
            #print self.lcs
            #print CollectionSetFactory.print_tree(self.lcs)
            while (len(self.lcs.layers[self.current_level])==0): self.current_level-=1
            while (self.lcs.layers[self.current_level][0].boundness!=0):    #na ovoj razini nema clanova drveta
                #print self.lcs.layers[self.current_level][0]
                #print self.current_level
                #print self.lcs.layers[self.current_level][0]
                self.current_level-=1
                if (self.current_level==-1):
                    print "Drvo nema clanova!!!!"
                    return

                  
            visina=self.sceneHeight
            sirina=self.sceneWidth
            self.visina_pojasa=1.*visina/self.current_level/1.5
            self.baseline=self.sceneHeight-100
            self.root_x=2500

           
            self.tree_depth=self.current_level              

            self.treeStarted=False            
            for razina in self.lcs.layers:
                for kolekcija in razina:
                    kolekcija.graphicsItem=None  #nijedna kolekcija nije narisana

            ogledna_razina=self.current_level
            self.micanjeMalihDrvacaPredznak=-1
            self.micanjeMalihDrvacaPomak=self.sceneWidth/3
            self.micanjeMalihDrvacaDefaultPomak=self.micanjeMalihDrvacaPomak
            while (ogledna_razina!=-1):
                for kolekcija in self.lcs.layers[ogledna_razina]:
                    #print kolekcija
                    if (kolekcija.graphicsItem is None): self.paint_collection(kolekcija)
                ogledna_razina-=1
                self.tree_depth=ogledna_razina   #novo potencijalno drfce
            

            for i in range(self.lcs.layers_total):
                if (showBoxes==True and self.inputDataSetName is not None): self.scene.addRect(-self.scene.width(),self.baseline-i*self.visina_pojasa-self.visina_pojasa/2, 3*self.scene.width(), self.visina_pojasa, QPen(Qt.white), QBrush(Qt.transparent))
           
            if (self.dirty==False and doNotLoad==False):   #prvo crtanje, provjeri da li ima snimljeni graf
                import pickle
                graphName=self.inputDataSetName+"_sup_"+str(self.lcs.min_abs_sup)+"_"+str(self.lcs.treeStrat)
                if (self.closedCollectionRoot is not None):
                    newThing = hashlib.md5(str(self.closedCollectionRoot)).digest().encode("base64")[1:10]
                    newThing = re.sub('[^0-9a-zA-Z]+', '_', newThing)
                    graphName+="_"+newThing
                graphName+=".gph"
                if graphName in os.listdir(os.getcwd()+"\\resources\\graphs"):
                    graphName=os.getcwd()+"\\resources\\graphs\\"+graphName
                    f = open(graphName, "r")
                    p = pickle.Unpickler(f)
                    graphCoords=None
                    graphCoords=p.load()
                    for cvor in self.cvorovi:
                        cvor.setPos(graphCoords.pop(0))
            self.dirty=True
            self.treeDrawn=True
        else:
            #self.changeAbsSupSpinBox.setEnabled(True)
            #self.changeSupOkButton.setEnabled(True)
            self.changeAbsSupSpinBox.setValue(0)
            self.changeAbsSupSpinBox.setMinimum(1-self.lcs.min_abs_sup)
            self.changeAbsSupSpinBox.setMaximum(self.lcs.transactionsTotal-self.lcs.min_abs_sup)
            
           
            
        """         
        else:
            #testiram
            broj_razina=10
            visina=self.scene.height()
            sirina=self.scene.width()
            pojas=1.*visina/broj_razina
            for i in range(broj_razina):
                if (showBoxes): self.scene.addRect(0,i*pojas, sirina, pojas, QPen(Qt.white), QBrush(Qt.transparent))
        """
            
    def calculate_y_coord(self, collection):
        #visina=self.scene.height()
        noviY=(self.baseline-(self.tree_depth+1-collection.elements_total)*self.visina_pojasa)
        if collection.elements_total==1:
            import random
            buba=random.randint(-20,20)
            noviY+=buba
            
        return noviY

    def calculate_x_coord(self, collection, parent, childInRow):
        broj_elemenata_roditelja=parent.collection.elements_total
        moj_broj_elemenata=collection.elements_total
        razlika_u_elementima=broj_elemenata_roditelja-moj_broj_elemenata-1
        #print parent.collection.elements, parent.pos().x()
        noviX=parent.pos().x()-50+razlika_u_elementima*50+(childInRow-1)*100
        if collection.elements_total==1:
            import random
            buba=random.randint(-5,5)
            noviX+=buba
        return noviX
            
    def paint_collection(self,collection, parentCvor=None, childInRow=0):
        #print "Jedan"
        stanje=collection.boundness
        visina=self.sceneHeight
        sirina=self.sceneWidth
        if (stanje==0):                          #kolekcija je dio drveta
            #print "Dva"
            color = QColor(255,255, 255)
           
            if (parentCvor is None):             #kolekcija je korijen jednog od stabala
                #print "Tri"
                cvorko=Cvor(color, 0, QPointF(self.root_x,self.baseline), collection, attributes=self.lcs.get_collection_attributes(collection))

                self.root_x+=self.micanjeMalihDrvacaPredznak*self.micanjeMalihDrvacaPomak
                self.micanjeMalihDrvacaPredznak*=(-1)
                self.micanjeMalihDrvacaPomak+=self.micanjeMalihDrvacaDefaultPomak
                
            
            else:                    #kolekcija je dite
                #print "Cetri"
                cvorko=Cvor(color, 0, QPointF(self.calculate_x_coord(collection, parentCvor, childInRow),self.calculate_y_coord(collection)), collection, attributes=self.lcs.get_collection_attributes(collection))
            self.scene.addItem(cvorko)
            self.cvorovi.append(cvorko)
            if (len(collection.links)!=0):
                #print "Sest"
                ditePoRedu=1
                for veza in collection.links:
                    #print collection.elements
                    #print collection.elements, "-->", veza.destination.elements
                    #print "Sedam"
                    self.paint_collection(veza.destination, parentCvor=cvorko, childInRow=ditePoRedu)
                    ditePoRedu+=1
                
                
                
                
                
                
        elif (stanje==2):
            color = QColor(200,200, 200)
            collection.graphicsItem=1    #placeholder
        else:
            color = QColor(255,0, 0)
            collection.graphicsItem=1    #placeholder
        
        
        
def main():
    import sys
    #atributi=['Pegla', 'Toster', 'Motokultivator']
    app = QApplication(sys.argv)
    #form = CollectionTreeWidget(atributi=None, inputFileName="Primjer1.tab", min_abs_sup=2, showDiscards=False)
    #form = CollectionTreeWidget(atributi=None, inputFileName="Primjer1_sup_1_BU.lcs", showDiscards=False)
    #form = CollectionTreeWidget(atributi=None, inputFileName="Computer_shop.tab", min_abs_sup=20, showDiscards=False)
    form = CollectionTreeWidget(atributi=None, inputFileName=None, showDiscards=False)
    #form.connect(form, SIGNAL("valueChanged"), valueChanged)
    form.setWindowTitle("CollectionTree")
    #form.move(0, 0)
    form.show()
    #form.resize(1000, 1000)
    app.exec_()

if __name__ == "__main__":
    main()
    
    

