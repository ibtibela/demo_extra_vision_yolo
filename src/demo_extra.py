import cv2
import numpy as np
from ultralytics import YOLO
import os
from gtts import gTTS
import threading
import time
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# Cargamos el detector de caras de OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Para que no se superpongan los avisos
bloqueo_voz = threading.Lock()

alerta_activa = False
ultimo_aviso_time = 0  # Guardamos el momento del último aviso por voz

# 1. Configuración de Voz (Sistema Multihilo)
# Definimos la función en un hilo separado (Thread) para no bloquear el flujo principal.
# Mientras este hilo se encarga de generar el audio y reproducirlo,
# el hilo principal (el bucle 'while True' del video) sigue procesando frames sin detenerse.
def hablar(texto):
    def thread_speech():
        # SI YA ESTÁ HABLANDO, NO HAGAS NADA (ESTO EVITA QUE SE SUPERPONGAN)
        if bloqueo_voz.locked():
            return
            
        with bloqueo_voz: # "Echa la llave" mientras habla
            try:
                tts = gTTS(text=texto, lang='es') # Convierte el texto a voz (Google)
                archivo = "alerta.mp3"            # Define el nombre del archivo de audio
                tts.save(archivo)                 # Guarda la voz generada en el archivo MP3
                os.system(f"mpg123 -q {archivo}") # Reproduce el MP3 por los altavoces
                # Esperamos 1 segundo extra para que respire antes de la siguiente
                import time
                time.sleep(1) 
            except Exception as e:
                print(f"Error en la voz: {e}")

    # Añadimos daemon=True para que el hilo de la voz muera si cerramos el programa
    threading.Thread(target=thread_speech, daemon=True).start()
    
# 2. Configuración de IA (YOLOv8)
# Cargamos el modelo normal (se bajará solo si no está ya descargado)
model = YOLO('yolov8m.pt') 

# 3. Definimos la función para el rectángulo con bordes redondeados
def rectangulo_redondeado(img, pt1, pt2, color, espesor, radio):
    x1, y1 = pt1
    x2, y2 = pt2
    
    # Dibujar los 4 círculos de las esquinas
    cv2.circle(img, (x1 + radio, y1 + radio), radio, color, espesor)
    cv2.circle(img, (x2 - radio, y1 + radio), radio, color, espesor)
    cv2.circle(img, (x1 + radio, y2 - radio), radio, color, espesor)
    cv2.circle(img, (x2 - radio, y2 - radio), radio, color, espesor)
    
    # Dibujar los rectángulos que unen los círculos
    cv2.rectangle(img, (x1 + radio, y1), (x2 - radio, y2), color, espesor)
    cv2.rectangle(img, (x1, y1 + radio), (x2, y2 - radio), color, espesor)

# 4. Configuración de Video
cap = cv2.VideoCapture(0)

AFORO_MAXIMO = 3
limite_cola_max = 2
alerta_activa = False
archivo_log = "registro_aforo.csv"
ultimo_registro_tiempo = 0
intervalo_log = 10  # Registra datos cada 10 segundos

print("--- SISTEMA DE CONTROL DE AFORO INICIADO ---")
print(f"Límite permitido: {AFORO_MAXIMO} personas.")

# Añadir barra deslizante para poder elegir el aforo máximo
# Crear la ventana con un nombre fijo
cv2.namedWindow("Control de Aforo")

# Función necesaria para que funcione la barra (no hace nada)
def nada(x): pass

# Crear la barra (Nombre, Ventana, Valor inicial, Valor máximo, Función)
cv2.createTrackbar("Limite Aforo", "Control de Aforo", AFORO_MAXIMO, 20, nada)
cv2.createTrackbar("Max Cola", "Control de Aforo", limite_cola_max, 10, nada) 

# Variables para la cola
contador_cola = 0
limite_cola_max = 2  # Si hay más de 2 en la mitad derecha, alerta de cola
ultimo_aviso_cola = 0

while True:
    ret, frame = cap.read()
    if not ret: break
    # ACTUALIZAR EL LÍMITE SEGÚN LA BARRA DESLIZANTE
    AFORO_MAXIMO = cv2.getTrackbarPos("Limite Aforo", "Control de Aforo")
    limite_cola_max = cv2.getTrackbarPos("Max Cola", "Control de Aforo")
    # Detección usando gráfica NVIDIA
    results = model(frame, stream=True, device=0, verbose=False)
    
    contador = 0
    contador_cola = 0

    # Calculamos la mitad de la pantalla
    alto, ancho, _ = frame.shape
    mitad_x = ancho // 2    

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            # Solo contamos si la clase detectada es 'person' (ID 0)
            if model.names[cls] == 'person':
                contador += 1
                # Dibujamos el cuadro alrededor de la persona
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Calculamos el centro de la persona para saber en qué zona está
                centro_x = (x1 + x2) // 2
                
                if centro_x > mitad_x:
                    contador_cola += 1
                    color_caja = (0, 165, 255) # Naranja para la cola
                else:
                    color_caja = (255, 0, 0) # Azul para paso normal
                
                # --- NUEVA LÓGICA DE PRIVACIDAD CON HAAR CASCADES ---
                # Cortamos la zona de la persona para buscar la cara dentro
                persona_roi = frame[max(0,y1):y2, max(0,x1):x2]
                
                if persona_roi.size > 0:
                    # Convertimos a gris el recorte para detectar mejor la cara
                    gris_roi = cv2.cvtColor(persona_roi, cv2.COLOR_BGR2GRAY)
                    
                    # Detectamos caras (ajustamos parámetros para evitar falsos positivos)
                    # detectMultiScale(imagen, factor_escala, min_vecinos, tamaño_minimo)
                    caras = face_cascade.detectMultiScale(gris_roi, 1.1, 5, minSize=(30, 30))
                    
                    for (cx, cy, cw, ch) in caras:
                        # Calculamos las coordenadas globales de la cara detectada
                        fx1, fy1 = x1 + cx, y1 + cy
                        fx2, fy2 = fx1 + cw, fy1 + ch
                        
                        # Extraemos el trozo de la cara de la imagen original
                        cara_roi = frame[max(0,fy1):fy2, max(0,fx1):fx2]
                        
                        if cara_roi.size > 0:
                            h, w, _ = cara_roi.shape
                            # Creamos la máscara en forma de elipse
                            # Creamos una imagen negra del mismo tamaño que la cara
                            mask = np.zeros((h, w), dtype=np.uint8)
                            
                            # Dibujamos un óvalo blanco (255) que ocupe todo el recorte
                            centro = (w // 2, h // 2)
                            ejes = (w // 2, h // 2)
                            cv2.ellipse(mask, centro, ejes, 0, 0, 360, 255, -1)
                            
                            # Suavizamos la máscara para que el borde del borroso no sea brusco
                            mask = cv2.GaussianBlur(mask, (21, 21), 11)
                            
                            # 3. Creamos la versión borrosa de la cara
                            cara_borrosa = cv2.GaussianBlur(cara_roi, (99, 99), 30)
                            
                            # 4. Mezclamos (Blending): donde la máscara es blanca, ponemos borroso
                            # Convertimos máscara a escala 0-1
                            mask_norm = mask.astype(float) / 255.0
                            
                            # Aplicamos la mezcla canal por canal (B, G, R)
                            for c in range(3):
                                cara_roi[:, :, c] = (mask_norm * cara_borrosa[:, :, c] + 
                                                   (1.0 - mask_norm) * cara_roi[:, :, c])
                            # 5. Pegamos el resultado en el frame
                            frame[max(0,fy1):fy2, max(0,fx1):fx2] = cara_roi
                                    
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, "Persona", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # --- LOGICA DE COLA ---
    if contador_cola > limite_cola_max:
        estado_cola = "SATURADA"
        color_cola = (0, 0, 255)  # Rojo
    else:
        estado_cola = "FLUIDA"
        color_cola = (0, 255, 0)  # Verde

    # Lógica de Aforo Insistente
    if contador > AFORO_MAXIMO:
        color_texto = (0, 0, 255) # Rojo si hay exceso
        mensaje = "ALERTA: AFORO EXCEDIDO!!"

        ahora = time.time()
        # Si es la primera vez (alerta_activa es False) 
        # O si ya ha pasado el tiempo de espera (10 segundos)
        if not alerta_activa or (ahora - ultimo_aviso_time > 10):
                    if not alerta_activa:
                        hablar("Atención, aforo máximo superado.")
                    else:
                        hablar("El aforo sigue superado, por favor despejen la zona.")
                    
                    ultimo_aviso_time = ahora
                    alerta_activa = True
    else:
        color_texto = (0, 255, 0) # Verde si todo ok
        mensaje = "Aforo Normal"
        alerta_activa = False
        ultimo_aviso_time = 0 # Importante: reseteamos para que la próxima vez sea instantáneo

    # --- PANEL DE CONTROL VISUAL ---
    # Dibujamos una línea divisoria y un suelo sombreado para la "Caja"
    # Línea divisoria
    cv2.line(frame, (mitad_x, 0), (mitad_x, alto), (255, 255, 255), 1)
    
    # Sombreado para la zona de caja (lado derecho)
    overlay = frame.copy()
    cv2.rectangle(overlay, (mitad_x, 0), (ancho, alto), (0, 165, 255), -1)
    cv2.addWeighted(overlay, 0.1, frame, 0.9, 0, frame) # Transparencia al 10%
    
    cv2.putText(frame, "ZONA DE COLA", (mitad_x +100, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
    
    # Dibujamos un rectángulo semi-transparente o negro para el fondo
    # (x1, y1), (x2, y2), color, grosor (-1 es relleno)
    # (imagen, top_left, bottom_right, color, espesor -1 para relleno, radio de curvatura)
    rectangulo_redondeado(frame, (10, 10), (400, 160), (0, 0, 0), -1, 15)

    # Contador de personas (Cambiamos el color según el estado)
    cv2.putText(frame, f"Personas detectadas: {contador}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Estado del Aforo y Límite
    # Usamos 'mensaje' y 'color_texto' que ya se calcularon en la lógica de if/else
    cv2.putText(frame, f"{mensaje} (Max: {AFORO_MAXIMO})", (20, 75), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_texto, 2)
    # Estado de la cola
    cv2.putText(frame, f"Cola Caja: {contador_cola} ({estado_cola} (Max: {limite_cola_max}))", (20, 105), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_cola, 2)

    # Instrucción de uso (en gris pequeñito)
    cv2.putText(frame, "Ajuste el limite del aforo maximo con la barra deslizante", (20, 135), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

    # --- REGISTRO EN EXCEL (LOG) ---
    tiempo_actual = time.time()
    if tiempo_actual - ultimo_registro_tiempo > intervalo_log:
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        estado_aforo = "ALERTA" if contador > AFORO_MAXIMO else "NORMAL"
        
        with open(archivo_log, mode='a', newline='') as f:
            escritor = csv.writer(f)
            if f.tell() == 0:
                # Poner los títulos si el archivo si está vacío
                escritor.writerow(["Fecha y Hora", "N. Personas", "Limite Aforo", "Estado", "Gente en Cola", "Limite Cola"])
            
            # Datos incluyendo el límite que el usuario tiene puesto en la barra
            escritor.writerow([fecha_hora, contador, AFORO_MAXIMO, estado_aforo, contador_cola, limite_cola_max])
            
        ultimo_registro_tiempo = tiempo_actual
    # --- MOSTRAR VENTANA ---
    cv2.imshow("Control de Aforo", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("\n--- GENERANDO REPORTE VISUAL FINAL ---")

try:
    # 1. Cargamos los datos del Excel que ha ido creando el programa
    df = pd.read_csv(archivo_log)
    
    # 2. Convertimos la columna de tiempo a un formato que Python entienda
    df['Fecha y Hora'] = pd.to_datetime(df['Fecha y Hora'])
    
    # 3. Creamos el lienzo de la gráfica
    plt.figure(figsize=(12, 6))
    
    # 4. Dibujamos la línea de personas (Azul) y la del límite (Roja)
    plt.plot(df['Fecha y Hora'], df['N. Personas'], label='Personas Detectadas', color='blue', linewidth=2)
    plt.step(df['Fecha y Hora'], df['Limite Aforo'], label='Límite de Aforo', color='red', linestyle='--', where='post')
    
    # 5. Rellenamos de rojo cuando se supera el aforo para que se vea el "problema"
    plt.fill_between(df['Fecha y Hora'], df['N. Personas'], df['Limite Aforo'], 
                     where=(df['N. Personas'] > df['Limite Aforo']),
                     color='red', alpha=0.3, label='Exceso de Aforo')

    # 6. Estética: Títulos y etiquetas
    plt.title('Reporte de Ocupación', fontsize=16)
    plt.xlabel('Hora del día', fontsize=12)
    plt.ylabel('Número de Personas', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.6)
    
    # Rotamos las fechas para que no se amontonen
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 7. Guardamos el reporte como imagen para que el dueño lo vea luego
    nombre_foto = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(nombre_foto)
    print(f"✅ Reporte guardado con éxito: {nombre_foto}")
    
    # 8. Mostramos la gráfica en una ventana emergente
    plt.show()

except Exception as e:
    print(f"❌ No se pudo generar el reporte: {e}")