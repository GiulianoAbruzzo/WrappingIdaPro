#esegui comandi
import subprocess
import os
import json

def main():
	#per ora a mano scrivo il file di input
	input="a_ARM.out"
	
	#eseguo la chiamata del processo ida
	subprocess.check_call(['ida.exe','-A', '-OIDAPython:script_crea_grafi.py', input])
	#subprocess.check_call(['ida.exe','-A', '-OIDAPython:script_crea_lista_funzioni.py', input])
	
	#elimino i database generati
	elementi = os.listdir(os.getcwd())
	for item in elementi:
		if item.endswith(".idb"):
			os.remove(os.path.join(os.getcwd(), item))
			
	for item in elementi:
		if item.endswith(".i64"):
			os.remove(os.path.join(os.getcwd(), item))
			
	#printa il dizionario
	print creaDizGrafi(input)
	#print creaDizFunzioni(input)
	
def creaDizGrafi(input):
	print "Creazione dizionario in corso..."
	pathPartenza = os.getcwd()
	nuovaCartella= pathPartenza + "\Grafi_" + input
	
	#se non esiste la cartella errore
	if not os.path.exists(nuovaCartella):		
		print "Errore nella generazione dei grafi"
				
	#muoviamoci nella nuova cartella di lavoro
	os.chdir(nuovaCartella)	
	newElenco = os.listdir(os.getcwd())	
		
	#creo il dizionario ci aggiungo come key il nome della funzione (nome del file .txt) e come valore il contenuto del testo
	dizionario = dict()
	for item in newElenco:
		if item.endswith(".txt"):
			file = open(item, "r")
			dizionario[item[:-4]]=file.read()
			file.close()
			
			#elimino il file .txt di appoggio ora inutile
			os.remove(os.path.join(os.getcwd(), item))
	
	#rimuovo la cartella di appoggio
	os.chdir(pathPartenza)
	os.rmdir(nuovaCartella)
	print "Creazione dizionario terminata"
	return json.dumps(dizionario)
	
def creaDizFunzioni(input):
	#crea dizionario 
	dizionario = dict()

	print "Creazione dizionario in corso..."
	
	#apro il file per ogni riga salvo nel dizionario nomefunzione e indirizzo di partenza (nel file txt di appoggio 
	#sono separati dalla stringa ////
	
	with open("ListaFunzioni_"+input+".txt","r") as f:
		for linea in f:
			dizionario[linea[:linea.index("////")].strip()] = linea[linea.index("////")+4:].strip()
	
	f.close()
	return dizionario

if __name__ == "__main__":
    main()
