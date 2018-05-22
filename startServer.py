import os
import subprocess
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename
import json

#modifica la path di dove saranno caricati i file
UPLOAD_FOLDER = 'C:\Users\Giuliano\Desktop\UploadingFiles'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/estraiFunzioni', methods=['GET', 'POST'])
def crea_funzioni():
    if request.method == 'POST':
        #salvo il file per poter avviare lo script
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        print "Richiesto dizionario funzioni"
        #subprocess.check_call(['idat64.exe','-A', '-OIDAPython:script_crea_lista_funzioni.py', UPLOAD_FOLDER+'\\'+filename])
        subprocess.check_call(['ida64.exe','-A', '-OIDAPython:script_crea_lista_funzioni.py', UPLOAD_FOLDER+'\\'+filename])
        
        #elimino i database generati
        elementi = os.listdir(UPLOAD_FOLDER)
        for item in elementi:
                if item.endswith(".i64"):
                        os.remove(os.path.join(UPLOAD_FOLDER, item))
                        
        #elimino il file passato
        os.remove(os.path.join(UPLOAD_FOLDER, filename))                
        return estrai_funzioni(filename,UPLOAD_FOLDER+'\\')

@app.route('/estraiCFG', methods=['GET', 'POST'])
def crea_grafi():
    if request.method == 'POST':
        #salvo il file per poter avviare lo script
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        print "Richiesto dizionario grafi"
        #subprocess.check_call(['idat64.exe','-A', '-OIDAPython:script_crea_grafi.py', UPLOAD_FOLDER+'\\'+filename])
        subprocess.check_call(['ida64.exe','-A', '-OIDAPython:script_crea_grafi.py', UPLOAD_FOLDER+'\\'+filename])
        
        #elimino i database generati
        elementi = os.listdir(UPLOAD_FOLDER)
        for item in elementi:
                if item.endswith(".i64"):
                        os.remove(os.path.join(UPLOAD_FOLDER, item))
                
        #elimino il file passato
        os.remove(os.path.join(UPLOAD_FOLDER, filename))              
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
    
    #termino
    print "Creazione dizionario funzioni terminato"
    return diz
            
def estrai_cfg(input,path):
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
            file = open(item, "r")
            dizionario[item[:-4]]=file.read()
            file.close()

            #elimino il file .txt di appoggio ora inutile
            os.remove(os.path.join(nuovaCartella, item))

    #rimuovo la cartella di appoggio
    os.chdir(pathPartenza)
    os.rmdir(nuovaCartella)
    
    #termino
    print "Creazione dizionario grafi terminata"
    return json.dumps(dizionario)

if __name__ == "__main__":
    app.run(debug=True)