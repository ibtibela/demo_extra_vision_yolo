# 🛡️ Sistema de Control de Aforo con IA

Este proyecto implementa un sistema de visión artificial en tiempo real para el conteo de personas y la gestión de aforos. El sistema utiliza IA para detectar presencia humana y emite alertas por voz de forma inteligente cuando se supera el límite de seguridad.

## 🌟 Características principales
- **Detección en tiempo real:** Utiliza el modelo **YOLOv8** de Ultralytics.
- **Aceleración por GPU:** Optimizado para la tarjeta gráfica **NVIDIA GeForce RTX 4050** mediante núcleos CUDA.
- **Control Dinámico:** Incluye una barra deslizante (*Trackbar*) para ajustar el límite de aforo sin detener el programa.
- **Alertas de Voz Inteligentes:** Emite un aviso por voz inmediato al detectar el aforo excedido; si tras un tiempo la situación persiste, el sistema lanza recordatorios periódicos para asegurar el cumplimiento de la norma.
- **Multihilo (Threading):** Implementado para separar la lógica de visión artificial de la de audio. Esto garantiza que la tasa de FPS se mantenga constante aunque el sistema esté emitiendo alertas sonoras.

## 🛠️ Requisitos e Instalación

### 1. Sistema Operativo y Audio
Este sistema está diseñado para **Ubuntu / Linux**. Para la reproducción de alertas de voz, es necesario instalar el motor de audio externo:
```bash
sudo apt update && sudo apt install mpg123 -y