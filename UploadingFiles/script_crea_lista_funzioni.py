from idautils import *
from idaapi import *
import os
import binascii
import json

try: 
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
            
            startA=funcea
            totI=""
            totH=""
            
            #json interno composto da address label e asm
            dizInterno={}
            
            for (startea, endea) in Chunks(funcea):
                for head in Heads(startea, endea):
                    insn = DecodeInstruction(head)
                    byte = get_bytes(head, insn.size)
                    
                    totI+=GetDisasm(head)
                    totH+=str(binascii.hexlify(byte))
                
            dizInterno["address"]=startA
            dizInterno["label"]=totI
            dizInterno["asm"]=totH
            
            #salvo il dizionario interno
            diz[functionName]=dizInterno
              
    #scrivo nel txt il json finale e poi chiudo
    text_file.write(json.dumps(diz))     
    text_file.close()  
    
except:
    print("ERROR DISASSEMBLING WITH IDA")
idc.Exit(0)