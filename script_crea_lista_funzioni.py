from idautils import *
from idaapi import *
import os

#crea il file
text_file = open("ListaFunzioni_"+idaapi.get_root_filename()+".txt", "w")

#aspetta il caricamento
idaapi.autoWait()

#apri il database
for segea in Segments():
	for funcea in Functions(segea, SegEnd(segea)):
		functionName = GetFunctionName(funcea)
		for (startea, endea) in Chunks(funcea):
			text_file.write(functionName+"\n")

#chiudi il file	e termina	
text_file.close()
idc.Exit(0)
