import re
import sys
import random
import psycopg2

predlosci = list()
identifikatori = list()


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
	
def parsirajPredloske(txt):
	i = 0
	while('ooooo' in txt):
		predlosci.append(txt[:txt.find('ooo')].strip(" "))
		txt = txt[(txt.find('ooo\n') + 4) :].strip(" ")
	if (len(txt.strip(" ").strip("\n")) > 0): 
		predlosci.append(txt.strip(" "))
	print("\nUspjesno ucitano "+str(len(predlosci))+" predlozaka!\n")

def pohraniSve( conn ) :
	cur = conn.cursor()
	insertQpref = "INSERT INTO eduMINE_HRZZ.predlozak(tekst) VALUES ('"
	for p in predlosci:
		insertQ = insertQpref + p + "');"
		insertQ.replace(r'\n', r'\r\n')
		cur.execute(insertQ)
		conn.commit()
		cur.execute("SELECT currval(pg_get_serial_sequence('eduMINE_HRZZ.predlozak','id'));")
		for id in cur.fetchall():
			identifikatori.append(id[0])
	print("\nPredlosci uspjesno upisani u bazu!\n")
	print("Identifikatori predlozaka su redom:")
	print(identifikatori)
	

if __name__ == "__main__":
	with open(sys.argv[1]) as myfile:
		tekst = myfile.read()
	parsirajPredloske(tekst)
	db = citaj_properties("dbConn.properties")
	myConnection = psycopg2.connect( host=db['hostname'], user=db['username'], password=db['password'], database=db['database'] )
	pohraniSve(myConnection)
	myConnection.close()
	



