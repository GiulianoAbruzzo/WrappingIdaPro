# WrappingIdaPro

Wrapping di IdaPro con l'utilizzo di IdaPython

### Specifiche progetto

```C 
startserver.py 
```

Con l'utilizzo di flask, attiva un server all'indirizzo http://127.0.0.1:5000/ a cui è possibile, passandogli dei binari, fare richieste attraverso cURL.

```C 
script_crea_grafi.py 
```
Crea una cartella contenente tutti i Control Flow Graph delle funzioni del binario in input

```C 
script_crea_lista_funzioni.py 
```
Crea un file di testo contenenti tutti i nomi delle funzioni del binario in input

### Utilizzo degli script

Prima di poter avviare il server è necessario modificare la path della upload folder all'interno dello startserver.py:

```C 
UPLOAD_FOLDER = 'INSERISCI/QUI/LA/PATH/DOVE/VERRANNO/CARICATI/I/FILE'
```

**E' necessario inserire all'interno della nostra UPLOAD_FOLDER i due script: script_crea_grafi.py, script_crea_lista_funzioni.py**

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
