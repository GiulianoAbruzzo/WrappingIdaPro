from idautils import *
from idaapi import *
import idc
import os
import json

#traduzione da .dot a json
def da_dot_a_json(input):
    import networkx
    from networkx.readwrite import json_graph
    import pydot
    grafo_netx = networkx.drawing.nx_pydot.read_dot(input)
    grafo_json = json_graph.node_link_data(grafo_netx)
    return json_graph.node_link_data(grafo_netx)

def main():
	#inizializza la directory e la salviamo per dopo
	pathPartenza = os.getcwd()
	nuovaCartella= pathPartenza + "\Grafi_" + idaapi.get_root_filename()

	#se non esiste la cartella creala
	if not os.path.exists(nuovaCartella):		
		os.makedirs("Grafi_"+idaapi.get_root_filename())	

	#muoviamoci nella nuova cartella di lavoro
	os.chdir(nuovaCartella)	

	#aspetta la creazione del database
	idaapi.autoWait()

	#scorri i segmenti poi le funzioni e genera i grafi in formato .dot
	for segmento in Segments():
		for funcea in Functions(segmento, SegEnd(segmento)):
			
			#salva il nome della funzione
			nomeFunzione = GetFunctionName(funcea)
			for (startea, endea) in Chunks(funcea):
			
				#crea file txt in cui verra scritto il grafo json
				file = open(nomeFunzione+".txt", "w")
				
				#genera il grafo .dot
				idc.gen_flow_graph(nomeFunzione,nomeFunzione,startea,endea,CHART_GEN_DOT)
				
				#salvi il percorso del nuovo file dot
				path= os.getcwd()+'\\'+nomeFunzione+".dot"
				
				#traduzione da dot a json
				contenuto= da_dot_a_json(path)	
				
				#scrivi il contenuto sul file txt
				file.write(json.dumps(contenuto))
				file.close()
				
	#elimina i file .dot dopo la traduzione
	elementi = os.listdir(os.getcwd())
	for item in elementi:
		if item.endswith(".dot"):
			os.remove(os.path.join(os.getcwd(), item))
			
	#termina IDA	
	idc.Exit(0)
	
if __name__ == "__main__":
    main()	
