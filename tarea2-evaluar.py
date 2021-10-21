import sys
import os.path


class Deteccion:
    def __init__(self, id_deteccion, television, desde, largo, comercial, score):
        self.id_deteccion = id_deteccion 
        self.television = television
        self.desde = desde
        self.largo = largo
        self.comercial = comercial
        self.score = score

    def interseccion(self, otra):
        if self.television != otra.television or self.comercial != otra.comercial:
            return 0
        ini1 = self.desde
        end1 = self.desde + self.largo
        ini2 = otra.desde
        end2 = otra.desde + otra.largo
        inter = min(end1, end2) - max(ini1, ini2)
        union = max(end1, end2) - min(ini1, ini2)
        if inter <= 0 or union <= 0:
            return 0
        return inter / union


def get_filename(filepath):
    name = filepath.lower().strip()
    if name.rfind('/') >= 0:
        name = name[name.rfind('/') + 1:]
    if name.rfind('\\') >= 0:
        name = name[name.rfind('\\') + 1:]
    return name


def parsear_gt(id_deteccion, archivo_origen, linea):
    linea = linea.rstrip("\r\n")
    # se ignoran lineas vacias o comentarios
    if linea == "" or linea.startswith("#"):
        return None
    partes = linea.split("\t")
    if len(partes) != 5:
        raise Exception("archivo " + archivo_origen +" incorrecto")
    tipo = partes[0]
    television = get_filename(partes[1])
    comercial = get_filename(partes[4])
    desde = round(float(partes[2]), 3)
    largo = round(float(partes[3]), 3)
    det = Deteccion(id_deteccion, television, desde, largo, comercial, 0)
    return det


def parsear_deteccion(id_deteccion, archivo_origen, linea):
    linea = linea.rstrip("\r\n")
    # se ignoran lineas vacias o comentarios
    if linea == "" or linea.startswith("#"):
        return None
    partes = linea.split("\t")
    if len(partes) != 5:
        raise Exception(
            archivo_origen + " incorrecto numero de columnas (se esperan 5 columnas separadas por un tabulador)")
    # nombre de video (sin ruta)
    television = get_filename(partes[0])
    if television == "":
        raise Exception("nombre television invalido en " + archivo_origen)
    # nombre de comercial (sin ruta)
    comercial = get_filename(partes[3])
    if comercial == "":
        raise Exception("nombre comercial invalido en " + archivo_origen)
    # los tiempos pueden incluir milisegundos
    desde = round(float(partes[1]), 3)
    if desde < 0:
        raise Exception("valor incorrecto desde={} en {}".format(desde, archivo_origen))
    largo = round(float(partes[2]), 3)
    if largo <= 0:
        raise Exception("valor incorrecto largo={} en {}".format(largo, archivo_origen))
    # el score
    score = float(partes[4])
    if score <= 0:
        raise Exception("valor incorrecto score={} en {}".format(score, archivo_origen))
    det = Deteccion(id_deteccion, television, desde, largo, comercial, score)
    return det


def leer_gt(lista, filename):
    if not os.path.isfile(filename):
        if filename == "":
            return
        raise Exception("no existe el archivo {}".format(filename))
    cont_lineas = 0
    cont_detecciones = 0
    with open(filename) as f:
        for linea in f:
            cont_lineas += 1
            try:
                # el id es su posición en la lista
                det = parsear_gt(len(lista), filename, linea)
                if det is not None:
                    lista.append(det)
                    cont_detecciones += 1
            except Exception as ex:
                print("Error {} (linea {}): {}".format(filename, cont_lineas, ex))
    print("{} detecciones en archivo {}".format(cont_detecciones, filename))


def leer_detecciones(lista, filename):
    if not os.path.isfile(filename):
        if filename == "":
            return
        raise Exception("no existe el archivo {}".format(filename))
    cont_lineas = 0
    cont_detecciones = 0
    with open(filename) as f:
        for linea in f:
            cont_lineas += 1
            try:
                # el id es su posición en la lista
                det = parsear_deteccion(len(lista), filename, linea)
                if det is not None:
                    lista.append(det)
                    cont_detecciones += 1
            except Exception as ex:
                print("Error {} (linea {}): {}".format(filename, cont_lineas, ex))
    print("{} detecciones en archivo {}".format(cont_detecciones, filename))


class ResultadoDeteccion:
    def __init__(self, deteccion):
        self.deteccion = deteccion
        self.es_incorrecta = False
        self.es_duplicada = False
        self.es_correcta = False
        self.gt = None
        self.iou = 0


class Metricas:
    def __init__(self, threshold):
        self.threshold = threshold
        self.total_gt = 0
        self.total_detecciones = 0
        self.correctas = 0
        self.incorrectas = 0
        self.recall = 0
        self.precision = 0
        self.f1 = 0
        self.iou = 0


class Evaluacion:
    def __init__(self):
        self.detecciones_gt = list()
        self.detecciones = list()
        self.resultado_por_deteccion = list()
        self.resultado_global = None

    def leer_archivo_gt(self, file_gt):
        # cargar el ground-truth
        leer_gt(self.detecciones_gt, file_gt)

    def leer_archivo_detecciones(self, file_detecciones):
        # cargar las detecciones
        leer_detecciones(self.detecciones, file_detecciones)

    def evaluar_cada_deteccion(self):
        # ordenar detecciones por score de mayor a menor
        self.detecciones.sort(key=lambda x: x.score, reverse=True)
        # para descartar las detecciones duplicadas
        ids_encontradas = set()
        # revisar cada deteccion
        for det in self.detecciones:
            # evaluar cada deteccion si es correcta a no
            gt_encontrada, iou = self.buscar_deteccion_en_gt(det)
            # retorna resultado
            res = ResultadoDeteccion(det)
            if gt_encontrada is None:
                res.es_incorrecta = True
            elif gt_encontrada.id_deteccion in ids_encontradas:
                res.es_duplicada = True
            else:
                res.es_correcta = True
                res.gt = gt_encontrada
                res.iou = iou
                ids_encontradas.add(gt_encontrada.id_deteccion)
            self.resultado_por_deteccion.append(res)
        # ordenar los resultados como el archivo de entrada
        self.resultado_por_deteccion.sort(key=lambda x: x.deteccion.id_deteccion)

    def buscar_deteccion_en_gt(self, deteccion):
        gt_encontrada = None
        iou = 0
        # busca en gt la deteccion que tiene mayor interseccion
        for det_gt in self.detecciones_gt:
            interseccion = deteccion.interseccion(det_gt)
            if interseccion > iou:
                gt_encontrada = det_gt
                iou = interseccion
        return gt_encontrada, iou

    def calcular_metricas(self):
        # todos los umbrales posibles
        all_scores = set()
        for res in self.resultado_por_deteccion:
            if res.es_correcta:
                all_scores.add(res.deteccion.score)
        all_scores.add(0)
        # calcular las metricas para cada score y seleccionar el mejor
        for score in sorted(list(all_scores), reverse=True):
            met = self.evaluar_con_threshold(score)
            if self.resultado_global is None or met.f1 > self.resultado_global.f1:
                self.resultado_global = met

    def evaluar_con_threshold(self, score_threshold):
        met = Metricas(score_threshold)
        met.total_gt = len(self.detecciones_gt)
        suma_iou = 0
        for res in self.resultado_por_deteccion:
            # ignorar detecciones con score bajo el umbral
            if res.deteccion.score < score_threshold:
                continue
            met.total_detecciones += 1
            if res.es_correcta:
                met.correctas += 1
                suma_iou += res.iou
            if res.es_incorrecta or res.es_duplicada:
                met.incorrectas += 1
        if met.correctas > 0:
            met.recall = met.correctas / met.total_gt
            met.precision = met.correctas / met.total_detecciones
        if met.precision > 0 and met.recall > 0:
            met.f1 = (2 * met.precision * met.recall) / (met.precision + met.recall)
        if met.correctas > 0:
            met.iou = suma_iou / met.correctas
        return met

    def imprimir_resultado_por_deteccion(self):
        if len(self.resultado_por_deteccion) == 0:
            return
        print("Resultado detallado de cada una de las {} detecciones:".format(len(self.resultado_por_deteccion)))
        for res in self.resultado_por_deteccion:
            s1 = ""
            s2 = ""
            if res.es_correcta:
                s1 = "   OK)"
                s2 = " //IoU={:.1%} gt=({} {})".format(res.iou, res.gt.desde, res.gt.largo)
            elif res.es_duplicada:
                s1 = "dup--)"
            elif res.es_incorrecta:
                s1 = "   --)"
            d = res.deteccion
            print(" {} {} {} {} {} {} {}".format(s1, d.television, d.desde, d.largo, d.comercial, d.score, s2))

    def imprimir_resultado_global(self):
        if self.resultado_global is None:
            return
        m = self.resultado_global
        print("Resultado global:")
        print(" {} detecciones en GT, {} detecciones a evaluar".format(m.total_gt, len(self.resultado_por_deteccion)))
        print(" Al usar un score umbral={} se seleccionan {} detecciones con:".format(m.threshold, m.total_detecciones))
        print("    {} detecciones correctas, {} detecciones incorrectas".format(m.correctas, m.incorrectas))
        print("    Precision={:.3f} ({}/{})  Recall={:.3f} ({}/{})".format(m.precision, m.correctas,
                                                                           m.total_detecciones, m.recall, m.correctas,
                                                                           m.total_gt))
        print("    F1={:.3f}  IoU promedio={:.1%}".format(m.f1, m.iou))
        print()
        nota = 1 + 6 * ponderar(m.f1, 0.7, m.iou, 0.1)
        print("==> Nota resultados = {:.2f}   (pondera 60% en nota final de la tarea)".format(nota))
        if nota >= 7:
            bonus = ponderar(m.f1 - 0.7, 0.3, m.iou - 0.1, 0.7)
            print("==> Bonus = {:.2f} puntos para otra tarea o mini-control".format(bonus))

        if m.total_gt == 0 and len(self.resultado_por_deteccion) > 0:
            print()
            print("¿archivo GT incorrecto?")
            return


def ponderar(valor_f1, max_f1, valor_iou, max_iou):
    nota_f1 = max(0, min(1, valor_f1 / max_f1))
    nota_iou = max(0, min(1, valor_iou / max_iou))
    return nota_f1 * 0.8 + nota_iou * 0.2


def main():
    if len(sys.argv) < 3:
        print("CC5213 - Evaluación Tarea 2  (2021-2)")
        print("Uso: {} [file_gt] [file_detecciones]".format(sys.argv[0]))
        sys.exit(1)

    file_gt = sys.argv[1] if len(sys.argv) > 1 else ""
    file_detecciones = sys.argv[2] if len(sys.argv) > 2 else ""

    if not os.path.isfile(file_gt):
        print("no encuentro GT: {} !".format(file_gt))
        sys.exit(1)
    elif not os.path.isfile(file_detecciones):
        print("no hay detecciones para evaluar en {} !".format(file_detecciones))
        sys.exit(1)

    print("Evaluando detecciones")
    ev = Evaluacion()
    ev.leer_archivo_gt(file_gt)
    ev.leer_archivo_detecciones(file_detecciones)
    ev.evaluar_cada_deteccion()
    ev.calcular_metricas()
    ev.imprimir_resultado_por_deteccion()
    ev.imprimir_resultado_global()


# método main
if __name__ == "__main__":
    main()
