import os
import subprocess
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import json
import networkx as nx
from networkx.readwrite import json_graph
import pyrebase

config = {
    "apiKey": "AIzaSyCfjLyqAG31RR3NWqGoCVYI-t0GlZAzzMU",
    "authDomain": "wrappingserver.firebaseapp.com",
    "databaseURL": "https://wrappingserver.firebaseio.com",
    "storageBucket": "wrappingserver.appspot.com"
  };

firebase = pyrebase.initialize_app(config)

#INSERISCI QUI LA PATH DOVE VERRANNO UPLOADATI 
#I FILE DEL SERVER E DOVE DEVI INSERIRE GLI SCRIPT "script_crea_grafi.py" e "script_crea_lista_funzioni.py"
UPLOAD_FOLDER = 'C:\Users\Giuliano\Desktop\UploadingFiles'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
firebase = pyrebase.initialize_app(config)
db = firebase.database()

@app.route("/upload", methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        #salvo il file uploadato e faccio partire l'uploaded_file dove verra' visualizzato
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',filename=filename))
    return '''
    <!doctype html>
    <title>Wrapping Ida Pro</title>
    <h1>Carica un binario</h1>
    <form method=post enctype=multipart/form-data onSubmit=test()>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploaded/<filename>', methods=['GET','POST'])
def uploaded_file(filename):
    try:
        result= db.child("Binari").child(filename.replace('.',',')).child("dizVisualizza").get()
        json_data = json.loads(result.val())
        lista=list(json_data.keys())
    except:
        json_data= json.loads(visualizza_file(filename))
        #mi scrivo in lista tutti i nomi delle funzioni
        lista=list(json_data.keys())
        
        #scorri tutti i nomi per modificare i grafi
        for item in lista:
            #mi salvo il grafo (attualmente json)
            G= json_graph.node_link_graph(json_data[item]["grafo"])
            
            #traduco con pydot il grafo in DOT
            dG = nx.nx_pydot.to_pydot(G)
            
            #sostituisco il vecchio grafo JSON nel nuovo in DOT 
            #lo salvo come una stringa poiche' non si puo' serializzare il formato DOT con json.dumps
            json_data[item]["grafo"]=str(dG)
    
        data = {"dizVisualizza": json.dumps(json_data)}
        db.child("Binari").child(filename.replace('.',',')).set(data)
        
    #carico l'html passando la lista delle funzioni e il dizionario completo per la visualizzazione    
    return render_template("uploadedfile.html", listaF=lista, dict=json.dumps(json_data))
        
def visualizza_file(filename):
    #mi sposto nella cartella di upload
    currentpath=os.getcwd()
    os.chdir(UPLOAD_FOLDER)
        
    #faccio partitre lo script di visualizzazione che salva il dizionario in un file di testo
    print "Richiesto visualizzazione"
    subprocess.check_call(['idat64.exe','-A','-OIDAPython:script_visualizza.py', UPLOAD_FOLDER+'\\'+filename])
        
    #elimino i database generati da idat
    elementi = os.listdir(UPLOAD_FOLDER)
    for item in elementi:
        if item.endswith(".i64"):
            os.remove(os.path.join(UPLOAD_FOLDER, item))
    
    #creo il dizionario
    diz=dict()
    
    #apro il .txt (creato dallo script visualizza) che e' gia salvato in formato json
    with open(UPLOAD_FOLDER+'\\'+"Visualizza_"+filename+".txt","r") as f:
        diz=f.read()
    
    #elimino il .txt contenente il dizionario (creato dallo script visualizza) ora inutile
    os.remove(os.path.join(UPLOAD_FOLDER+'\\', "Visualizza_"+filename+".txt"))
    
    #elimino il binario passato
    os.remove(os.path.join(UPLOAD_FOLDER+'\\', filename))
    
    #termino ritornando il dizionario gia in json
    print "Creazione visualizzazione terminata"
    return diz
   
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

@app.route('/uploaded',methods=['GET'])
def listafile():
        try:
            lista=list()
            all_file = db.child("Binari").get()
            for file in all_file.each():
                lista.append(file.key().replace(',','.'))
                
            return render_template("listafile.html", filelist=lista)
        except:
            return "Nessun file trovato"
        
if __name__ == "__main__":
    app.run(debug=True)