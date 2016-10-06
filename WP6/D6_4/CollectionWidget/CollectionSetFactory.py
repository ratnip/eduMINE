# -*- coding: utf-8 -*-


import sys
import time

DEBUG=True
TIMED=True


#konstante za sort
ALPHABETICALLY=0
BY_SUPPORT=1
BY_ADDED_VALUE=2
BY_BOUNDNESS=3

#konstante za drvo
BOTTOM_UP=1
TOP_DOWN=2
BOTTOM_UP_CONSTRAINED=3
TOP_DOWN_CONSTRAINED=4


#konstante za elemente strukture
BOUND=0
UNKNOWN=1
DISCARDED=2


startTime=time.clock()

#klasa koja čuva skup transakcija, te vektor atributa tih transakcija
class TransactionSet():
    def __init__(self, transactions=[], attributes=None):
        self.transactions=transactions
        self.attributes=attributes

    

#klasa koja čuva skup kolekcija, organiziran u razine (prema broju elemenata)
        #cuva i informaciju o minimalnom supportu nad kojim je izradjen taj skup
class LayeredCollectionSet():

    def __init__(self, layers=[], min_abs_sup=None, min_rel_sup=None, attributes=None):
        self.layers=layers
        self.min_abs_sup=min_abs_sup
        self.min_rel_sup=min_rel_sup
        self.attributes=attributes

        
        self.transactionsTotal=None         # ukupno transakcija
        self.supportsCalculated=False       # izracunati supporti
        self.collectionsClosed=False        # zatvorene kolekcije
        self.addedValuesCalculated=False    # izracunate dodane vrijednosti
        self.maximalsFlagged=False          # oznacene maksimalne
        self.maximals=None                  # izracunate maksimalne
        self.treeStrat=None                 # koja strategija je koristena
        self.treeBuilt=False                # izgradjeno stablo
        self.IRPcalculated=False            # izracunat IRP
        self.totalIRP=None                  # ukupni IRP

        #added value flagovi i izracunatost
        self.totalAddedValueCalculated=False
        self.totalBoundAddedValueCalculated=False
        self.totalAddedValue=None
        self.totalAddedValueNoSingletons=None
        self.totalBoundAddedValue=None
        self.totalBoundAddedValueNoSingletons=None

    #u koliko razina su pohranjenje
    def get_layers_total(self):
        return len(self.layers)
    layers_total=property(get_layers_total)

    #dohvati cijelu razinu
    def get_layer(self, layer):
        if layer<self.layers_total: return self.layers(layer)
        else: return None

    #dodaj kolekciju
    #kolekcija ide na onu razinu koja odgovara broju elemenata-1
    def add(self, collection):
        elTot=collection.elements_total
        if (elTot>=self.layers_total):
            while((self.layers_total!=elTot)): self.layers.append([])
        for old_coll in self.layers[elTot-1]:
            if (old_coll.elements==collection.elements):
                raise ValueError('Vec postoji ta kolekcija!!')
        self.layers[elTot-1].append(collection)

    #koje sve elemente ima ta kolekcija
    def get_collection_attributes(self, collection):
        atributi=[]
        j=0
        for i in collection.elements:
            if (i==1): atributi.append(self.attributes[j])
            j+=1
        return atributi

    
    def __str__(self):
        output=""
        output+="=============================================================\n"
        output+="Collections:"
        if (self.supportsCalculated): output+="           ....  support"
        if (self.addedValuesCalculated): output+="    .... add.val."
        if (self.treeBuilt):output+=" ..... tree status"
        if (self.IRPcalculated):output+="      ..... rel.inf."
        output+="\n-----------------------------------------------------------------------------------------\n"
        for i in range(self.layers_total):
            for j in range(len(self.layers[i])):
                output+="  "+str(self.layers[i][j])
                output+="\t\t      ....     "+str(self.layers[i][j].support)
                output+="      ....     "+str(self.layers[i][j].added_value)
                if (self.treeBuilt):
                    if (self.layers[i][j].boundness==BOUND): output+="     ....     BOUND"
                    elif (self.layers[i][j].boundness==UNKNOWN):  output+="     ....    UNKNOWN"
                    elif (self.layers[i][j].boundness==DISCARDED):  output+="     ....     DISCARDED"
                    if (self.IRPcalculated): output+="\t      ....     "+str(self.layers[i][j].IRP)
                output+="\n"
                
            output+="    * * * * * * \n"
        output+="=============================================================\n"
        return output
        
        
# objekt koji stvara LCS-ove
class CollectionSetFactory(object):

    input_datasets_path="\\resources\\input_datasets"
    stored_lcs_path="\\resources\\stored_lcs"

    @staticmethod
    def getTime():
        currentTime=time.clock()
        return "%.2f" % (currentTime - startTime)
        
    # stvara od datoteke transaction set
    @staticmethod
    def loadTransactionSetFromFile(inputFileName, store=True):
        tcs=None
        if inputFileName.lower().endswith(".tcs"):
            import pickle
            f = open(inputFileName, "r")
            p = pickle.Unpickler(f)
            tcs = p.load()
        elif inputFileName.lower().endswith(".tab"):
            try:
                f = open(inputFileName, 'r')
            except IOError:
                f=open("resources\\input_datasets\\"+inputFileName, 'r')     
            atributi=str.split(f.readline()[:-1],"\t")
            tcs=TransactionSet([], atributi)
            f.readline()
            f.readline()
            for line in f:
                values=str.split(line[:-1], "\t")
                if (values[0]!=''):
                    values_int=[int(v) for v in values]
                    tcs.transactions.append(Transaction(values_int))
            
            #import orange
            #orangeData=orange.ExampleTable(inputFileName)                        #privremeno (i sporo) rjesenje; zamijeniti vlastitim parserom
            #atributi=[]
            #for at in orangeData.domain: atributi.append(at.name)
            #atributi.pop(-1)
            #tcs=TransactionSet([], atributi)
            #for redak in orangeData:
                #int_redak=[int(x) for x in redak.native(0)]
                #int_redak.pop(-1)
                #tcs.transactions.append(Transaction(int_redak))
        if (store):
            import os
            if os.path.split(inputFileName)[1] not in os.listdir((os.getcwd()+CollectionSetFactory.input_datasets_path)):
                import shutil
                shutil.copy(inputFileName, os.getcwd()+CollectionSetFactory.input_datasets_path+"\\"+os.path.split(inputFileName)[1])
        return tcs

    
    @staticmethod
    def saveTransactionSetToFile(tcs, outputFileName):
        if outputFileName.lower().endswith(".tcs")==False:
            outputFileName+=".tcs"
        import pickle
        f = open(outputFileName, "w")
        p = pickle.Pickler(f)
        p.dump(tcs)
        f.close()    

    @staticmethod
    def loadLayeredCollectionSetFromFile(inputFileName):
        lcs=None
        if inputFileName.lower().endswith(".lcs"):
            import pickle
            f = open(inputFileName, "r")
            p = pickle.Unpickler(f)
            lcs = p.load()
        return lcs

    @staticmethod
    def saveLayeredCollectionSetToFile(lcs, outputFileName):
        if outputFileName.lower().endswith(".lcs")==False:
            outputFileName+=".lcs"
        import pickle
        f = open(outputFileName, "w")
        p = pickle.Pickler(f)
        p.dump(lcs)
        f.close()    

            
    """
    def generateLayeredCollectionSet():
        pass
    """

    
    @staticmethod
    def __constructLcsFileName(inputFileName, min_abs_sup):
        import os
        inputFileName=os.path.split(inputFileName)[1]
        if inputFileName.lower().endswith(".lcs")==False:
            outputFileName=inputFileName[:inputFileName.rindex(".")]
            outputFileName=os.getcwd()+CollectionSetFactory.stored_lcs_path+"\\"+outputFileName+"_sup_"+str(min_abs_sup)+".lcs"
        else:
            outputFileName=os.getcwd()+CollectionSetFactory.stored_lcs_path+"\\"+outputFileName
        return outputFileName

    #ako vec postoji LCS (sto provjerava trazeci odgovarajuci fajl nejm) onda vraca TRUE
    @staticmethod
    def alreadyInitialized(inputFileName, min_abs_sup=None):
        import os
        if inputFileName.lower().endswith(".lcs")==True:
            if os.path.split(inputFileName)[1] in (os.getcwd()+CollectionSetFactory.stored_lcs_path): return True
        elif inputFileName.lower().endswith(".tab")==True:
            lcsFileName=os.path.split(inputFileName)[1]
            lcsFileName=lcsFileName[:lcsFileName.rindex(".")]
            lcsFileName+="_sup_"+str(min_abs_sup)+".lcs"
            #print lcsFileName
            if lcsFileName in os.listdir(os.getcwd()+CollectionSetFactory.stored_lcs_path): return True
        return False

    #inicijalizira LCS sa apriori algoritmom
    @staticmethod
    def initializeLcsWithApriori(inputFileName=None, inputTcs=None, inputLcs=None, min_abs_sup=None, min_rel_sup=None, calculateAddedValues=True, closeCollections=True, keepSingletons=True, findMaximals=True,  buildTree=True, treeStrat=BOTTOM_UP, storeTcs=False, storeLcs=True):
        ##if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
        if (DEBUG):
            print "Initializing LCS...."
            if inputFileName is not None: print "InputFileName:", inputFileName
            if min_abs_sup is not None: print "Min. abs. support:", min_abs_sup

        #ucitava transakcije (bilo iz danog parametra ili iz datoteke)
        if (inputTcs is not None): __tcs=inputTcs
        elif (inputFileName is not None): __tcs=CollectionSetFactory.loadTransactionSetFromFile(inputFileName)
        else: raise Exception("Cannot load input data.")

        #podesi relativni i/ili apsolutni support
        __min_abs_sup, __min_rel_sup=CollectionSetFactory.__fix_rel_abs(min_rel_sup,min_abs_sup,len(__tcs.transactions))

        #postoji LCS.. ucitaj ga i napravi tree ako treba
        if ((inputFileName is not None) and (CollectionSetFactory.alreadyInitialized(inputFileName, __min_abs_sup)==True)):
            __lcs=CollectionSetFactory.loadLayeredCollectionSetFromFile(CollectionSetFactory.__constructLcsFileName(inputFileName, __min_abs_sup))
            if (buildTree): CollectionSetFactory.build_tree(__lcs, strategy=treeStrat, criteria=BY_SUPPORT, reset_tree=True, root=None)
            ##if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
            if (DEBUG):
                print "This LCS was already initialized! Returning...."

        # ne postoji LCS.. moramo ga napraviti
        # pozivam internu f-ju find_all_frequent_itemsets koja je zapravo apriori
        # usput poziva funkcije koje racunaju razne vesele stvari
        else:
            __lcs=LayeredCollectionSet([],__min_abs_sup, __min_rel_sup, __tcs.attributes )
            CollectionSetFactory.__find_all_frequent_itemsets(__lcs, __tcs, __min_abs_sup)
            __lcs.transactionsTotal=len(__tcs.transactions)
            if (closeCollections): CollectionSetFactory.close_collections(__lcs, keepSingletons)
            if (calculateAddedValues): CollectionSetFactory.calculate_added_values(__lcs)
            if (findMaximals): CollectionSetFactory.flag_maximal_collections(__lcs)
            if (buildTree): CollectionSetFactory.build_tree(__lcs, strategy=treeStrat, criteria=BY_SUPPORT, reset_tree=True, root=None)
            if (calculateAddedValues): CollectionSetFactory.calculate_total_bound_added_values(__lcs)
            if (storeLcs==True and inputFileName is not None): CollectionSetFactory.saveLayeredCollectionSetToFile(__lcs, CollectionSetFactory.__constructLcsFileName(inputFileName, __min_abs_sup))
        ##if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
        return __lcs
        
        
    @staticmethod
    def __fix_rel_abs(min_rel_sup,min_abs_sup,transactionsCount):
        ##if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
        if (DEBUG):
            print "Fixing supports...."
        if (min_rel_sup is None) and (min_abs_sup is None):
            min_rel_sup=0.1                     
            min_abs_sup=0.1*transactionsCount
        elif (min_rel_sup is None or transactionsCount is None):
            min_rel_sup=min_abs_sup*1.0/transactionsCount
        else:
            min_abs_sup=int(min_rel_sup*transactionsCount)
        return min_abs_sup,min_rel_sup

    @staticmethod  
    def __find_all_frequent_itemsets(lcs, tcs, min_abs_sup):
        #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
        if (DEBUG):
            print "Finding all frequent itemsets supports...."
        CollectionSetFactory.__find_frequent_singleton_itemsets(lcs, tcs, min_abs_sup)
        CollectionSetFactory.__apriori(lcs, 0)
        current_level=1
        while (lcs.layers_total-1==current_level):
            #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
            if (DEBUG):
                print "Next task: calculating level supports for level....", current_level
            CollectionSetFactory.calculate_supports(lcs, tcs, level=current_level)
            #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
            if (DEBUG):
                print "Next task: pruning supports for level....", current_level
            CollectionSetFactory.prune(lcs, min_abs_sup, level=current_level)
            #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
            if (DEBUG):
                print "Pruned! Level", current_level,"now has", str(len(lcs.layers[current_level])), "collections!"
                if (len(lcs.layers[current_level])!=0):
                    for kola in lcs.layers[current_level]: print "_____", kola
            #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
            if (DEBUG):
                print "Next task: running apriori supports for level....", current_level
            CollectionSetFactory.__apriori(lcs, level=current_level)
            current_level+=1
        #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
        if (DEBUG):
            print "Frequent itemsets found."
            
        

    @staticmethod
    def __find_frequent_singleton_itemsets(lcs, tcs, min_abs_sup):
        #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
        if (DEBUG):
            print "Finding singleton itemsets...."
        for i in range(len(tcs.attributes)):
            elements=[0]*len(tcs.attributes)
            elements[i]=1
            new_collection=Collection(elements, support=0)
            lcs.add(new_collection)
        CollectionSetFactory.calculate_supports(lcs, tcs, 0)
        CollectionSetFactory.prune(lcs, min_abs_sup, 0)
        lcs.supportsCalculated=True
        #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
        if (DEBUG):
            print "Singleton itemsets found.... level 0 now has", len(lcs.layers[0]), "elements"
            for kola in lcs.layers[0]:
                print "_____", kola

    @staticmethod
    def get_all_minus_one_subsets(collection):
        indexes=[i for i in range(len(collection.elements)) if collection.elements[i]==1]
        #print indexes
        result=[]
        for i in indexes:
            new_collection=Collection(collection.elements)
            new_collection.elements[i]=0
            result.append(new_collection)
        return result
            
            
    @staticmethod
    def __apriori(lcs, level):
        has_levels=lcs.layers_total
        #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
        if (DEBUG):
            print "LCS has", lcs.layers_total, "layers, entering APRIORI.... constructing level", level+1
        current_level_elements=[]
        for collection in lcs.layers[level]:
            current_level_elements.append(collection.elements)
        ##if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
        #if (DEBUG):
            #print "Weird place where it hangs."
            #for kola in lcs.layers[level]: print "====", kola
        
        for kolekcija_i in lcs.layers[level][:-1]:
            indeks_kolekcije_i=lcs.layers[level].index(kolekcija_i)
            #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
            #if (DEBUG):
                #print "Picking out collection", kolekcija_i, "koja je na indeksu",indeks_kolekcije_i
            ##if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
            #if (DEBUG):
                #print "Stvorio sam novitet!", novitet
                #for kola in novitet: print ":::::", kola
            for kolekcija_j in lcs.layers[level][(indeks_kolekcije_i+1):]:
                #print kolekcija_i, kolekcija_j
                #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
                #if (DEBUG):
                    #print "Comparing collections", kolekcija_i, "and", kolekcija_j
                if CollectionSetFactory.__are_apriori_joinable(kolekcija_i, kolekcija_j):
                    #print kolekcija_i, kolekcija_j, kolekcija_i.AND(kolekcija_j), kolekcija_i.OR(kolekcija_j), kolekcija_i.XOR(kolekcija_j),"+++++++"
                    nova_kolekcija=kolekcija_i.OR(kolekcija_j)
                    podkolekcije=CollectionSetFactory.get_all_minus_one_subsets(nova_kolekcija)
                    #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
                    #if (DEBUG):
                        #print "They are joinable! Creating a new joined collection", nova_kolekcija, "and minus-one subcollections"
                    all_frequent_subsets=True
                    for podkolekcija in podkolekcije:
                        if podkolekcija.elements not in current_level_elements:
                            all_frequent_subsets=False
                            break
                    if (all_frequent_subsets):
                        #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
                        if (DEBUG):
                            print "Collection", nova_kolekcija,"is added to level", level+1
                        lcs.add(nova_kolekcija)
                    else:
                        #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
                        if (DEBUG):
                            print "Collection", nova_kolekcija,"is discarded!"
        #if (TIMED): print "Timestamp:" + CollectionSetFactory.getTime(),
        if (DEBUG):
            now_has_levels=lcs.layers_total
            if now_has_levels==has_levels:
                print "Exiting apriori, no new layers added."
            else:
                print "LCS now has", lcs.layers_total, "layers, exiting APRIORI....","currently level", level+1, "now has", str(len(lcs.layers[level+1])), "collections"
                for kola in lcs.layers[level+1]: print "_____", kola
                    
       

    #dvije kolekcije su joinable ako imaju isti broj stavaka i ako se poklapaju u svim stavkama osim zadnje     
    @staticmethod
    def __are_apriori_joinable(a, b):
        #print a,b
        #print a.attributes_total, b.attributes_total
        #print a.elements_total, b.elements_total
        #print a.elements, b.elements
        if (a.attributes_total!=b.attributes_total or a.elements_total!=b.elements_total):
            #print 1
            return False
        indeks_razlike=0
        #print "Nije nije dobro"
        #time.sleep(2)
        #print "Fino bijase spavati"
        
        
        while (a.elements[indeks_razlike]==b.elements[indeks_razlike]):
            indeks_razlike+=1
            if ((indeks_razlike+1)>a.attributes_total):
                #print 2
                return False

           
        nulavac, kolega = (a,b) if a.elements[indeks_razlike]==0 else (b,a)
       
                
        #onaj u kojem je nadjena jedinica mora imati sve nule do kraja 
        if (sum(kolega.elements[(indeks_razlike+1):])!=0): return False

        #onaj s nulom mora imati tocno jednu jedinicu do kraja 
        if (sum(nulavac.elements[(indeks_razlike+1):])!=1): return False
       
        
        return True
        
        
    @staticmethod
    def prune(lcs, min_abs_sup, level=None):
        if level is None:
            for i in range(lcs.layers_total-1,-1,-1): CollectionSetFactory.prune(lcs, min_abs_sup, i)
        else:
            for i in range(len(lcs.layers[level])-1,-1,-1):
                if (lcs.layers[level][i].support<min_abs_sup): lcs.layers[level].remove(lcs.layers[level][i]) 

    @staticmethod
    def calculate_supports(lcs, tcs, level=None):
        if (level is None):
            for layer in lcs.layers:
                for kolekcija in layer:
                    if kolekcija.support is None: kolekcija.support=0
                    for redak in tcs.transactions:
                        if kolekcija.is_subset_of(redak):
                           kolekcija.support+=1 
                    
        else:
            for kolekcija in lcs.layers[level]:
                if kolekcija.support is None: kolekcija.support=0
                for redak in tcs.transactions:
                    if kolekcija.is_subset_of(redak):
                       kolekcija.support+=1
                    

    @staticmethod
    def calculate_added_values(lcs):
        trenutna_razina=lcs.layers_total-1 #krecem od vrsne razine
        for kolekcija in lcs.layers[trenutna_razina]: kolekcija.added_value=kolekcija.support
        trenutna_razina-=1
        while (trenutna_razina!=-1):
            ogledna_razina=trenutna_razina+1
            for kolekcija in lcs.layers[trenutna_razina]:
                kolekcija.added_value=kolekcija.support
                max_support_nadseta=0
                ogledna_razina_backup=ogledna_razina
                while (ogledna_razina<=(lcs.layers_total-1)):
                    for nadkolekcija in lcs.layers[ogledna_razina]:
                        if (kolekcija.is_subset_of(nadkolekcija)):
                             if (nadkolekcija.support>max_support_nadseta):
                                max_support_nadseta=nadkolekcija.support
                    ogledna_razina+=1
                kolekcija.added_value-=max_support_nadseta
                ogledna_razina=ogledna_razina_backup         #moram se opet vratiti za jednu razinu iznad iduce gledane kolekcije
            trenutna_razina-=1
        razina=lcs.layers_total-1
        lcs.totalAddedValue=0
        lcs.totalAddedValueNoSingletons=0
        while razina!=-1:
            for kolekcija in lcs.layers[razina]:
                if kolekcija.added_value is not None:
                    lcs.totalAddedValue+=kolekcija.added_value
                    if (razina!=0): lcs.totalAddedValueNoSingletons+=kolekcija.added_value
                    print "*******-----*******"
                    print kolekcija, kolekcija.added_value
            razina-=1
        lcs.totalAddedValueCalculated=True
        lcs.addedValuesCalculated=True

    @staticmethod
    def calculate_total_bound_added_values(lcs):
        razina=lcs.layers_total-1
        lcs.totalBoundAddedValue=0
        lcs.totalBoundAddedValueNoSingletons=0
        while razina!=-1:
            for kolekcija in lcs.layers[razina]:
                if kolekcija.added_value is not None and (kolekcija.boundness==BOUND or kolekcija.get_elements_total()==1):
                    lcs.totalBoundAddedValue+=kolekcija.added_value
                    if (razina!=0): lcs.totalBoundAddedValueNoSingletons+=kolekcija.added_value
                    print "*******-----*******"
                    print kolekcija, kolekcija.added_value
                
            razina-=1
        lcs.totalBoundAddedValueCalculated=True
        print "+++++++++++++++"
        print lcs.totalAddedValue
        print lcs.totalAddedValueNoSingletons
        print lcs.totalBoundAddedValue
        print lcs.totalBoundAddedValueNoSingletons
        
                

    @staticmethod
    def close_collections(lcs, keep_singletons):
        donja_razina=0 if keep_singletons else -1
        trenutna_razina=lcs.layers_total-1
        while (trenutna_razina!=0):
            for glavna_kolekcija in lcs.layers[trenutna_razina]:
                promatrana_razina=trenutna_razina-1
                while (promatrana_razina!=donja_razina):
                    for indeks in range(len(lcs.layers[promatrana_razina])-1, -1, -1):
                        if (lcs.layers[promatrana_razina][indeks].support==glavna_kolekcija.support):
                            if (lcs.layers[promatrana_razina][indeks].is_subset_of(glavna_kolekcija)):
                                lcs.layers[promatrana_razina].remove(lcs.layers[promatrana_razina][indeks])                        
                    promatrana_razina-=1
            trenutna_razina-=1
        lcs.collectionsClosed=True

    @staticmethod
    def flag_maximal_collections(lcs):
        lcs.maximals=[]
        trenutna_razina=lcs.layers_total-1
        while (trenutna_razina!=-1):
            for glavna_kolekcija in lcs.layers[trenutna_razina]:
                if (glavna_kolekcija.isMaximal==False): continue
                else:
                    glavna_kolekcija.isMaximal=True
                    lcs.maximals.append(glavna_kolekcija)
                promatrana_razina=trenutna_razina-1
                while (promatrana_razina!=-1):
                    for donja_kolekcija in lcs.layers[promatrana_razina]:
                        if donja_kolekcija.is_subset_of(glavna_kolekcija): donja_kolekcija.isMaximal=False
                    promatrana_razina-=1
            trenutna_razina-=1
        lcs.maximalsFlagged=True

    @staticmethod
    def __calcIRP(kolekcija, parent=None):
        elemenata=kolekcija.get_elements_total()
        if elemenata!=1:
            if parent is not None: kolekcija.IRP=1.*elemenata*(elemenata-1)*(kolekcija.support-parent.support)/2
            else: kolekcija.IRP=1.*elemenata*(elemenata-1)*kolekcija.support/2
        else:
            IRP=0.0
        if (len(kolekcija.links)!=0):   
            for dite in kolekcija.links: CollectionSetFactory.__calcIRP(dite.destination, kolekcija)
        
        

    @staticmethod
    def calculate_IRP(lcs):
        if (lcs.treeBuilt==False): return
        razina=lcs.layers_total-1
        while razina!=0:
            for kolekcija in lcs.layers[razina]:
                #print "A mozda sam i ovdi jeee!", kolekcija
                if kolekcija.boundness==BOUND and kolekcija.IRP is None:
                    #print "Eto me ovdi jeee!", kolekcija
                    CollectionSetFactory.__calcIRP(kolekcija)
                    #if (len(kolekcija.links)!=0):
                       # for dite in kolekcija.links: CollectionSetFactory.__calcIRP(dite.destination, kolekcija)
            razina-=1
        razina=lcs.layers_total-1
        lcs.totalIRP=0
        while razina!=0:
            for kolekcija in lcs.layers[razina]:
                if kolekcija.IRP is not None: lcs.totalIRP+=kolekcija.IRP
            razina-=1
        lcs.IRPcalculated=True
      
        
                
    @staticmethod
    def sort_layers(lcs, how=ALPHABETICALLY, reverse=True, just_layer=None):
        if (just_layer is None):
            for layer in lcs.layers:
                CollectionSetFactory.sort_layers(lcs, how, reverse, just_layer=lcs.layers.index(layer))
        else:
            layer=lcs.layers[just_layer]
            if (how==ALPHABETICALLY): layer.sort(reverse=reverse, key=lambda x:str(x))
            elif ( (how==BY_SUPPORT) and (lcs.supportsCalculated)): layer.sort(reverse=reverse, key=lambda x:x.support)

            elif ( (how==BY_ADDED_VALUE) and (lcs.addedValuesCalculated)): layer.sort(reverse=reverse, key=lambda x:x.added_value)
            elif ( (how==BY_BOUNDNESS) and (lcs.addedValuesCalculated)): layer.sort(key=lambda x:x.boundness)

    @staticmethod
    def build_tree(lcs, strategy=BOTTOM_UP, criteria=BY_SUPPORT, reset_tree=True, root=None, calculateIRP=True):
        print "Pozvan build tree, strategija:", strategy, " root:", root
        if (reset_tree):
            lcs.treeBuilt=False
            lcs.IRPcalculated=False
            lcs.totalIRP=None
            for layer in lcs.layers:
                for collection in layer:
                    collection.boundness=UNKNOWN
                    collection.IRP=None
                    collection.links=[]
       
        if (strategy==BOTTOM_UP):
            #print "Strategy is bottom up!"
            CollectionSetFactory.__build_bottom_up_tree(lcs,criteria)
        elif (strategy==TOP_DOWN):
            #print "Strategy is top down!"
            CollectionSetFactory.__build_top_down_tree(lcs, criteria)
        elif (strategy==BOTTOM_UP_CONSTRAINED):
            #print "Strategy is bottom up constrained!"
            CollectionSetFactory.__build_bottom_up_tree(lcs,criteria, root)
        elif (strategy==TOP_DOWN_CONSTRAINED):
            #print "Strategy is top down constrained!"
            CollectionSetFactory.__build_top_down_tree(lcs,criteria, root)
        lcs.treeStrat=strategy
        for layer in lcs.layers:
                for collection in layer:
                    if collection.boundness==BOUND:
                        lcs.treeBuilt=True
                        break
                if lcs.treeBuilt==True: break
        if calculateIRP: CollectionSetFactory.calculate_IRP(lcs)
        CollectionSetFactory.calculate_total_bound_added_values(lcs)
        #CollectionSetFactory.print_tree(lcs)


    @staticmethod

    # uzima LCS i gradi top_down tree
    
    def __build_top_down_tree(lcs, criteria=BY_SUPPORT, root=None):
        from copy import deepcopy
        print "Tu sam!!!!"
        if root is not None: print root

        #kreni od zadnje (predzadnje?) razine
        trenutna_razina=lcs.layers_total-1

        #sortiraj razine abecedno
        CollectionSetFactory.sort_layers(lcs, how=ALPHABETICALLY)
                                    #for kola in lcs.layers[0]: print kola,
                                    #print
        CollectionSetFactory.sort_layers(lcs, how=criteria)
                                    #for kola in lcs.layers[0]: print kola,
                                    #print

        #idem od najvece razine prema najmanjoj
        
        while (trenutna_razina!=0):

            # ako se radi o razini koja nije najveca (jer to valjda znaci da je tek poceo), presortiraj razinu po povezanosti cvorova
            # ako dobro gledam, prvo ce biti povezani, pa oni sa nepoznatim statusom (koji valjda jos nisu razmatrani), pa odbaceni
            if (trenutna_razina!=lcs.layers_total-1): CollectionSetFactory.sort_layers(lcs, just_layer=trenutna_razina, how=BY_BOUNDNESS)

            # proseci se po kolekcijama trenutne razine
            # varijabla "kolekcija" je ona koju trenutno gledam
            for kolekcija in lcs.layers[trenutna_razina]:

                # ako postoji root kolekcija, a kolekcija nije njen podskup, baci ju van, ovo sve dolje se onda ne izvodi
                if (root is not None) and (kolekcija.is_subset_of(root)==False): kolekcija.boundness=DISCARDED
                
                if kolekcija.boundness!=DISCARDED:                #ako je DISCARDED ne gledam ga uopce
                    for i in range(lcs.layers[trenutna_razina].index(kolekcija)+1,len(lcs.layers[trenutna_razina])):   # kolekcija "rezervira" sve svoje clanove 
                        if (kolekcija.AND(lcs.layers[trenutna_razina][i]).elements_total!=0):                          # zato ubijam kolekcije na istoj razini koje s njom dijele clanove
                            lcs.layers[trenutna_razina][i].boundness=DISCARDED

                    # idem sad od jedne razine nize pa sve do dna        
                    ogledna_razina=trenutna_razina-1
                    kolekcija_copy=deepcopy(kolekcija)   #kopiram originalnu kolekciju da zapamtim
                    kandidati=[]
                    while (ogledna_razina!=-1):         #idem od jedne nize razine do dna i povezujem
                        for donja_kolekcija in lcs.layers[ogledna_razina]:
                            if (donja_kolekcija.boundness==UNKNOWN):
                                if (donja_kolekcija.is_subset_of(kolekcija_copy)):   # ako je manja kolekcija podskup, MOZDA ce se povezati
                                    kandidati.append(donja_kolekcija)
                                    kolekcija_copy=kolekcija_copy.XOR(donja_kolekcija)   # izbaci iz originalne kolekcije elemente koje pokriva ovaj kandidat
                                elif (((donja_kolekcija.is_subset_of(kolekcija))==False) and (donja_kolekcija.AND(kolekcija)).elements_total!=0):      #kolekcija ima zajednicke elemente sa vrsnom, ali nije podskup.. treba ju discardati
                                    donja_kolekcija.boundness=DISCARDED
                        ogledna_razina-=1
                    if (kolekcija_copy.elements_total==0):   # uspio sam pokupiti sve elemente iz originalne kolekcije
                        kolekcija.boundness=BOUND            # kolekcija sada postaje dio drveta, kao i svi kandidati iz donjih razina
                        for kandidat in kandidati:
                            kandidat.boundness=BOUND
                            kolekcija.add_link(CollectionLink(type='child', destination=kandidat))   # spajam originalnu kolekciju sa svom njenom djecom
                    else: kolekcija.boundness=DISCARDED
            trenutna_razina-=1

        #moguce je da je na prvoj razini ostalo UNKNOWN kolekcija, sada to popravljam
        for kolekcija in lcs.layers[0]: 
            if (kolekcija.boundness==UNKNOWN): kolekcija.boundness=DISCARDED

        

    @staticmethod
    def __build_bottom_up_tree(lcs,criteria, root=None):
        from copy import deepcopy
        CollectionSetFactory.sort_layers(lcs, how=ALPHABETICALLY)
        #for kola in lcs.layers[0]: print kola, str(kola), kola.support, "...",
        #print
        CollectionSetFactory.sort_layers(lcs, how=criteria)
        #for kola in lcs.layers[0]: print kola, str(kola), kola.support,  "...",
        #print
        trenutna_razina=1                                           #singletone ne diram
        while (trenutna_razina!=(lcs.layers_total)):                #idem od druge razine do vrha
            for kolekcija in lcs.layers[trenutna_razina]:           #kolekcija po kolekcija, pocevsi od one sa max_supportom
                kandidati=[]
                if (root is not None):
                    if (kolekcija.is_subset_of(root)==False):
                        kolekcija.boundness=DISCARDED
                        continue
                ogledna_razina=trenutna_razina-1
                kolekcija_copy=deepcopy(kolekcija)
                while (ogledna_razina!=-1):                         #gledam donje razine, sve do dna
                    for donja_kolekcija in lcs.layers[ogledna_razina]:
                        if (donja_kolekcija.boundness==UNKNOWN):
                            if (donja_kolekcija.is_subset_of(kolekcija_copy)):
                                kandidati.append(donja_kolekcija)
                                kolekcija_copy=kolekcija_copy.XOR(donja_kolekcija)
                    ogledna_razina-=1
                if (kolekcija_copy.elements_total!=0): kolekcija.boundness=DISCARDED
                else:
                    for kandidat in kandidati:
                        kandidat.boundness=BOUND
                        kolekcija.add_link(CollectionLink(type='child', destination=kandidat))
            trenutna_razina+=1
                
        # svaki cvor na kraju algoritma treba biti ili BOUND ili DISCARDED
        # posto su vrsni cvorovi mozda ostali UNKNOWN sada to moram popraviti
        for i in range(lcs.layers_total):
            for kolekcija in lcs.layers[i]:
                if kolekcija.boundness==UNKNOWN:
                    if i!=0: kolekcija.boundness=BOUND
                    else:kolekcija.boundness=DISCARDED

    @staticmethod    
    def print_tree(lcs, showDiscards=False):
        print "===================================="
        print "Printing tree:"
        razina_broj=1
        print "===================================="
        for layer in lcs.layers:
            print "------------"
            print "Layer ", lcs.layers.index(layer)
            print "------------"
            for collection in layer:
                if (collection.boundness==DISCARDED and showDiscards==True):
                    print "Collection", collection, "is discarded from the tree."
                elif (collection.boundness==UNKNOWN):
                    print "Collection", collection, "has unknown status (error?)."
                elif (collection.boundness==BOUND):
                    print "Collection", collection, "is a part of the tree."
                    if len(collection.links)>0:
                        print "Children:"
                        for veza in collection.links:
                            print "___", veza.destination
                elif (collection.boundness!=DISCARDED): print "ERROR! ERROR! ERROR! ERROR! ERROR! ERROR! ERROR!"
        print "===================================="
            
                    

    
    
#reprezentacija jednog retka/transakcije
class Transaction():
    def __init__(self, elements=None, attributes_total=None):           #elementi je vektor elemenata, attributes_total je ukupni broj atributa (valjda za inic. prazne transakcije
        if ((elements is not None) and (elements is not [])):
            self.elements=elements[:]
        elif (attributes_total is not None and attributes_total>0):
            self.elements=[0]*attributes_total
        else: raise Exception("Bad initializer arguments...")

    #suma svih elemenata  (posto su jedinice onda broj elemenata)
    def get_elements_total(self):
        return sum(self.elements)

    elements_total=property(get_elements_total)

    #broj atributa
    def get_attributes_total(self):
        return len(self.elements)

    attributes_total=property(get_attributes_total)    

    
    def XOR(self,transaction):
        return Transaction([x^y for x,y in zip(self.elements, transaction.elements)])
        

    def AND(self,transaction):
        return Transaction([x&y for x,y in zip(self.elements, transaction.elements)])
        
    def OR(self,transaction):
        return Transaction([x|y for x,y in zip(self.elements, transaction.elements)])
        

    def __str__(self):
        text=""
        if self.attributes_total<=26: return "".join([str(chr(65+i)) for i in range(len(self.elements)) if self.elements[i]==1])        
        else: return "".join(["A"+str(i)+"," for i in range(len(self.elements)) if self.elements[i]==1])[:-1]
           
    """
    def string_repr(self, atributi=None, letters=True):
        text=""
        for i in range(len(self.__elements)):
            if (self.__elements[i]!=0):
                if ((atributi is not None) and len(atributi)==len(self.__elements)):
                    text+=atributi[i]
                    if (i!=(len(self.__elements)-1)): text+=","
                else: text+=str(chr(65+i))
        return text
    """

    def is_subset_of(self, superset):
        if (len(self.elements)!=len(superset.elements)):
            #print len(self.elements)
            #print len(superset.elements)
            return False
        #superset_elementi_int = self.elementi_2_int(superset.elementi)
        and_proba = self.AND(superset)
        if (sum(and_proba.elements)!=0) and (sum(and_proba.XOR(self).elements)==0): return True
        return False

#kolekcija je transakcija sa dodatnim opisnim elementima
         # support - koliko puta se pojavljuje u ulaznom skupu
         # added_value - koliko doprinosi
         # links - s kojim je kolekcijama povezana u stablu (za dendrogram)
         # boundness - da li je povezana ili ne (povezana, izbacena, nepoznato)
         # isMaximal - da li se radi o maksimalnoj kolekciji
         # IRP - mjera
         
class Collection(Transaction):
    def __init__(self, elements=None, attributes_total=None, support=None, added_value=None):
        Transaction.__init__(self, elements, attributes_total)
        self.support=support
        self.added_value=added_value
        self.links=None
        self.boundness=UNKNOWN
        self.isMaximal=None
        self.IRP=None

    #dodajem CollectionLink objekt u vektor veza
    def add_link(self, link):
        if self.links is None: self.links=[]
        self.links.append(link)
    
    def XOR(self,transaction):
        return Collection([x^y for x,y in zip(self.elements, transaction.elements)])
        

    def AND(self,transaction):
        return Collection([x&y for x,y in zip(self.elements, transaction.elements)])
        
    def OR(self,transaction):
        return Collection([x|y for x,y in zip(self.elements, transaction.elements)])        



#poveznica dvije kolekcije, moze imati tip i broj
class CollectionLink():

    #type
    #measure
    #source
    #destination

    def __init__(self, type=None, measure=None, source=None, destination=None):
        self.type=type
        self.measure=measure
        self.source=source
        self.destination=destination



def print_transaction(t):
    print "=========================="
    #print "Elementi:", t.get_elements()
    #print "Elementi_int:", t.get_elements_int()
    print "Elementi:", t.elements
    print "Ukupno elemenata:", t.elements_total
    print "Ukupno atributa:", t.attributes_total
    print "=========================="

def print_collection(c):
    print_transaction(c)
    print "Podrska:", c.support
    print "Dodana vrijednost:", c.added_value
    print "Veze:", c.links
    print "Maksimalac? ", c.isMaximal
    print "Boundness:", c.boundness
    print "=========================="


def test_transaction():
    t1=Transaction([1,0,0,1,0])
    print_transaction(t1)
    t1.set_elements([0,0,1,0,0])
    print_transaction(t1)
    print_transaction(t1)
    print_transaction(t1)
    t2=Transaction([1,1,0,0,0,1,1,0,1,1])
    print "Parovi se moraju podudarati:"
    print t1.is_subset_of(t2), "TRUE"
    print t2.is_subset_of(t1), "FALSE"
    t3=Transaction([1,1,0,1])
    print t3.is_subset_of(t1), "FALSE"
    print t4.is_subset_of(t1), "FALSE"
    print_transaction(t4)
    print_transaction(t1)
    print_transaction(t4.XOR(t1))
    print_transaction(t4.AND(t1))
    print_transaction(t4.OR(t1))
    print t1
    print t2
    
    
    
    
    

def test_collection():
    c1=Collection([1,0,0,1,0])
    print_collection(c1)
    c1.add_link("Baba")
    c1.support=5
    c1.added_value=2
    c1.boundness=BOUND
    c1.isMaximal=True
    print_collection(c1)
    print_collection(c1)
    print c1
    
def test_csf():

    
    #tcs=CollectionSetFactory.loadTransactionSetFromFile(inputFileName="Primjer1.tab")
    import time
    print 
    start=time.clock()
    print " Dvadeset Botm up"
    lcs1=CollectionSetFactory.initializeLcsWithApriori(inputFileName="resources\\input_datasets\\Computer_shop.tab", min_abs_sup=151, treeStrat=TOP_DOWN)
    print(lcs1)
    CollectionSetFactory.print_tree(lcs1)
    
   

    #korijen=lcs1.layers[3][0]
   # CollectionSetFactory.build_tree(lcs1,strategy=TOP_DOWN_CONSTRAINED, root=korijen)
    #CollectionSetFactory.print_tree(lcs1)
    
  
   
    
    
    #lcs2=CollectionSetFactory.initializeLcsWithApriori(inputFileName="Primjer1.tab", min_abs_sup=2, treeStrat=BOTTOM_UP)
    #lcs3=CollectionSetFactory.initializeLcsWithApriori(inputFileName="Primjer1.tab", min_abs_sup=1, treeStrat=BOTTOM_UP)
    #lcs4=CollectionSetFactory.initializeLcsWithApriori(inputFileName="Primjer1.tab", min_abs_sup=1, treeStrat=BOTTOM_UP)
    end=time.clock()
    print "Execution time: %.2f seconds" % (end-start)
    #print lcs
    #CollectionSetFactory.print_tree(lcs)
    
    #for t in tcs.transactions: print t
    #print "Pisem..."
    #CollectionSetFactory.saveTransactionSetToFile(tcs, outputFileName="Computer_shop")
    #print "Citam iz novog fajla..."
    #tcs=CollectionSetFactory.loadTransactionSetFromFile(inputFileName="Computer_shop.tcs")
    #for t in tcs.transactions: print t


def njamnjam():
    a=Collection([1,0,0,0,1,0,0,0,1])
    b=Collection([1,0,1,0,1,0,1,0,1])
    print a.elements
    print b.elements
    print a
    print b
    print a.OR(b)
    print a.AND(b)
    print a.XOR(b)
    print a.is_subset_of(b)
    print b.is_subset_of(a)
    kola=CollectionSetFactory.get_all_minus_one_subsets(b)
    for koka in kola: print koka
    a.support=4
    print a.support
    #print b.OR(a), b.AND(a), b.XOR(a)

def testiram_novo_ucitavanje():
    lcs1=CollectionSetFactory.initializeLcsWithApriori(inputFileName="resources\\input_datasets\\mushroom-trans.tab", min_abs_sup=6000, treeStrat=TOP_DOWN)
    

if __name__ == '__main__':
    #import threading
    #class MyThread ( threading.Thread ):
        #def run ( self ):
    #test_csf()
    testiram_novo_ucitavanje()
    #test_njamnjam()
    #nitna=MyThread()
    #nitna.run()
    #test_transaction()
    #test_csf()
    #test_pickled_tree('MojeMaloDrvo2.lcs')
    
        
        
        
        
