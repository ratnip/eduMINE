import re
import sys
import random
import psycopg2



class Rjesenje:
	tekstVrijednost = ''
	tekstPrikaz = ''
	tocnost = True
	
	
	def __repr__(self):
		txt = ''
		if (self.tekstVrijednost != ''):
			txt += self.tekstVrijednost + ' '
		if (self.tekstPrikaz != ''):
			txt += "[" + self.tekstPrikaz + '] '
		txt += str(self.tocnost)
		return(txt)
		
	def __str__(self):
		return(self.__repr__())
    
class Zadatak:
	parametri = {}
	tekst = ''
	rjesenja = []
	rjTip = 'tekst'
	kljucne_rijeci = []

#GLOBALS
z = Zadatak()
precision = 2

def citaj_properties(staza, sep='=', comment_char='#'):
	props = {}
	with open(staza, "rt") as f:
		for line in f:
			l = line.strip()
			if l and not l.startswith(comment_char):
				key_value = l.split(sep)
				key = key_value[0].strip()
				value = sep.join(key_value[1:]).strip().strip('"') 
				props[key] = value 
	print("\nPostavke baze ucitane!\n")
	return props
	
def evalRound(txt):
	res = eval(txt, globals(), z.parametri)
	if (res - int(res)) == 0:
		res = int(res)
	else:
		res = round(res,precision)
	return(str(res))


def convertBlock(txt,  prec = 2):
	pattern_expr = re.compile('\$\(.*?\)')
	exprs = re.findall(pattern_expr, txt)
	exprs = list(map(lambda x:evalRound(x[2:-1]), exprs))
	while len(exprs) > 0:
		txt = re.sub(pattern_expr, exprs.pop(0), txt, count = 1)
	return txt

def parsirajRjesenja(txt):
	txt = txt.strip(" ").strip("\n")
	if (txt[0:1] != '[') and (txt[1:2]!='['):
		z.rjTip = 'broj'
	txt = convertBlock(txt)
	for red in txt.splitlines():
		r = Rjesenje()
		if red[0:1]=='!':
			red = red[1:]
			r.tocnost = False
		if z.rjTip == 'broj':
			r.tekstVrijednost = red[:red.find('[')].strip(" ")
		r.tekstPrikaz = red[red.find('[')+1:red.find(']')]
		z.rjesenja.append(r)
	
    
def parsirajZadatak(txt):
	parTxt = ''
	tekstTxt = ''
	rjesTxt = ''
	kljucTxt = ''
    
	if '---' in txt:    # ima parametre
		parTxt = txt[:txt.find('---')].strip(" ")
		txt = txt[txt.rfind('---')+3:]
    # tekst i rjesenje mora imati
	if '+++' not in txt:
		raise Error('Zadatak mora razdvojiti tekst i rjesenje sa +++++++!!')
	tekstTxt = txt[:txt.find('+++')].strip(" ")
	txt = txt[txt.rfind('+++')+3:]
	if '===' in txt:
		rjesTxt = txt[:txt.find('===')].strip(" ")
		kljucTxt = txt[txt.rfind('===')+3:].strip(" ")
	else:
		rjesTxt = txt.strip(" ")

	if parTxt!='':
		parsirajParametre(parTxt)
	z.tekst = convertBlock(tekstTxt)
	parsirajRjesenja(rjesTxt)
	slovo = 65
	if (len(z.rjesenja) > 1):
		for i in range(len(z.rjesenja)):
			z.rjesenja[i].oznaka = chr(slovo)
			slovo += 1
			
	if kljucTxt.strip(" ").strip("\n")!='':
		z.kljucne_rijeci = kljucTxt.strip(" ").strip("\n").split(" ")
		z.kljucne_rijeci = [r[1:] if r[0:1]=='#' else r for r in z.kljucne_rijeci]
	
		

def parsirajParametre(parTxt):
	parTxt = parTxt.split("\n")
	parTxt = [p for p in parTxt if len(p.strip()) > 0]
	for p in parTxt:
		if '$' in p:
			p = convertBlock(p)
		p = p.split("=")
		if (p[1].strip()[0] in ['\'', '\"']):
			z.parametri[p[0].strip()] = p[1].strip()[1:-1]
		else:
			if 'rand' in p[1]:
				p[1] = 'random.choice([' + p[1][p[1].find("(")+1 : p[1].find(")")] + '])'
			z.parametri[p[0].strip()] = eval(p[1].strip())

def pohraniZadatak( predlozakId, conn ) :
	zad_id = None
	cur = conn.cursor()
	insertQ = "INSERT INTO eduMINE_HRZZ.zadatak(tekst, predlozak_id, tip_zadatka_id) VALUES ('"
	insertQ += z.tekst + "',"
	insertQ += str(predlozakId) + ","
	if (len(z.rjesenja) > 1):
		insertQ += "1);"
	else:
		insertQ += "2);"
	cur.execute(insertQ)
	conn.commit()
	cur.execute("SELECT currval(pg_get_serial_sequence('eduMINE_HRZZ.zadatak','id'));")
	for id in cur.fetchall():
		zad_id = id[0]
	insertQpref = "INSERT INTO eduMINE_HRZZ.rjesenje(oznaka, tekst_vrijednost, tekst_prikaz, tocnost, zadatak_id) VALUES ('"
	for r in z.rjesenja:
		insertQ = insertQpref + r.oznaka + "', "
		if (r.tekstVrijednost == ''):
			insertQ += "NULL, "
		else:
			insertQ += "'" + r.tekstVrijednost + "', "
		insertQ += "'" + r.tekstPrikaz + "', "
		insertQ += str(r.tocnost) + ", "
		insertQ += str(zad_id) + ");"
		cur.execute(insertQ)
		conn.commit()
			

def citajPredlozak(predlozakId, conn):
		predlozak = ''
		cur = conn.cursor()
		cur.execute("SELECT tekst from eduMINE_HRZZ.predlozak WHERE id = " + str(predlozakId) + ";")
		for i in cur.fetchall():
			predlozak = i[0]
			break
		return(predlozak.strip(" ").strip("\n"))
    


    

if __name__ == "__main__":
	db = citaj_properties("dbConn.properties")
	myConnection = psycopg2.connect( host=db['hostname'], user=db['username'], password=db['password'], database=db['database'] )
	pred = citajPredlozak(sys.argv[1], myConnection)
	#print("Procitan predlozak:\n" + pred)
	parsirajZadatak(pred)
	print("Instanciran zadatak:")
	print("\nParametri:\n" + str(z.parametri))
	print("\nTekst:\n" + z.tekst)
	print("\nRjesenja:\n" + str(z.rjesenja))
	print("\nKljucne rijeci:\n" + str(z.kljucne_rijeci))
	pohraniZadatak(sys.argv[1], myConnection)
	myConnection.close()








