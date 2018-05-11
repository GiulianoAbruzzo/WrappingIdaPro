# WrappingIdaPro

Wrapping di IdaPro con l'utilizzo di IdaPython

### Specifiche progetto

```C 
script_crea_grafi.py 
```
Crea una cartella contenente tutti i Control Flow Graph delle funzioni del binario in input

```C 
script_crea_lista_funzioni.py 
```
Crea un file di testo contenenti tutti i nomi delle funzioni del binario in input

### Utilizzo degli script

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

- Pydot

```C 
$ pip install pydot
```

- Graphviz

```C
https://www.graphviz.org/download/
```
