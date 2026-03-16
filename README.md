# 🛡️ Sistema de Control de Aforo con IA

Este proyecto implementa un sistema de visión artificial en tiempo real para el conteo de personas y la gestión de aforos. El sistema utiliza IA para detectar presencia humana y emite alertas por voz de forma inteligente cuando se supera el límite de seguridad.

## 🌟 Características principales
- **Detección en tiempo real:** Utiliza el modelo **YOLOv8** de Ultralytics.
- **Aceleración por GPU:** Optimizado para la tarjeta gráfica **NVIDIA GeForce RTX 4050** mediante núcleos CUDA.
- **Control Dinámico:** Incluye barras deslizantes (*Trackbars*) para ajustar tanto el límite de aforo como el de la cola sin detener el programa.
- **Alertas de Voz Inteligentes:** Emite un aviso por voz inmediato al detectar el aforo excedido; si tras un tiempo la situación persiste, el sistema lanza recordatorios periódicos para asegurar el cumplimiento de la norma.
- **Multihilo (Threading):** Implementado para separar la lógica de visión artificial de la de audio. Esto garantiza que la tasa de FPS se mantenga constante aunque el sistema esté emitiendo alertas sonoras.
* **Privacidad Proactiva:** Difuminado elíptico de rostros para anonimización.
- **Gestión de Colas en Caja:** El sistema detecta cuánta gente hay esperando para pagar y avisa visualmente si la cola es demasiado larga.
- **Analítica de Negocio:** Genera gráficas automáticas y registros en Excel (CSV) con el historial de ocupación y colas.

## 🚀 ¿Por qué esto ayuda a vender más?
* **Evita colas desesperantes:** La gran mayoría de los clientes se va si ve una cola muy larga. Este sistema te avisa antes de que pierdas la venta.
* **Optimiza tus turnos:** Con los datos del Excel, puedes ver qué horas son las más críticas y poner a tus empleados solo cuando realmente hace falta, ahorrando dinero.
* **Privacidad y Confianza:** Al emborronar las caras, cumples con la ley (GDPR) y tus clientes se sienten más cómodos comprando.

## 📊 Decisiones rápidas con Gráficas Visuales
Al cerrar el programa, el sistema genera una **gráfica comparativa** que permite al dueño tomar decisiones de un vistazo:

* **Aforo vs Cola:** Compara cuánta gente hay paseando frente a cuánta hay en caja. Si hay mucha gente en tienda pero poca en cola, tus promociones funcionan. Si la cola siempre está llena, necesitas otro cajero.
* **Detección de "Horas Críticas":** Mira de un golpe en qué momentos del día se superaron los límites para reforzar el equipo en el momento justo.

## 🛠️ Requisitos e Instalación

### 1. Sistema Operativo y Audio
Este sistema está diseñado para **Ubuntu / Linux**. Para la reproducción de alertas de voz, es necesario instalar el motor de audio externo:
```bash
sudo apt update && sudo apt install mpg123 -y
```
