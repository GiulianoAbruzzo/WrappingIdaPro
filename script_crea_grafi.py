from idautils import *
from idaapi import *
import idc
import os
import json
import binascii
import networkx as nx
from networkx.readwrite import json_graph

def main():
    #inizializza la directory e la salviamo per dopo
    pathPartenza = os.getcwd()
    nuovaCartella= pathPartenza + "\Grafi_" + idaapi.get_root_filename()

    #se non esiste la cartella creala
    if not os.path.exists(nuovaCartella):       
        os.makedirs("Grafi_"+idaapi.get_root_filename())    

    #muoviamoci nella nuova cartella di lavoro
    os.chdir(nuovaCartella) 

    # aspetta la creazione del database
    idaapi.autoWait()
    
    # scorri i segmenti poi le funzioni
    for segmento in Segments():
        for funcea in Functions(segmento, SegEnd(segmento)):
            # salva il nome della funzione
            nomeFunzione = GetFunctionName(funcea)
            
            #scorro i chunks
            for (startea, endea) in Chunks(funcea):
                func = get_func(startea)
                
                #creo un oggetto FlowChart che posso iterare sui nodi
                flowChart = FlowChart(f=func, bounds=None, flags=0)
                
                #creo il Grafo
                G=nx.DiGraph()      
                
                #itero sui nodi n e un oggetto nodo che ha tre campo id, startEA, endEA
                for n in flowChart:
                
                    #se il nodo non e' presente nel grafo lo aggiungo
                    if (str(n.id) not in G.nodes()):
                        G.add_node(str(n.id),label='',asm='')
                        
                    #n contiene anche il metodo succs che mi ritona l id dei nodi successori
                    successors = []
                    for s in n.succs():
                        successors.append(s.id)
                        #se e' un successore lo aggiungo al grafo
                        G.add_edge(str(n.id),str(s.id))
                        
                    #salvo l'indirizzo di partenza
                    addr = n.startEA
                    
                    #salvo in queste variabili gli hex e le istruzioni
                    totIstruzioni=""
                    totHex=""
                    
                    #se e' il nodo di partenza aggiungo il nome della funzione
                    if (str(n.id)=="0"):
                        totIstruzioni=nomeFunzione+":"+"\n"
                    
                    #faccio un decoding delle istruzioni del blocco parto dalla prima istruzione del nodo
                    #mi fermo quando arrivo all indirizzo di fine del nodo
                    while(addr < n.endEA):
                        #DecodeInstruict mi crea un oggetto insn_t che ha come campo size la lunghezza dell istruzione 
                        insn = DecodeInstruction(addr)
                        if (insn is None):
                            break
                            
                        #prendo l' istruzione disassemblata
                        disasm = idc.GetDisasm(addr)
                        
                        #prendo i bytes dell istruzione
                        byte = get_bytes(addr, insn.size)
                        
                        #concateno alle due stringhe
                        totIstruzioni+=disasm+"\n"
                        totHex+=str(binascii.hexlify(byte))+"\n"
                        
                        # aggiungo size all'indirzzo per andare all istruzione successiva'
                        addr = addr + insn.size
                        
                    #finito il while modifico il contenuto dei nodi
                    G.node[str(n.id)]['label'] = totIstruzioni
                    G.node[str(n.id)]['asm'] = totHex
                
                #salvo il nostro grafo in json
                file = open(nomeFunzione+".txt", "w")
                file.write(json.dumps(json_graph.node_link_data(G)))
                file.close()
             
    # termina IDA
    idc.Exit(0)

if __name__ == "__main__":
    main()
