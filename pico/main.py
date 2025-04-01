from mfrc522 import MFRC522
import _thread
import utime
import json
import machine
LED = machine.Pin(25,machine.Pin.OUT)
rojo = machine.Pin(16,machine.Pin.OUT)
verde = machine.Pin(17,machine.Pin.OUT)
puerta = machine.Pin(15,machine.Pin.OUT)

#####	PARÁMETROS	#####

reader = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=0)
global limite
limite=10
tiempo_puerta=1
tiempo_entre_comprobaciones=1
tarjeta_maestra="[0x72, 0x58, 0x61, 0x51]"

#####	FUNCIONES	#####
def encender(elemento):
    elemento.value(1)
def apagar(elemento):
    elemento.value(0)
    
def parpadeo(elemento):
    
    for i in range(5):
        elemento.value(1)
        utime.sleep_ms(100) 
        elemento.value(0)
        utime.sleep_ms(100)
        
def liberar_taquilla():
    data={'ocupada': False, 
              'tarjeta' :"",
                   "fecha_inicio":0}
    g=open("archivo", "w")
    g.write(json.dumps(data))
    g.close()
    apagar(rojo)
    encender(verde)
    encender(puerta)
    utime.sleep(tiempo_puerta)
    apagar(puerta)
def ocupar_taquilla(tarjeta_leida):
    data={'ocupada': True, 
              'tarjeta' :tarjeta_leida,
                   "fecha_inicio":utime.time()}
    g=open("archivo", "w")
    g.write(json.dumps(data))
    g.close()
    encender(puerta)
    utime.sleep(tiempo_puerta)
    apagar(puerta)
    apagar(verde)
    encender(rojo)
    
    
def comprobar_tiempo_uso():
    global limite
    while True:
        g=open("archivo", "r")
        data=json.load(g)
        g.close()
        ocupada=data['ocupada']
        tarjeta_guardada=data['tarjeta']
        fecha_inicio=data['fecha_inicio']
        ahora=utime.time()
        if ahora-fecha_inicio>limite and fecha_inicio!=0:
            print("tiempo excedido")
            data={'ocupada': False, 
              'tarjeta' :"",
                   "fecha_inicio":0}
            g=open("archivo", "w")
            g.write(json.dumps(data))
            g.close()
            for i in range(5):
                encender(verde)
                utime.sleep(0.1)
                apagar(verde)
                utime.sleep(0.1)
                encender(puerta)
                utime.sleep(0.1)
                apagar(puerta)
                encender(verde)
        
        utime.sleep(tiempo_entre_comprobaciones)
        

#####	INICIA UN PARPADEO PARA PODER IDENTIFICAR QUE EL PROGRAMA ESTÁ EN MARCHA	#####
#_thread.start_new_thread(parpadeo, ())
        
##### COMPRUEBA SI EXISTE EL ARCHIVO DE PERSISTENCIA	#####
try:
    g=open("archivo", "r")
    data=json.load(g)
    
    g.close()
#####	SI EL ARCHIVO NO EXISTE, LO CREA Y LO PUEBLA	#####
except:
    f=open("archivo", "w")
    diccionario= {'ocupada': False, 
              'tarjeta' :"",
                   "fecha_inicio":0} 
    f.write(json.dumps(diccionario))
    f.close()
#####	ABRE LA PERSISTENCIA Y CARGA LOS VALORES DE LAS VARIABLES	#####
# g=open("archivo", "r")
# data=json.load(g)
# ocupada=data['ocupada']
# tarjeta_guardada=data['tarjeta']
# fecha_inicio=data['fecha_inicio']
# print(ocupada, tarjeta_guardada, fecha_inicio)
# 
# g.close()

#####	INICIA LOOP QUE COMPRUEBA QUE NO SE HAYA EXCEDIDO EL TIEMPO DE USO	#####
#_thread.start_new_thread(comprobar_tiempo_uso, ())



#####	INICIA EL LOOP DE LECTURA Y COMPROBACIÓN DE TARJETAS	#####
g=open("archivo", "r")
data=json.load(g)
ocupada=data['ocupada']
tarjeta_guardada=data['tarjeta']

if tarjeta_guardada=="":
    encender(verde)
    apagar(rojo)
else:
    encender(rojo)
    apagar(verde)
g.close()
print("Acerque su tarjeta\n")

while True:
    g=open("archivo", "r")
    data=json.load(g)
    ocupada=data['ocupada']
    tarjeta_guardada=data['tarjeta']
    
    print("Tarjeta guardada: ", tarjeta_guardada)
   
    fecha_inicio=data['fecha_inicio']
    print(ocupada, tarjeta_guardada, fecha_inicio)
    g.close()
    reader.init()
    
    (stat, tag_type) = reader.request(reader.REQIDL)
    if stat == reader.OK:
        (stat, uid) = reader.SelectTagSN()
        #print(type(uid))
        tarjeta_leida=reader.tohexstring(uid)
        #print(type(tarjeta_leida))
        

#####	ABRO CON LA LLAVE MAESTRA	#####
        if tarjeta_leida == tarjeta_maestra:
            print("LLAVE MAESTRA")
            liberar_taquilla()
#####	ABRO CON LA MISMA TARJETA	#####
        if tarjeta_leida == tarjeta_guardada:
            print("coincide")
            liberar_taquilla()
                      
#####	TAQUILLA DISPONIBLE	#####
        elif tarjeta_guardada=="":
            print("Disponible, adjudicando")
            ocupar_taquilla(tarjeta_leida)

#####	INTENTO ABRIR LA TAQUILLA OCUPADA CON OTRA TARJETA	#####
        else:
            print("ocupada por otra tarjeta")
            parpadeo(rojo)
            encender(rojo)
        if stat == reader.OK:
            print("The card details are as follows")
            card = reader.tohexstring(uid)
            #print(tarjeta_leida)
            
            print(card)
            
            
    else:
        tarjeta_guardada=[0]
    utime.sleep_ms(500)  
# while True:
    
#     g=open("archivo", "r")
#     data=json.load(g)
#     ocupada=data['ocupada']
#     tarjeta_guardada=data['tarjeta']
#     fecha_inicio=data['fecha_inicio']
#     print(ocupada, tarjeta_guardada, fecha_inicio)
# 
#     g.close()
#     
#     data={'ocupada': False, 
#               'tarjeta' :"",
#                    "fecha_inicio":utime.time()}
#     print(ocupada, tarjeta_guardada, fecha_inicio)
#     g=open("archivo", "w")
#     g.write(json.dumps(data))
#     g.close()
#     utime.sleep(30)
    
    
