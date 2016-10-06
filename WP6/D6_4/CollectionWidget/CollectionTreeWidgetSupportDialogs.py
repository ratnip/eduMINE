from PyQt4.QtCore import *
from PyQt4.QtGui import *
from CollectionSetFactory import *
import os

class ChooseMaxClosedCollectionDialog(QDialog):

    def __init__(self, parent=None, lcs=None):
        super(ChooseMaxClosedCollectionDialog, self).__init__()
        self.StyleSheet = """
            QComboBox { color: darkblue; }
            QSpinBox { color: black; }
            QSpinBox[initialized="true"] {
            background-color: rgb(185, 248, 160);
            color: darkblue;
            }
            QDoubleSpinBox { color: black; }
            QDoubleSpinBox[initialized="true"] {
            background-color: rgb(185, 248, 160);
            color: darkblue;
            }
            """
        singletonCollectionsGroupBox=QGroupBox("Frequent items")
        singletonCollectionsLayout=QVBoxLayout()
        maxClosedCollectionGroupBox=QGroupBox("Maximal closed connections")
        maxClosedCollectionsLayout=QVBoxLayout()
        self.singletonList=QListWidget()
        self.singletonList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.collList=QListWidget()

        self.chosenCollection=None        
        
        #self.lcs=lcs
        CollectionSetFactory.sort_layers(lcs, how=ALPHABETICALLY)
        self.singletons=lcs.layers[0]
        self.maximals=lcs.maximals
        self.current_maximals=self.maximals
        i=0
       
        for kolekcija in lcs.layers[0]:
            for index in range(len(kolekcija.elements)):
                if kolekcija.elements[index]==1: break   
            self.singletonList.addItem(str(kolekcija)+": "+lcs.attributes[index])
                #listica.append(str(kolekcija)+": "+lcs.attributes[index])
            i+=1
        #listica.sort()
        #for item in listica: self.singletonList.addItem(item)
        for kolekcija in lcs.maximals:
            self.collList.addItem(str(kolekcija)+"\tSupport: "+str(kolekcija.support)+"\tAdded_value: "+str(kolekcija.added_value))
        singletonCollectionsLayout.addWidget(self.singletonList)
        maxClosedCollectionsLayout.addWidget(self.collList)
        singletonCollectionsGroupBox.setLayout(singletonCollectionsLayout)
        maxClosedCollectionGroupBox.setLayout(maxClosedCollectionsLayout)
        mainLayout=QHBoxLayout()
        mainLayout.addWidget(singletonCollectionsGroupBox)
        mainLayout.addWidget(maxClosedCollectionGroupBox)
        
        okCancelLayout=QHBoxLayout()
        okButton = QPushButton("&OK")
        cancelButton = QPushButton("&Cancel")
        okCancelLayout.addStretch()
        okCancelLayout.addWidget(okButton)
        okCancelLayout.addWidget(cancelButton)

        layout=QVBoxLayout()
        layout.addLayout(mainLayout)
        layout.addLayout(okCancelLayout)
        self.setLayout(layout)
        self.setWindowTitle("Choose maximal closed collection for root:")
        self.connect(okButton, SIGNAL("clicked()"),
                     self, SLOT("accept()"))
        self.connect(cancelButton, SIGNAL("clicked()"),
                     self, SLOT("reject()"))
        self.connect(self.singletonList, SIGNAL("itemSelectionChanged()"), self.singletonsChanged)
        self.connect(self.collList, SIGNAL("itemSelectionChanged()"), self.collectionChosen)
        

    def collectionChosen(self):
        i=0
        for i in range(self.collList.count()):
            if self.collList.isItemSelected(self.collList.item(i)): break
        
       
        
        self.chosenCollection=self.current_maximals[i]
        
    def singletonsChanged(self):
        izabraneKolekcije=[]
        for i in range(self.singletonList.count()):
            if self.singletonList.isItemSelected(self.singletonList.item(i)):
                izabraneKolekcije.append(self.singletons[i])
        self.updateMaxCollections(izabraneKolekcije)

    def updateMaxCollections(self, izabraneKolekcije):
        #for mala_kolekcija in izabraneKolekcije: print mala_kolekcija
        self.collList.clear()
        self.current_maximals=[]
        unija=None
        if (len(izabraneKolekcije)>0): unija=izabraneKolekcije[0]
        if (len(izabraneKolekcije)>1):
            for mala_kolekcija in izabraneKolekcije[1:]:
                unija=unija.XOR(mala_kolekcija)
        if (unija is not None):
            for kolekcija in self.maximals:
                if (unija.is_subset_of(kolekcija)) and kolekcija not in self.current_maximals:
                    self.current_maximals.append(kolekcija)
            for kolekcija in self.current_maximals:
                self.collList.addItem(str(kolekcija)+"\tSupport: "+str(kolekcija.support)+"\tAdded_value: "+str(kolekcija.added_value))
        else:
            for kolekcija in self.maximals:
                self.collList.addItem(str(kolekcija)+"\tSupport: "+str(kolekcija.support)+"\tAdded_value: "+str(kolekcija.added_value))
            
                
                
        
        
        
        
        

class ChooseDatasetSupportDialog(QDialog):

   

    def __init__(self, parent=None):
        self.StyleSheet = """
            QComboBox { color: darkblue; }
            QSpinBox { color: black; }
            QSpinBox[initialized="true"] {
            background-color: rgb(185, 248, 160);
            color: darkblue;
            }
            QDoubleSpinBox { color: black; }
            QDoubleSpinBox[initialized="true"] {
            background-color: rgb(185, 248, 160);
            color: darkblue;
            }
            """
        self.tcs=None
        super(ChooseDatasetSupportDialog, self).__init__()
        
        inputDatasetBox=QGroupBox("Input dataset")
        inputDatasetBox.setFlat(False)
        inputDatasetLayout=QVBoxLayout()
        inputDatasetFirstRowLayout=QHBoxLayout()
        datasetLabel = QLabel("&Dataset:")
        self.datasetComboBox = QComboBox()
        self.minAbsSupSpinBox = QSpinBox()
        self.propagateSupport=False
        self.minRelSupSpinBox = QDoubleSpinBox()
        datasetLabel.setBuddy(self.datasetComboBox)
        self.datasetComboBox.addItems(self.getDatasetList())
        self.datasetCharacteristicsLabel=QLabel()
        if (parent.inputFileName is not None):
            self.datasetComboBox.setCurrentIndex(self.datasetComboBox.findText(os.path.split(parent.inputFileName)[1]))
            self.datasetChanged(self.datasetComboBox.findText(os.path.split(parent.inputFileName)[1]))
        else:
            self.datasetComboBox.setCurrentIndex(0)
            self.datasetChanged(0)
        self.changeSpinboxColor()
        
        
        browseButton=QPushButton("&Browse...")
        browseButton.setFocusPolicy(Qt.NoFocus)
        inputDatasetFirstRowLayout=QHBoxLayout()
        inputDatasetFirstRowLayout.addWidget(datasetLabel)
        inputDatasetFirstRowLayout.addWidget(self.datasetComboBox)
        inputDatasetFirstRowLayout.addStretch()
        inputDatasetFirstRowLayout.addWidget(browseButton)
        inputDatasetLayout.addLayout(inputDatasetFirstRowLayout)
        inputDatasetLayout.addWidget(self.datasetCharacteristicsLabel)
        inputDatasetBox.setLayout(inputDatasetLayout)

        

        supportBox=QGroupBox("Choose minimal support")
        supportBoxLayout=QHBoxLayout()
        minAbsSupLabel=QLabel("Absolute support:")
        
        self.minAbsSupSpinBox.setMinimum(1)
        
        
        minAbsSupLabel.setBuddy(self.minAbsSupSpinBox)
        self.minAbsSupSpinBox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.minAbsSupSpinBox.setProperty("initialized", QVariant(True))
        self.minRelSupSpinBox.setProperty("initialized", QVariant(True))
        minRelSupLabel=QLabel("Relative support:")
        
        self.minRelSupSpinBox.setSuffix("%")
        self.minRelSupSpinBox.setMaximum(100.00)
        minRelSupLabel.setBuddy(self.minRelSupSpinBox)
        self.minRelSupSpinBox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.fixSpinboxes()
        if (parent.inputFileName is not None):
            self.minAbsSupSpinBox.setValue(parent.lcs.min_abs_sup)
        #self.initializedLabel=QLabel()
        
        supportBoxLayout.addWidget(minAbsSupLabel)
        supportBoxLayout.addWidget(self.minAbsSupSpinBox)
        supportBoxLayout.addStretch()
        supportBoxLayout.addWidget(minRelSupLabel)
        supportBoxLayout.addWidget(self.minRelSupSpinBox)
        #supportBoxLayout.addWidget(self.initializedLabel)
        supportBox.setLayout(supportBoxLayout)

        
        
        
        


        
        okButton = QPushButton("&OK")
        #okButton.setFocus()
        cancelButton = QPushButton("&Cancel")


        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)


        layout = QVBoxLayout()
        
        layout.addWidget(inputDatasetBox)
        layout.addWidget(supportBox)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        self.connect(self.minAbsSupSpinBox, SIGNAL("valueChanged(int)"), self.absSupportChanged)
        self.connect(self.minRelSupSpinBox, SIGNAL("valueChanged(double)"), self.relSupportChanged)
        self.connect(okButton, SIGNAL("clicked()"),
                     self, SLOT("accept()"))
        self.connect(cancelButton, SIGNAL("clicked()"),
                     self, SLOT("reject()"))
        self.connect(self.datasetComboBox, SIGNAL("activated(int)"),
                     self.datasetChanged)
        self.connect(browseButton, SIGNAL("clicked()"),
                     self.openChooseFileDialog)
        self.setWindowTitle("Choose dataset/support")
        self.setStyleSheet(self.StyleSheet)
        self.changeSpinboxColor()

    def fixSpinboxes(self):    
        if self.tcs is not None:
            self.minAbsSupSpinBox.setMaximum(len(self.tcs.transactions))
            self.minRelSupSpinBox.setMinimum(100./len(self.tcs.transactions))
            self.minAbsSupSpinBox.setEnabled(True)
            self.minRelSupSpinBox.setEnabled(True)
            self.changeSpinboxColor()
        else:
            self.minAbsSupSpinBox.setEnabled(False)
            self.minRelSupSpinBox.setEnabled(False)

    def absSupportChanged(self, value):
        if self.tcs is not None:
            if (self.propagateSupport==False):                  #korisnik mijenja, nije automatski
                self.propagateSupport=True
                self.minRelSupSpinBox.setValue(100.*value/len(self.tcs.transactions))
            else:                                               #broj se mijenja automatski, ne propagiraj
                self.propagateSupport=False
            self.changeSpinboxColor()
                
                

    def relSupportChanged(self, value):
        if (self.propagateSupport==False):
            self.propagateSupport=True
            self.minAbsSupSpinBox.setValue(int(len(self.tcs.transactions)*value/100))
        else:
            self.propagateSupport=False
            

    def changeSpinboxColor(self):
        if self.tcs is not None:
            if (CollectionSetFactory.alreadyInitialized(str(self.datasetComboBox.itemText(self.datasetComboBox.currentIndex())), self.minAbsSupSpinBox.value())):
                self.minAbsSupSpinBox.setProperty("initialized", QVariant(True))
                self.minRelSupSpinBox.setProperty("initialized", QVariant(True))
                self.setStyleSheet(self.StyleSheet)
            else:
                self.minAbsSupSpinBox.setProperty("initialized", QVariant(False))
                self.minRelSupSpinBox.setProperty("initialized", QVariant(False))
                self.setStyleSheet(self.StyleSheet)
               
    def getDatasetList(self):
        return os.listdir(os.getcwd()+"\\resources\\input_datasets")

    def datasetChanged(self, value):
        #print value
        inputName="resources\\input_datasets\\"+str(self.datasetComboBox.itemText(value))
        if inputName is not None and inputName!="":
            self.tcs=CollectionSetFactory.loadTransactionSetFromFile(inputName)
            self.datasetCharacteristicsLabel.setText((str(len(self.tcs.attributes))+ " attributes, "+str(len(self.tcs.transactions))+" transactions."))
        else:
            self.tcs=None
            self.datasetCharacteristicsLabel.setText("No datasets available.")
        self.fixSpinboxes()
        self.minAbsSupSpinBox.setValue(1)
        self.changeSpinboxColor()

    def openChooseFileDialog(self):
        filename = str(QFileDialog.getOpenFileName(self, 'Open dataset','.', "Tab files (*.tab)"))
        newtcs=None
        if (filename is not None and filename!=""):
            newtcs=CollectionSetFactory.loadTransactionSetFromFile(filename)
        if (newtcs is not None):
            itemCount=self.datasetComboBox.count()
            for i in range(itemCount): self.datasetComboBox.removeItem(0)
            self.datasetComboBox.addItems(self.getDatasetList())
            newIndex=self.datasetComboBox.findText(os.path.split(filename)[1])
            self.datasetComboBox.setCurrentIndex(newIndex)
            self.datasetChanged(newIndex)

if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    #form = CollectionTreeWidget(atributi=None, inputFileName="Primjer1.tab", min_abs_sup=2, showDiscards=False)
    #form = CollectionTreeWidget(atributi=None, inputFileName="Primjer1_sup_1_BU.lcs", showDiscards=False)
    #form = CollectionTreeWidget(atributi=None, inputFileName="Computer_shop.tab", min_abs_sup=20, showDiscards=False)
    lcs=CollectionSetFactory.initializeLcsWithApriori(inputFileName="Primjer1.tab", min_abs_sup=1)
    form = ChooseMaxClosedCollectionDialog(parent=None, lcs=lcs)
    #form.connect(form, SIGNAL("valueChanged"), valueChanged)
    #form.move(0, 0)
    form.show()
    #form.resize(1000, 1000)
    app.exec_()
            
