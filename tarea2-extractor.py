import sys
import os.path

if len(sys.argv) < 3:
    print("Uso: {} [carpeta_entrada_videos] [carpeta_salida_descriptores]".format(sys.argv[0]))
    sys.exit(1)

carpeta_entrada_videos = sys.argv[1]
carpeta_salida_descriptores = sys.argv[2]

print("calculando descriptores y guardandolos en {} ...".format(carpeta_salida_descriptores))

if not os.path.isdir(carpeta_entrada_videos):
    print(" no existe directorio {}!".format(carpeta_entrada_videos))
    sys.exit(1)

#procesar todos los archivos de carpeta_entrada_videos que terminen en: mp4 avi mpg wav mp3
#para cada archivo:
#  extraer la pista de audio con el commando ffmpeg
#  dividir el audio en N segmentos de tiempo
#  calcular una matriz de descriptores de N filas por d columnas (d=dimension del descriptor)
#  crear directorio: os.mkdir(carpeta_salida_descriptores)
#  escribir matriz descriptores en carpeta_salida_descriptores/archivo

