import os
import subprocess
from flask import Flask, request
from werkzeug.utils import secure_filename
import json

#INSERISCI QUI LA PATH DOVE VERRANNO UPLOADATI 
#I FILE DEL SERVER E DOVE DEVI INSERIRE GLI SCRIPT "script_crea_grafi.py" e "script_crea_lista_funzioni.py"
UPLOAD_FOLDER = 'C:\Users\Giuliano\Desktop\UploadingFiles'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
@app.route('/estraiFunzioni', methods=['POST'])
def crea_funzioni():
    #salvo il file per poter avviare lo script
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    #mi sposto nella cartella di upload e salvo la vecchia cartella di lavoro
    currentpath=os.getcwd()
    os.chdir(UPLOAD_FOLDER)
        
    #chiamo lo script "script_crea_lista_funzioni.py"
    print "Richiesto dizionario funzioni"
    subprocess.check_call(['idat64.exe','-A','-OIDAPython:script_crea_lista_funzioni.py', UPLOAD_FOLDER+'\\'+filename])
        
    #elimino i database generati
    elementi = os.listdir(UPLOAD_FOLDER)
    for item in elementi:
        if item.endswith(".i64"):
            os.remove(os.path.join(UPLOAD_FOLDER, item))
                        
    #elimino il file passato
    os.remove(os.path.join(UPLOAD_FOLDER, filename))  

    #torno nella cartella del server e chiamo la funzione estrai_funzioni che mi ritorna un dizionario json
    os.chdir(currentpath)    
    return estrai_funzioni(filename,UPLOAD_FOLDER+'\\')

@app.route('/estraiCFG', methods=['POST'])
def crea_grafi():
    #salvo il file per poter avviare lo script
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    #mi sposto nella cartella di upload e salvo la vecchia cartella di lavoro
    currentpath=os.getcwd()
    os.chdir(UPLOAD_FOLDER)
         
    #chiamo lo script "script_crea_grafi.py"
    print "Richiesto dizionario grafi"
    subprocess.check_call(['idat64.exe','-A','-OIDAPython:script_crea_grafi.py', UPLOAD_FOLDER+'\\'+filename])
        
    #elimino i database generati
    elementi = os.listdir(UPLOAD_FOLDER)
    for item in elementi:
        if item.endswith(".i64"):
            os.remove(os.path.join(UPLOAD_FOLDER, item))
                
    #elimino il file passato
    os.remove(os.path.join(UPLOAD_FOLDER, filename))   

    #torno nella cartella del server e chiamo la funzione estrai_funzioni che mi ritorna un dizionario json
    os.chdir(currentpath)
    return estrai_cfg(filename,UPLOAD_FOLDER)        
        
def estrai_funzioni(input,path):  
    #crea dizionario
    dizionario = dict()

    print "Creazione dizionario funzioni in corso..."

    #apro il file che e' gia salvato in formato json
    with open(path+"ListaFunzioni_"+input+".txt","r") as f:
        diz=f.read()
    
    #elimino il .txt ora inutile
    os.remove(os.path.join(path, "ListaFunzioni_"+input+".txt"))
    
    #termino ritornando il dizionario gia in json
    print "Creazione dizionario funzioni terminato"
    return diz
            
def estrai_cfg(input,path):
    #salvo la path currente e mi sposto nella cartella creata dallo script crea_grafi dove trovero tutti i grafi della funzione
    print "Creazione dizionario grafi in corso..."
    pathPartenza = path
    nuovaCartella= pathPartenza + "\Grafi_" + input

    #se non esiste la cartella errore
    if not os.path.exists(nuovaCartella):
        print "Errore nella generazione dei grafi"

    #muoviamoci nella nuova cartella di lavoro
    os.chdir(nuovaCartella)
    newElenco = os.listdir(nuovaCartella)

    #creo il dizionario ci aggiungo come key il nome della funzione (nome del file .txt) e come valore il contenuto del testo
    dizionario = dict()
    for item in newElenco:
        if item.endswith(".txt"):
            
            #apro i vari file dei grafi e levo il .txt finale (-4) e salvo i valori dei grafi in un dizionario
            file = open(item, "r")
            dizionario[item[:-4]]=file.read()
            file.close()

            #elimino il file .txt di appoggio ora inutile
            os.remove(os.path.join(nuovaCartella, item))

    #rimuovo la cartella di appoggio
    os.chdir(pathPartenza)
    os.rmdir(nuovaCartella)
    
    #termino ritornando il dizionario in json
    print "Creazione dizionario grafi terminata"
    return json.dumps(dizionario)

if __name__ == "__main__":
    app.run(debug=True)