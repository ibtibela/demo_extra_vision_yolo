# 🛡️ MSI Sentinel: Sistema de Control de Aforo con IA

Este proyecto implementa un sistema de visión artificial en tiempo real para el conteo de personas y la gestión de aforos. El sistema emite alertas por voz de forma automática cuando se supera el límite de seguridad establecido.

## 🌟 Características principales
- **Detección en tiempo real:** Utiliza el modelo **YOLOv8** de Ultralytics.
- **Aceleración por GPU:** Optimizado para la tarjeta gráfica **NVIDIA GeForce RTX 4050** (MSI Thin GF63).
- **Alertas Auditivas:** Integración con sistemas de síntesis de voz para avisos de seguridad.
- **Contador Dinámico:** Visualización en pantalla del número de personas detectadas frente al límite permitido.

> ⚠️ **NOTA SOBRE EL AUDIO**: Esta versión utiliza **gTTS (Google Text-to-Speech)** para una voz más humana. 
> * **Requisito:** Requiere conexión a Internet para generar los archivos de voz.
> * **Modo Offline:** Si se desea usar sin conexión, se debe revertir a la librería `pyttsx3` o utilizar archivos de audio (.mp3) previamente grabados.

## 🛠️ Requisitos e Instalación

### 1. Entorno de Python
Se recomienda el uso de Conda para gestionar las dependencias:
```bash
conda activate vision_nvidia
pip install -r requirements.txt