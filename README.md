# WrappingIdaPro

Wrapping di IdaPro con l'utilizzo di IdaPython, Flask, SQLite.

### Specifiche progetto

```C 
startserver.py 
```

Con l'utilizzo di flask, attiva un server all'indirizzo http://127.0.0.1:5000/ da cui è possibile ottenere, passandogli dei binari,attraverso cURL il dizionario delle funzioni e il control flow graph del binario, oppure da sito web una visualizzazione del grafo la lista delle funzioni e le istruzioni disassemblate.

```C 
http://127.0.0.1:5000/upload 
```

All'indirizzo http://127.0.0.1:5000/upload è possibile caricare uno o più binari. Se il dizionario della visualizzazione del binario da caricare è già presente nel database lo carica direttamente altrimenti lo genera chiamando lo script "script_visualizza.py" presente nella cartella di UploadingFiles. Se sono più binari da caricare allora una volta finito il caricamento dei binari mostrerà la lista dei binari al momento presente nel database.

![alt text](https://github.com/GiulianoAbruzzo/WrappingIdaPro/blob/master/Preview.PNG)

```C 
http://127.0.0.1:5000/uploaded
```

Mostra la lista dei binari con dizionario visualizza al momento presenti nel database.

```C 
script_visualizza.py 
```

Crea un dizionario contenente la lista di tutte le funzioni presenti nel binario, il control flow graph di ogni funzione, l'indirizzo di partenza di ogni funzione e le istruzioni disassemblate.

```C 
script_crea_grafi.py 
```
Crea una cartella contenente tutti i Control Flow Graph delle funzioni del binario in input

```C 
script_crea_lista_funzioni.py 
```

Crea un file di testo contenenti tutti i nomi delle funzioni del binario in input

### Utilizzo degli script

Prima di poter avviare il server è necessario modificare la path della upload folder e la path del database (lo creerà lui da zero) all'interno dello startserver.py:

```C 
UPLOAD_FOLDER = 'INSERISCI/QUI/LA/PATH/DOVE/VERRANNO/CARICATI/I/FILE'
SERVER_LOC= 'INSERISCI/QUI/LA/PATH/DOVE/VERRANNO/CARICATI/I/FILE/databaseServer.db'
```

**E' necessario inserire all'interno della nostra UPLOAD_FOLDER i tre script: script_crea_grafi.py, script_crea_lista_funzioni.py, script_visualizza.py**

Avvia il server attraverso il comando da cmd di windows trovandoci nella cartella del server:

```C 
$ python startserver.py
```


**E' possibile ora fare richieste al server.**

Per richiede i grafi inserire il comando da cmd di windows:

```C 
$ curl -F file=INSERISCI/PATH/DEL/FILE http://127.0.0.1:5000/estraiCFG
```

Restituirà il dizionario JSON avente come chiavi il nome delle funzioni del binario e come valori il CFGraph 
di networkx delle funzioni corrispondenti.

Per richiede la lista delle funzioni inserire il comando da cmd di windows:

```C 
$ curl -F file=INSERISCI/PATH/DEL/FILE http://127.0.0.1:5000/estraiFunzioni
```
Restituirà il dizionario JSON avente come chiavi il nome delle funzioni del binario e come valori un dizionario interno
composto da:
"address" con l'indirizzo di partenza della funzione
"label" con la lista delle istruzioni decodificate
"asm" con la lista delle istruzioni in hex



**E' anche possibile avviare i due script senza passare per il server**

Da prompt dei comandi di windows:
(Inserire la cartella di ida nella PATH o inserire la path intera di ida.exe)

```C 
$ ida.exe -A -OIDAPython:script_crea_grafi.py file.out
```

Per 64bit:

```C 
$ ida64.exe -A -OIDAPython:script_crea_grafi.py a_x86_64.out
```

### Requisiti

- Networkx

```C 
$ pip install networkx
```

- Flask

```C
$ pip install flask
```

- cURL

```C
https://curl.haxx.se/download.html
```

- Python 2.7

```C
https://www.python.org/downloads/release/python-2714/
```
