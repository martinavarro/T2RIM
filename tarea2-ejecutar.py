import sys
import os.path
import subprocess


def run_command(comando):
    print()
    print("---------")
    print("INICIANDO COMANDO:")
    print("  {}".format(" ".join(comando)))
    print()
    code = subprocess.call(comando)
    print()
    if code != 0:
        print("ERROR EN EL COMANDO!")
        print("(fin de la tarea)")
        sys.exit()


def evaluar_resultados(file_gt, file_detecciones):
    comando = ["python", "tarea2-evaluar.py", file_gt, file_detecciones]
    run_command(comando)


def ejecutar_comandos(dataset_dir):
    # ruta del dataset
    carpeta_videos_comerciales = "{}/comerciales".format(dataset_dir)
    carpeta_videos_television = "{}/television".format(dataset_dir)

    # validar las rutas del dataset
    if not os.path.isdir(carpeta_videos_comerciales) or not os.path.isdir(carpeta_videos_television):
        print("ruta {} no contiene un dataset".format(dataset_dir))
        return None

    # carpetas y archivo a crear durante la ejecución
    carpeta_descriptores_tv = "work_{}_tv".format(dataset_dir)
    carpeta_descriptores_com = "work_{}_com".format(dataset_dir)
    archivo_similares = "work_{}_similares".format(dataset_dir)
    archivo_detecciones = "work_{}_detecciones.txt".format(dataset_dir)

    # comandos a ejecutar
    comandos = []

    # tareas en python
    comandos.append(["python", "tarea2-extractor.py", carpeta_videos_comerciales, carpeta_descriptores_com])
    comandos.append(["python", "tarea2-extractor.py", carpeta_videos_television, carpeta_descriptores_tv])
    comandos.append(["python", "tarea2-busqueda.py", carpeta_descriptores_tv, carpeta_descriptores_com, archivo_similares])
    comandos.append(["python", "tarea2-deteccion.py", archivo_similares, archivo_detecciones])

    # tareas en c++
    # comandos.append(["./tarea2-extractor", carpeta_videos_comerciales, carpeta_descriptores_com])
    # comandos.append(["./tarea2-extractor", carpeta_videos_television, carpeta_descriptores_tv])
    # comandos.append(["./tarea2-busqueda", carpeta_descriptores_tv, carpeta_descriptores_com, archivo_similares])
    # comandos.append(["./tarea2-deteccion", archivo_similares, archivo_detecciones])

    # tareas en java
    # comandos.append(["java", "Tarea2Extractor", carpeta_videos_comerciales, carpeta_descriptores_com])
    # comandos.append(["java", "Tarea2Extractor", carpeta_videos_television, carpeta_descriptores_tv])
    # comandos.append(["java", "Tarea2Busqueda", carpeta_descriptores_tv, carpeta_descriptores_com, archivo_similares])
    # comandos.append(["java", "Tarea2Deteccion", archivo_similares, archivo_detecciones])

    # ejecutar todos los comandos
    for comando in comandos:
        run_command(comando)

    # retonar el archivo con las detecciones
    return archivo_detecciones


def main():
    print("CC5213 - EJECUTAR TAREA 2 (2021-2)")
    datasets = ["dataset_a", "dataset_b", "dataset_c"]
    for dataset_dir in datasets:
        archivo_detecciones = ejecutar_comandos(dataset_dir)
        file_gt = "{}/gt.txt".format(dataset_dir)
        evaluar_resultados(file_gt, archivo_detecciones)


# método main
if __name__ == "__main__":
    main()
