import cv2
from ultralytics import YOLO
import pyttsx3
import threading

# 1. Configuración de Voz
engine = pyttsx3.init()
# Forzamos la voz ID 26 que es la de España
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[26].id)
# Bajamos un poco la velocidad para que se entienda perfecto
engine.setProperty('rate', 145)

def hablar(texto):
    def thread_speech():
        # En Linux, a veces es mejor re-inicializar dentro del hilo para evitar bloqueos
        local_engine = pyttsx3.init()
        local_engine.setProperty('voice', local_engine.getProperty('voices')[26].id)
        local_engine.setProperty('rate', 145)
        local_engine.say(texto)
        local_engine.runAndWait()
    threading.Thread(target=thread_speech).start()

# 2. Configuración de IA (YOLOv8)
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

    # Detección usando tu gráfica NVIDIA
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

    cv2.imshow("MSI Sentinel - Control de Aforo", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
voices = engine.getProperty('voices')
for i, v in enumerate(voices):
    print(f"{i}: {v.name} - {v.languages}")
cap.release()
cv2.destroyAllWindows()