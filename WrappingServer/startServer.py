import os
import subprocess
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import json
import networkx as nx
from networkx.readwrite import json_graph
import sqlite3
from concurrent.futures import ThreadPoolExecutor

#INSERISCI QUI IL NUMERO MASSIMO DI THREAD IN ESECUZIONE
MAX_THREAD= 2;
executor = ThreadPoolExecutor(MAX_THREAD)

#INSERISCI QUI LA PATH DOVE VERRANNO UPLOADATI 
#I FILE DEL SERVER E DOVE DEVI INSERIRE GLI SCRIPT "script_crea_grafi.py" e "script_crea_lista_funzioni.py"
UPLOAD_FOLDER = 'C:\Users\Giuliano\Desktop\UploadingFiles'
SERVER_LOC = 'C:\Users\Giuliano\Desktop\WrappingServer\databaseServer.db'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/upload", methods=['GET','POST'])
def upload():       
    #Carica la pagina html upload, nel momento del click di upload ci reindirizzera' alla pagina di caricamento
    return '''
    <!doctype html>
    <title>Wrapping Ida Pro</title>
    <h1>Carica un binario</h1>
        <form action="caricamento" enctype="multipart/form-data" method="post">
        <input multiple="multiple" name="file[]" type="file" />
        <input type="submit" value="Upload" /></form>
    '''    

@app.route('/caricamento', methods = ['POST'])
def caricamento():
    #Nel momento in cui arriviamo alla pagina del caricamento partira' un thread per l'upload sul server dei file
    f=executor.submit(thread_upload_file,request.files.getlist("file[]"))
    lista=f.result()
    #Questo thread ci ritornera' una lista dei nomi dei file caricati sul server
    
    if len(lista)==1:
        #Se e' solo un file ci spostiamo nella pagina della visualizzazione
        return redirect(url_for('uploaded_file',filename=lista[0]))
    else:
        #Altrimenti carica i file nel server e crea i loro dati di visualizzazione e ci sposta nella pagina della lista dei file sul database
        for file in lista:
            executor.submit(thread_uploaded,file)
            
        #QUI DEVO TROVARE UN MODO DI ATTENDERE CHE TUTTI I THREAD LANCIATI DAL FOR TERMINANO
        return redirect(url_for('listafile'))
    
@app.route('/uploaded/<filename>', methods=['GET','POST'])
def uploaded_file(filename):
    #Appena arrivato nella pagina della visualizzazione di un file parte un thread per ottenere i dati all'interno del database o estrarli dal file
    ff=executor.submit(thread_uploaded,filename)
    risultati=ff.result()
    
    #Ottenuti i risultati carichiamo la visualizzazione del file
    return render_template("uploadedfile.html", listaF=risultati[0], dict=risultati[1])

@app.route('/uploaded',methods=['GET'])
def listafile():
    #Faccio partire il thread per richiede la lista dei file
    f=executor.submit(thread_lista_file)
    
    #Controllo di che tipo e' il result, se e' una stringa allora la tabella e' vuota
    if isinstance(f.result(), basestring):
        return "Nessun file trovato o nessun file con dizionario visualizza"
        
    #Altrimenti e' una lista e carico la lista dei file nel database
    else:
        #carico l'html con la lista di tutti i file nel database
        return render_template("listafile.html", filelist=f.result())
    
@app.route('/estraiFunzioni', methods=['POST'])
def crea_funzioni():
    #faccio partire il thread della lista delle funzioni
    f=executor.submit(thread_lista_funzioni,request.files['file'])
    return f.result()

@app.route('/estraiCFG', methods=['POST'])
def crea_grafi():
    #faccio partire il thread del grafo
    f=executor.submit(thread_cfg,request.files['file'])
    return f.result()
                      
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
    
def thread_upload_file(uploaded_files):
    #Creiamo una lista dove inseriremo tutti i nomi dei file che andiamo a caricare
    lista=[]
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        
        print("Lanciato thread upload di: " +filename)
        
        #Salviamo tutti i file nella cartella del server e infine ritorniamo la lista dei nomi dei file caricati
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        lista.append(filename)
        
        print("Terminato thread upload di: " +filename)
    return lista
    
def thread_uploaded(filename):
    #Creiamo una lista dove inseriremo la lista con i nomi della funzione in posizione x[0] e il grafo in x[1]
    x=[]
    print("Lanciato thread caricaricamento visualizzazione di: "+filename)
    
    #Ci connettiamo al database
    con= sqlite3.connect(SERVER_LOC)
    c=con.cursor()
    
    #Cerchiamo se e' gia' presente un file con quel nome
    c.execute("SELECT dizV FROM tableV WHERE id="+"'"+filename+"'")
    result = c.fetchall()
    if not result:
        #print "Dizionario visualizza "+filename+ " non trovato"
    
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
        
        #Aggiungo alla lista i risultati prima di ritornarli 
        x.append(lista)
        x.append(json.dumps(json_data))
        
        print("Terminato thread caricaricamento visualizzazione di: "+filename)
        return x
        #return render_template("uploadedfile.html", listaF=lista, dict=json.dumps(json_data))
    else:
        #print "Dizionario visualizza "+filename+ " trovato"

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
        
        #aggiungo alla lista i risultati trovati
        x.append(lista)
        x.append(json.dumps(json_data))
        
        print("Terminato thread caricaricamento visualizzazione di: "+filename)
        return x
        
def thread_lista_file():
    print("Lanciato thread lista file nel database")
    
    #Creo una lista in cui andro' a inserire tutti i nomi dei file inseriti nel database
    lista=list()
    
    #Mi connetto al database se non esiste creo' la tabella
    con= sqlite3.connect(SERVER_LOC)
    c=con.cursor()
    
    #Cerco tutti gli id e li aggiungo alla lista
    c.execute("SELECT id FROM tableV")
    result = c.fetchall()
    
    #Se non ci sono risultati (tabella vuota) termino ritornando una stringa 
    if not result:
        print("Terminato thread lista file nel database")
        return "Nessun file trovato o nessun file con dizionario visualizza"
        
    #Altrimenti aggiungo tutti i file alla lista e ritorno la lista
    else:
        for file in result:
            lista.append(file[0])
        print ("Terminato thread lista file nel database")
        return lista
              
def thread_lista_funzioni(file):
    #salvo il nome del file
    filename = secure_filename(file.filename)
    
    print("Lanciato thread lista funzioni del file: "+filename)

    #mi connetto al database
    con= sqlite3.connect(SERVER_LOC)
    c=con.cursor()
    
    #controllo se esiste gia' il dizionario delle funzioni di questo file
    c.execute("SELECT dizF FROM tableF WHERE id="+"'"+filename+"'")
    result = c.fetchall()
    
    #se non esiste creo il database
    if not result:
        #salvo il file per poterci lavorare sopra
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
            print "Inserito il dizionario funzioni di "+ filename
            
        except:
            return "Errore non sono riuscito a inserire nel database il file: "+ filename
            
        c.close()
        con.close()
        
        print("Terminato thread lista funzioni del file: "+filename)
        return diz
        
    else:
        print ("Dizionario funzioni "+filename+" trovato")
        c.close()
        con.close()
 
        print("Terminato thread lista funzioni del file: "+filename)
        return result[0][0]          
         
def thread_cfg(file):
    #mi salvo il nome del file
    filename = secure_filename(file.filename)
    
    #mi connetto al database
    con= sqlite3.connect(SERVER_LOC)
    c=con.cursor()
    
    #cerco se esiste gia' il dizionario del grafo del file
    c.execute("SELECT dizG FROM tableG WHERE id="+"'"+filename+"'")
    result = c.fetchall()
    
    print("Lanciato thread json grafo del file: "+filename)
    
    #se non esiste lo facciamo creare dallo script crea grafi
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
            print "Inserito il dizionario grafi di "+ filename
        except:
            return "Errore non sono riuscito a inserire nel database il file: "+ filename
        
        c.close()
        con.close()
        print("Terminato thread json grafo del file: "+filename)
        return diz
        
    else:
        print ("Dizionario grafi "+filename+" trovato")
        c.close()
        con.close()
        print("Terminato thread json grafo del file: "+filename)
        return result[0][0]
         
if __name__ == "__main__":
    #Appena avviamo il server creiamo il database se non esiste
    con= sqlite3.connect(SERVER_LOC)
    c=con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS tableF (id TEXT unique,dizF TEXT)") #funzioni
    c.execute("CREATE TABLE IF NOT EXISTS tableG (id TEXT unique,dizG TEXT)") #grafi
    c.execute("CREATE TABLE IF NOT EXISTS tableV (id TEXT unique,dizV TEXT)") #visualizza  
    app.run(debug=True)