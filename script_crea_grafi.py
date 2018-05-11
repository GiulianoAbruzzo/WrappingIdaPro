from idautils import *
from idaapi import *
import idc
import os

#inizializza la directory
filenamepath = os.getcwd()
target= filenamepath + "\Grafi_" + idaapi.get_root_filename()

#se non esiste la cartella creala
if not os.path.exists(target):		
	os.makedirs("Grafi_"+idaapi.get_root_filename())	

#muoviamoci nella nuova cartella di lavoro
os.chdir(target)	

#aspetta la creazione del database
idaapi.autoWait()

#scorri i segmenti poi le funzioni e genera i grafi in formato .dot
for segea in Segments():
	for funcea in Functions(segea, SegEnd(segea)):
		functionName = GetFunctionName(funcea)
		for (startea, endea) in Chunks(funcea):
			idc.gen_flow_graph(functionName,functionName,startea,endea,CHART_GEN_DOT)

idc.Exit(0)		