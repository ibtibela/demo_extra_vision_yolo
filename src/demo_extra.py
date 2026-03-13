import cv2
from ultralytics import YOLO
import os
from gtts import gTTS
import threading

# Para que no se superpongan los avisos
bloqueo_voz = threading.Lock()
# 1. Configuración de Voz

def hablar(texto):
    def thread_speech():
        # SI YA ESTÁ HABLANDO, NO HAGAS NADA (ESTO EVITA QUE SE SUPERPONGAN)
        if bloqueo_voz.locked():
            return
            
        with bloqueo_voz: # "Echa la llave" mientras habla
            try:
                tts = gTTS(text=texto, lang='es')
                archivo = "alerta.mp3"
                tts.save(archivo)
                os.system(f"mpg123 -q {archivo}")
                # Esperamos 1 segundo extra para que respire antes de la siguiente
                import time
                time.sleep(1) 
            except Exception as e:
                print(f"Error en la voz: {e}")

    # Añadimos daemon=True para que el hilo muera si cierras el programa
    threading.Thread(target=thread_speech, daemon=True).start()# 2. Configuración de IA (YOLOv8)
# Cargamos el modelo normal (se bajará solo si no lo tienes)
model = YOLO('yolov8n.pt') 

# 3. Configuración de Video
cap = cv2.VideoCapture(0)

AFORO_MAXIMO = 3  # Cambia este número según necesites
alerta_activa = False

print("--- SISTEMA DE CONTROL DE AFORO INICIADO ---")
print(f"Límite permitido: {AFORO_MAXIMO} personas.")

while True:
    ret, frame = cap.read()
    if not ret: break

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
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, "Persona", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Lógica de Aforo
    if contador > AFORO_MAXIMO:
        color_texto = (0, 0, 255) # Rojo si hay exceso
        mensaje = "¡ALERTA: AFORO EXCEDIDO!"
        if not alerta_activa:
            hablar("Atención, aforo máximo superado.")
            alerta_activa = True
    else:
        color_texto = (0, 255, 0) # Verde si todo ok
        mensaje = "Aforo Normal"
        alerta_activa = False

    # Dibujar información en pantalla
    cv2.putText(frame, f"Personas: {contador} / {AFORO_MAXIMO}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, color_texto, 2)
    cv2.putText(frame, mensaje, (20, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, color_texto, 2)

    cv2.imshow("Control de Aforo", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()