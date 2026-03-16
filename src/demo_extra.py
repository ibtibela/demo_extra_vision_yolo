import cv2
from ultralytics import YOLO
import os
from gtts import gTTS
import threading
import time

# Cargamos el detector de caras de OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')# Para que no se superpongan los avisos

bloqueo_voz = threading.Lock()

alerta_activa = False
ultimo_aviso_time = 0  # Guardamos el momento del último grito

# 1. Configuración de Voz
# Usamos Threading (multihilo) para que el proceso de generar y reproducir 
# la voz corra en paralelo. Así evitamos que el video se detenga mientras se habla.
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
model = YOLO('yolov8n.pt') 

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
alerta_activa = False

print("--- SISTEMA DE CONTROL DE AFORO INICIADO ---")
print(f"Límite permitido: {AFORO_MAXIMO} personas.")

# Añadir barra deslizante para poder elegir el aforo máximo
# Crear la ventana con un nombre fijo
cv2.namedWindow("Control de Aforo")

# Función necesaria para que funcione la barra (no hace nada)
def nada(x): pass

# Crear la barra (Nombre, Ventana, Valor inicial, Valor máximo, Función)
cv2.createTrackbar("Limite Aforo", "Control de Aforo", AFORO_MAXIMO, 20, nada)

while True:
    ret, frame = cap.read()
    if not ret: break
    # ACTUALIZAR EL LÍMITE SEGÚN LA BARRA DESLIZANTE
    AFORO_MAXIMO = cv2.getTrackbarPos("Limite Aforo", "Control de Aforo")
    # Detección usando gráfica NVIDIA
    results = model(frame, stream=True, device=0, verbose=False)
    
    contador = 0
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            # Solo contamos si la clase detectada es 'person' (ID 0)
            if model.names[cls] == 'person':
                contador += 1
                # Dibujamos el cuadro alrededor de la persona
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # --- NUEVA LÓGICA DE PRIVACIDAD CON HAAR CASCADES ---
                # Cortamos la zona de la persona para buscar la cara dentro
                persona_roi = frame[max(0,y1):y2, max(0,x1):x2]
                
                if persona_roi.size > 0:
                    # Convertimos a gris el recorte para detectar mejor la cara
                    gris_roi = cv2.cvtColor(persona_roi, cv2.COLOR_BGR2GRAY)
                    
                    # Detectamos caras (ajustamos parámetros para evitar falsos positivos)
                    caras = face_cascade.detectMultiScale(gris_roi, 1.1, 5, minSize=(30, 30))
                    
                    for (cx, cy, cw, ch) in caras:
                        # Calculamos las coordenadas globales de la cara detectada
                        fx1, fy1 = x1 + cx, y1 + cy
                        fx2, fy2 = fx1 + cw, fy1 + ch
                        
                        # Extraemos el trozo de la cara de la imagen original
                        cara_img = frame[max(0,fy1):fy2, max(0,fx1):fx2]
                        
                        if cara_img.size > 0:
                            # Aplicamos el emborronado
                            frame[max(0,fy1):fy2, max(0,fx1):fx2] = cv2.GaussianBlur(cara_img, (99, 99), 30)
                                    
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, "Persona", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

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
    # Dibujamos un rectángulo semi-transparente o negro para el fondo
    # (x1, y1), (x2, y2), color, grosor (-1 es relleno)
    # (imagen, top_left, bottom_right, color, espesor -1 para relleno, radio de curvatura)
    rectangulo_redondeado(frame, (10, 10), (380, 115), (0, 0, 0), -1, 15)

    # 2. Contador de personas (Cambiamos el color según el estado)
    cv2.putText(frame, f"Personas detectadas: {contador}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # 4. Estado del Aforo y Límite
    # Usamos 'mensaje' y 'color_texto' que ya se calcularon en la lógica de if/else
    cv2.putText(frame, f"{mensaje} (Max: {AFORO_MAXIMO})", (20, 75), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_texto, 2)

    # 5. Instrucción de uso (en gris pequeñito)
    cv2.putText(frame, "Ajuste el limite con la barra deslizante", (20, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

    # --- MOSTRAR VENTANA ---
    cv2.imshow("Control de Aforo", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()