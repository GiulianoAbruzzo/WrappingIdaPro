import os
import subprocess
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import json
import networkx as nx
from networkx.readwrite import json_graph
import pyrebase

#Config di firebase
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

#inizializza il database di firebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()

@app.route("/upload", methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        #lista dei file da uplodare
        uploaded_files = request.files.getlist("file[]")
        
        #se e' solo un file da uploadare salva il file e redirect alla pagina di visualizzazione
        if len(uploaded_files)==1:
            file = uploaded_files[0]
            filename = secure_filename(file.filename)
            
            result= db.child("Binari").child(filename.replace('.',',')).child("dizVisualizza").get()
            if (result.val() is None):
                return redirect(url_for('uploaded_file',filename=filename))
            else:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('uploaded_file',filename=filename))
        #Altrimenti salva ogni file e redirect alla pagina con tutti i file presenti
        else:
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #se il file non e' presente aggiungilo al database
                try:
                    #sostituisco i punti con le virgole (le key di firebase non possono contenere alcuni caratteri)
                    result= db.child("Binari").child(filename.replace('.',',')).child("dizVisualizza").get()
                    json_data = json.loads(result.val())
                    lista=list(json_data.keys())
                    
                except:
                    json_data= json.loads(visualizza_file(filename))
                    
                    #scrivo in una lista tutti i nomi delle funzioni
                    lista=list(json_data.keys())
                    
                    #scorri tutti i nomi per modificare i grafi
                    for item in lista:
                        #salvo il grafo (attualmente json)
                        G= json_graph.node_link_graph(json_data[item]["grafo"])
                        
                        #traduco con pydot il grafo in DOT
                        dG = nx.nx_pydot.to_pydot(G)
                        
                        #sostituisco il vecchio grafo JSON nel nuovo in DOT 
                        #lo salvo come una stringa poiche' non si puo' serializzare il formato DOT con json.dumps
                        json_data[item]["grafo"]=str(dG)
                
                    #salvo il dizionario nel database
                    data = {"dizVisualizza": json.dumps(json_data)}
                    db.child("Binari").child(filename.replace('.',',')).update(data)
                    
            #Finito di uploadare i file redirecta alla lista dei file
            return redirect(url_for('listafile'))
    return '''
    <!doctype html>
    <title>Wrapping Ida Pro</title>
    <h1>Carica un binario</h1>
    <form action="upload" method="post" enctype="multipart/form-data">
        <input type="file" multiple="" name="file[]" /><br />
        <input type="submit" value="Upload">
    </form>
    '''

@app.route('/uploaded/<filename>', methods=['GET','POST'])
def uploaded_file(filename):
    #Sostituisco i punti con le virgole per firebase e vedo se e' gia presente nel database
    try:
        result= db.child("Binari").child(filename.replace('.',',')).child("dizVisualizza").get()
        json_data = json.loads(result.val())
        lista=list(json_data.keys())
        print "Dizionario visualizza gia' presente nel database"
    except:
        #se non lo e' chiamo la funzione visualizza file che ritorna il dizionario della visualizzazione
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
    
        #Salvo nel database il dizionario visualizzazione
        data = {"dizVisualizza": json.dumps(json_data)}
        db.child("Binari").child(filename.replace('.',',')).update(data)
        
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
    #salvo il nome del file
    file = request.files['file']
    filename = secure_filename(file.filename)
    
    #se e' gia' presente nel database ritorna il valore altrimenti esegui lo script (sostituisco il punto poiche' non e' accettato da firebase nelle key)
    try:
        print "Dizionario funzioni gia presente nel database"
        result= db.child("Binari").child(filename.replace('.',',')).child("dizFunzioni").get()
        json_data = json.loads(result.val())
        return json_data
    except:
        #salvo il file per poter avviare lo script
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
    
    #cerco se e' gia' presente nel database se non lo e' avvio lo script altrimenti ritorno il valore del database
    result= db.child("Binari").child(filename.replace('.',',')).child("dizGrafo").get()
    
    if (result.val() is None):
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
       
    else:
        print "Dizionario grafi gia presente nel database"
        json_data = result.val()
        return json_data
                     
def estrai_funzioni(input,path):  
    #crea dizionario
    dizionario = dict()

    print "Creazione dizionario funzioni in corso..."

    #apro il file che e' gia salvato in formato json
    with open(path+"ListaFunzioni_"+input+".txt","r") as f:
        diz=f.read()
    
    #elimino il .txt ora inutile
    os.remove(os.path.join(path, "ListaFunzioni_"+input+".txt"))
    
    #salvo nel database il dizionario appena creato
    data = {"dizFunzioni": json.dumps(diz)}
    db.child("Binari").child(input.replace('.',',')).update(data)

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
    
    #salvo nel database il dizionario appena creato
    data = {"dizGrafo": json.dumps(dizionario)}
    db.child("Binari").child(input.replace('.',',')).update(data)
    
    #termino ritornando il dizionario in json
    print "Creazione dizionario grafi terminata"
    return json.dumps(dizionario)

@app.route('/uploaded',methods=['GET'])
def listafile():
        #Salvo in una lista tutti i binari caricati con dizionario e quelli senza
        try:
            lista=list()
            listaSenzaDiz=list()
            
            all_file = db.child("Binari").get()
            for file in all_file.each():
                result= db.child("Binari").child(file.key()).child("dizVisualizza").get()
                if (result.val() is None):
                    listaSenzaDiz.append(file.key().replace(',','.'))
                    print file.key().replace(',','.')+": non e' presente nel database il dizionario visualizza e' necessario uploadarlo di nuovo"
                else:
                    lista.append(file.key().replace(',','.'))
            
            #carico l'html con la lista di tutti i file nel database
            return render_template("listafile.html", filelist=lista, filelistsenzadiz=listaSenzaDiz)
        except:
            return "Nessun file trovato o nessun file con dizionario visualizza"
        
if __name__ == "__main__":
    app.run(debug=True)