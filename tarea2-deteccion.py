import sys
import os.path

if len(sys.argv) < 3:
    print("Uso: {} [archivo_similares] [archivo_detecciones]".format(sys.argv[0]))
    sys.exit(1)

archivo_similares = sys.argv[1]
archivo_detecciones = sys.argv[2]

print("detectando apariciones de comerciales y guardandolos en {} ...".format(archivo_detecciones))

if not os.path.isfile(archivo_similares):
    print(" no existe {}!".format(archivo_similares))
    sys.exit(1)

#leer datos en archivo_similares
#buscar secuencias de un mismo video con un mismo offset
#escribir los comerciales detectados en archivo_detecciones
