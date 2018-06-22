import os
import subprocess
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import json
import networkx as nx
from networkx.readwrite import json_graph
import sqlite3

#INSERISCI QUI LA PATH DOVE VERRANNO UPLOADATI 
#I FILE DEL SERVER E DOVE DEVI INSERIRE GLI SCRIPT "script_crea_grafi.py" e "script_crea_lista_funzioni.py"
UPLOAD_FOLDER = 'C:\Users\Giuliano\Desktop\UploadingFiles'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route("/upload", methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        #lista dei file da uplodare
        uploaded_files = request.files.getlist("file[]")
        
        #se e' solo un file da uploadare salva il file e redirect alla pagina di visualizzazione
        if len(uploaded_files)==1:
            file = uploaded_files[0]
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',filename=filename))
            
        #Altrimenti salva ogni file e redirect alla pagina di tutti i file nel database
        else:
            con= sqlite3.connect('C:\Users\Giuliano\Desktop\WrappingServer\databaseServer.db')
            c=con.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS tableV (id TEXT unique,dizV TEXT)") #visualizza
        
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                c.execute("SELECT dizV FROM tableV WHERE id="+"'"+filename+"'")
                result = c.fetchall()
                if not result:
                    json_data= json.loads(estrai_visualizza(filename))
                    
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
                    
                    try: 
                        #tenta di inserire nel database il nuovo file
                        c.execute('INSERT INTO tableV (id,dizV) VALUES (?, ?)',(filename,json.dumps(json_data)))
                        con.commit()
                    except:
                        return "Errore non sono riuscito a inserire nel database il file:"+ filename
                else:
                    #result[0] restituisce la prima tupla con id=filename (id e' unico quindi avra size sempre o 0 se non e' presente o 1 se e' presente
                    #lo restituisce in formato di tupla (diz,) quindi dobbiamo prendere il primo valore del primo risultato--> result[0][0]
                    json_data = json.loads(result[0][0])
                    
                    #mi scrivo in lista tutti i nomi delle funzioni
                    lista=list(json_data.keys())
                    
                    #elimino il binario passato
                    os.remove(os.path.join(UPLOAD_FOLDER+'\\', filename))
            
            #chiudo le connessioni
            c.close()
            con.close()
            
            #Finito di uploadare i file redirecta alla lista dei file
            return redirect(url_for('listafile'))
    return '''
    <!doctype html>
    <title>Wrapping Ida Pro</title>
    <h1>Carica un binario</h1>
        <form action="upload" enctype="multipart/form-data" method="post">
        <input multiple="multiple" name="file[]" type="file" />
        <input type="submit" value="Upload" /></form>
    '''

@app.route('/uploaded/<filename>', methods=['GET','POST'])
def uploaded_file(filename):
    con= sqlite3.connect('C:\Users\Giuliano\Desktop\WrappingServer\databaseServer.db')
    c=con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS tableV (id TEXT unique,dizV TEXT)") #visualizza
    
    c.execute("SELECT dizV FROM tableV WHERE id="+"'"+filename+"'")
    result = c.fetchall()
    if not result:
        print "Dizionario visualizza "+filename+ " non trovato"
    
        #carica il dizionario creato dalla funzione estrai_visualizza
        json_data= json.loads(estrai_visualizza(filename))
        
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
        
        try: 
            #tenta di inserire nel database il nuovo file e poi chiudo la connessione
            c.execute('INSERT INTO tableV (id,dizV) VALUES (?, ?)',(filename,json.dumps(json_data)))
            con.commit()
        except:
            return "Errore non sono riuscito a inserire nel database il file:"+ filename
          
        c.close()
        con.close()
        return render_template("uploadedfile.html", listaF=lista, dict=json.dumps(json_data))
    else:
        print "Dizionario visualizza "+filename+ " trovato"

    
        #result[0] restituisce la prima tupla con id=filename (id e' unico quindi avra size sempre o 0 se non e' presente o 1 se e' presente
        #lo restituisce in formato di tupla (diz,) quindi dobbiamo prendere il primo valore del primo risultato--> result[0][0]
        json_data = json.loads(result[0][0])
        
        #mi scrivo in lista tutti i nomi delle funzioni
        lista=list(json_data.keys())
        
        #chiudo le connessioni
        c.close()
        con.close()
        
        #elimino il binario passato (uso il try perche' se accedo al file dalla lista dei file non sara' presente il binario)
        try: os.remove(os.path.join(UPLOAD_FOLDER+'\\', filename))
        except: pass
        
        return render_template("uploadedfile.html", listaF=lista, dict=json.dumps(json_data))    
          
@app.route('/estraiFunzioni', methods=['POST'])
def crea_funzioni():
    #salvo il nome del file
    file = request.files['file']
    filename = secure_filename(file.filename)
    
    print os.getcwd()
    
    con= sqlite3.connect('C:\Users\Giuliano\Desktop\WrappingServer\databaseServer.db')
    c=con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS tableF (id TEXT unique,dizF TEXT)") #funzioni
    
    c.execute("SELECT dizF FROM tableF WHERE id="+"'"+filename+"'")
    result = c.fetchall()
    if not result:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        print ("Dizionario funzioni "+ filename + " non trovato")
    
        #mi sposto nella cartella di upload e salvo la vecchia cartella di lavoro
        currentpath=os.getcwd()
        os.chdir(UPLOAD_FOLDER)
            
        #chiamo lo script "script_crea_lista_funzioni.py"
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
        diz= estrai_funzioni(filename,UPLOAD_FOLDER+'\\')
        
        #tenta di inserire nel database il nuovo file e poi chiudo la connessione
        try:
            c.execute('INSERT INTO tableF (id,dizF) VALUES (?, ?)',(filename,json.dumps(diz)))
            con.commit()
            c.close()
            con.close()
            print "Inserito il dizionario funzioni di "+ filename
            
        except:
            c.close()
            con.close()
            return "Errore non sono riuscito a inserire nel database il file: "+ filename
         
        return diz
        
    else:
        print ("Dizionario funzioni "+filename+" trovato")
        c.close()
        con.close()
        return result[0][0]

@app.route('/estraiCFG', methods=['POST'])
def crea_grafi():
    #salvo il file per poter avviare lo script
    file = request.files['file']
    filename = secure_filename(file.filename)
    
    con= sqlite3.connect('C:\Users\Giuliano\Desktop\WrappingServer\databaseServer.db')
    c=con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS tableG (id TEXT unique,dizG TEXT)") #grafi
    
    c.execute("SELECT dizG FROM tableG WHERE id="+"'"+filename+"'")
    result = c.fetchall()
    if not result:
        print "Dizionario grafi "+filename+ " non trovato"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #mi sposto nella cartella di upload e salvo la vecchia cartella di lavoro
        currentpath=os.getcwd()
        os.chdir(UPLOAD_FOLDER)
             
        #chiamo lo script "script_crea_grafi.py"
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
        diz= estrai_cfg(filename,UPLOAD_FOLDER)
        
        try: 
            #tenta di inserire nel database il nuovo file e poi chiudo la connessione
            c.execute('INSERT INTO tableG (id,dizG) VALUES (?, ?)',(filename,diz))
            con.commit()
            c.close()
            con.close()
            print "Inserito il dizionario grafi di "+ filename
        except:
            c.close()
            con.close()
            return "Errore non sono riuscito a inserire nel database il file: "+ filename
        
        return diz
        
    else:
        print ("Dizionario grafi "+filename+" trovato")
        c.close()
        con.close()
        return result[0][0]
                      
def estrai_funzioni(input,path):  
    #crea dizionario
    dizionario = dict()

    #apro il file che e' gia salvato in formato json
    with open(path+"ListaFunzioni_"+input+".txt","r") as f:
        diz=f.read()
    
    #elimino il .txt ora inutile
    os.remove(os.path.join(path, "ListaFunzioni_"+input+".txt"))

    #termino ritornando il dizionario gia in json
    return diz
            
def estrai_cfg(input,path):
    #salvo la path currente e mi sposto nella cartella creata dallo script crea_grafi dove trovero tutti i grafi della funzione
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
    return json.dumps(dizionario)

def estrai_visualizza(filename):
    #mi sposto nella cartella di upload
    currentpath=os.getcwd()
    os.chdir(UPLOAD_FOLDER)
        
    #faccio partitre lo script di visualizzazione che salva il dizionario in un file di testo
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
    
    #torno nella cartella di start
    os.chdir(currentpath)
    
    #termino ritornando il dizionario gia in json
    return diz
    
@app.route('/uploaded',methods=['GET'])
def listafile():
        #Salvo in una lista tutti i binari caricati con dizionario visualizza
        #try:
        lista=list()
        con= sqlite3.connect('C:\Users\Giuliano\Desktop\WrappingServer\databaseServer.db')
        c=con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS tableV (id TEXT unique,dizV TEXT)") #visualizza
        c.execute("SELECT id FROM tableV")
        result = c.fetchall()
        if not result:
            return "Nessun file trovato o nessun file con dizionario visualizza"
        else:
            for file in result:
                lista.append(file[0])
            #carico l'html con la lista di tutti i file nel database
            return render_template("listafile.html", filelist=lista)      
        
if __name__ == "__main__":
    app.run(debug=True, threaded=True)