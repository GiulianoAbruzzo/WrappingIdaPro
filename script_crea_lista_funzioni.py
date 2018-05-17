from idautils import *
from idaapi import *
import os
import binascii
import json

#crea il file
text_file = open("ListaFunzioni_"+idaapi.get_root_filename()+".txt", "w")

#aspetta il caricamento
idaapi.autoWait()

#json di tutte le funzioni
diz={}

#apri il database
for segea in Segments():
        for funcea in Functions(segea, SegEnd(segea)):
                functionName = GetFunctionName(funcea)
                
                #non sono sicuro che il funcea rappresenta l'indirizzo di start della funzione
                startA=funcea
                totI=""
                totH=""
                
                #json interno composto da address label e asm
                dizInterno={}
                
                for (startea, endea) in Chunks(funcea):
                        for head in Heads(startea, endea):
                                insn = DecodeInstruction(head)
                                byte = get_bytes(head, insn.size)
                                
                                #ho evitato di mettere "/n" o " " poi dimmi tu come vuoi
                                totI+=GetDisasm(head)
                                totH+=str(binascii.hexlify(byte))
                        
                dizInterno["address"]=startA
                dizInterno["label"]=totI
                dizInterno["asm"]=totH
                json_data = json.dumps(dizInterno)
                
                #salvo il dizionario interno
                diz[functionName]=json_data
              
#scrivo nel txt il json finale
text_file.write(json.dumps(diz)) 

#chiudi il file	e termina	        
text_file.close()
idc.Exit(0)