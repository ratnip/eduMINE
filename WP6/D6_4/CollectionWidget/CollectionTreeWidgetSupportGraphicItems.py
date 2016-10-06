
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from CollectionSetFactory import *
import os


class Cvor(QGraphicsItem):
    Rect = QRectF(-50,-20,100,40)

    def __init__(self, color, angle, position, collection, attributes=None):
        
        super(Cvor, self).__init__()
        self.offsetOnce=False
        self.color = color
        self.angle = angle
        self.unselectedPen=QPen(Qt.black)
        self.selectedPen=QPen(Qt.blue)
        
        self.collection=collection
        self.collection.graphicsItem=self
        self.dialogOpen=False
        self.prvaRazina=False
        self.zumano=False
        #print len(attributes)
        #print collection
        #print str(collection).find(",")
        #if (len(attributes)>20 and str(collection).find(",")==-1): print "StiZe Nova Godina"
        self.text=str(collection)
        failsafeUvjet=False
        if len(str(collection))>1:
            if str(collection)[1].isdigit()==True: failsafeUvjet=True     # da se ne ubija ovo dolje kod elementa "A"
            
        #if ((len(self.text)==1 and attributes is not None and len(attributes[0])!=1) or (str(collection)[0]=="A" and str(collection)[1].isdigit()==True and str(collection).find(",")==-1)):
        if ((len(self.text)==1 and attributes is not None and len(attributes[0])!=1) or (str(collection)[0]=="A" and failsafeUvjet and str(collection).find(",")==-1)):
            self.prvaRazina=True
            tekstic=" "+self.text+":  "
            self.text=tekstic+attributes[0]
        self.lines=[]
     
        self.setPos(position)
        
        if (QPainter().isActive()==True): 
            fonto=QPainter().font()
            #print "Jedan"
        else:
            fonto=QFont()
            #print "Nijedan"
        fonto.setPointSize(fonto.pointSize()+2)
        
        fm = QFontMetricsF(fonto)  
        self.sirinaTeksta=fm.width(self.text)
        self.sirinaSupportTeksta=fm.width("Sup: XXX   A.V:XXX")
        if self.sirinaTeksta<100: self.rect=QRectF(-50,-20,100,40)
        elif self.sirinaTeksta>260:
            self.rect=QRectF(-150,-20,300,40)
            self.text=self.text[:50]+"..."
            self.sirinaTeksta=fm.width(self.text)
        else: self.rect=QRectF(-(10+self.sirinaTeksta)/2,-20,10+self.sirinaTeksta,40)
        self.rectVeci=QRectF(self.rect)
        self.rectVeci.setHeight(self.rect.height()+10)
        self.setFlags(QGraphicsItem.ItemIsMovable|QGraphicsItem.ItemIsSelectable)
        toolTipText=""
        for at in attributes:
            toolTipText+=at
            if len(at)>3: toolTipText+="\n"
            else: toolTipText+=" "
        toolTipText+="\nSupport: "+str(collection.support)+"\nAdded value: "+str(collection.added_value)
        toolTipText+="\nIRP: "+str(collection.IRP)
        if self.collection.isMaximal==True: toolTipText+="\nMaximal collection"
        self.setToolTip(toolTipText)
        self.setZValue(2)

    def boundingRect(self):
        if (self.zumano==True and self.prvaRazina==True): return self.rectVeci
        else: return self.rect

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.rect)
        return path

    def paint(self, painter, option, widget=None):
        #print "Baba s kolacima ide u sumu saddadqa!"
        painter.setBrush(QBrush(self.color))
        gradient = QLinearGradient(QPointF(5, 5), QPointF(self.sirinaTeksta,30))
        gradient.setColorAt(0, Qt.white)
        gradient.setColorAt(1, QColor(195,197,251))
        painter.setBrush(QBrush(gradient))

                
        
        if self.isSelected():
            painter.setPen(self.selectedPen)
            self.setZValue(3)
        else:
            painter.setPen(self.unselectedPen)
            self.setZValue(2)
        if self.collection.isMaximal==True:
            gradient = QLinearGradient(QPointF(-50, -20), QPointF(50,20))
            gradient.setColorAt(0, Qt.white)
            gradient.setColorAt(1, QColor(240,174,252))
            painter.setBrush(QBrush(gradient))
        if option.levelOfDetail<1.1:
            self.zumano=False
            #self.prvaRazina=False
            painter.drawEllipse(self.rect)
            fonto=painter.font()
            fonto.setPointSize(fonto.pointSize()+2)
            painter.setFont(fonto)
            painter.drawText(-self.sirinaTeksta/2,4,self.text)
        else:
            self.zumano=True
            if self.prvaRazina==True:
                painter.drawEllipse(self.rectVeci)
            else: painter.drawEllipse(self.rect)
            #fm = QFontMetricsF(QPainter().font())  
            #sirinaTeksta=fm.width(self.text)
            fonto=painter.font()
            fonto.setPointSize(fonto.pointSize()+2)
            painter.setFont(fonto)
            if (self.prvaRazina==False): painter.drawText(-self.sirinaTeksta/2, -2,self.text)
            else:  painter.drawText(-self.sirinaTeksta/2, 6,self.text)
            fonto=painter.font()
            fonto.setPointSize(fonto.pointSize()-3)
            painter.setFont(fonto)
            fm = QFontMetricsF(fonto)  
            extraText="Sup:"+str(self.collection.support)+" AdV:"+str(self.collection.added_value)
            sirinaTeksta=fm.width(extraText)
            if (self.prvaRazina==False): painter.drawText(-sirinaTeksta/2,12,  extraText)
            else: painter.drawText(-sirinaTeksta/2,22,  extraText)
            

        #painter.drawText(0,0, "prvo")
        #
        #
        #painter.drawText(0,10, "drvo")        
        
        #ovaj dio koda je zbog toga sto se kolekcije sa jednim elementom "lijepe" jedna preko druge, pa da ih se vizualno razdvoji
        # to se treba naravno raditi samo kod prvog iscrtavanja
        #if (self.offsetOnce==False) and (sum(self.collection.elements)==1) and self.scene().parent().dirty==False:
            #import random
            #buba=random.randint(-20,20)
            #muba=random.randint(-20,20)
            #self.setPos(QPointF(self.pos().x()+buba, self.pos().y()+muba))
            #self.offsetOnce=True
            
        self.scene().parent().paint_links()

   
  