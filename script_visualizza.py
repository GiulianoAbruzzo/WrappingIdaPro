from idautils import *
from idaapi import *
import os
import binascii
import json

import sys
sys.path.append("C:\python27-x64\Lib\site-packages")
import networkx as nx
from networkx.readwrite import json_graph

try: 
    #crea il file
    text_file = open("Visualizza_"+idaapi.get_root_filename()+".txt", "w")

    #aspetta il caricamento
    idaapi.autoWait()

    #json di tutte le funzioni
    diz={}

    #apri il database
    for segea in Segments():
        for funcea in Functions(segea, SegEnd(segea)):
            functionName = GetFunctionName(funcea)
            functionStart = "0x%08x"%(funcea)
            
            dizInterno={}
            totI=""
            
            for (startea, endea) in Chunks(funcea):
                for head in Heads(startea, endea):
                    totI+="0x%08x"%(head)+": "+GetDisasm(head)+"\n"
                    
                func = get_func(startea)
                flowChart = FlowChart(f=func, bounds=None, flags=0)
                G=nx.DiGraph()      
                
                #itero sui nodi n e un oggetto nodo che ha tre campo id, startEA, endEA
                for n in flowChart:
                   
                    G.add_node(int(str(n.id)),label='',address="0x%08x"%(n.startEA),shape="box")
                        
                    #n contiene anche il metodo succs che mi ritona l id dei nodi successori
                    successors = []
                    for s in n.succs():
                        successors.append(s.id)
                        #se e' un successore lo aggiungo al grafo
                        G.add_edge(int(str(n.id)),int(str(s.id)))
                        
                    #salvo l'indirizzo di partenza
                    addr = n.startEA
                    
                    #salvo in queste variabili gli hex e le istruzioni
                    totIstruzioni=""
                    
                    #faccio un decoding delle istruzioni del blocco parto dalla prima istruzione del nodo
                    #mi fermo quando arrivo all indirizzo di fine del nodo
                    while(addr < n.endEA):
                        #DecodeInstruict mi crea un oggetto insn_t che ha come campo size la lunghezza dell istruzione 
                        insn = DecodeInstruction(addr)
                        if (insn is None):
                            break
                            
                        #prendo l' istruzione disassemblata
                        disasm = idc.GetDisasm(addr)
                        
                        #concateno alle due stringhe
                        totIstruzioni+="0x%08x"%(addr)+": "+disasm+"\n"
                        
                        # aggiungo size all'indirzzo per andare all istruzione successiva'
                        addr = addr + insn.size
                        
                    #finito il while modifico il contenuto dei nodi
                    G.node[int(str(n.id))]['label'] = totIstruzioni
                
            dizInterno["address"]=functionStart
            dizInterno["istruzioni"]=totI
            dizInterno["grafo"]=json_graph.node_link_data(G)
            
            diz[functionName]=dizInterno
    #scrivo nel txt il json finale e poi chiudo
    text_file.write(json.dumps(diz))
    text_file.close()  
    
except:
    print("ERROR DISASSEMBLING WITH IDA")
idc.Exit(0)