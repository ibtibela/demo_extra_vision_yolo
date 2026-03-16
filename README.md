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

## 📊 Analítica Inteligente: Tu negocio en un vistazo
Al cerrar el programa, el sistema genera automáticamente una **gráfica comparativa de alta precisión**. Ya no tienes que adivinar qué ha pasado en tu tienda; ahora tienes los datos para demostrarlo:

![Reporte de Ocupación y Colas](reporte_ocupacion_y_colas_en_caja.png)

* **Optimización del flujo Aforo vs. Cola:** Compara en tiempo real cuánta gente hay "mirando" frente a cuánta hay "comprando". 
    * *Si el aforo es alto pero la cola es baja:* Tus promociones están atrayendo gente, pero no están convirtiendo en ventas.
    * *Si la cola está siempre en el límite:* Estás perdiendo dinero por lentitud en caja. ¡Es hora de abrir otra!
* **Identificación de "Fugas de Clientes":** Analizando estas gráficas, puedes saber exactamente cuándo necesitas reforzar las cajas para que la experiencia del cliente sea siempre fluida y evitar que la gente se marche al ver demasiada espera.
* **Planificación de Turnos Basada en Datos:** Deja de pagar horas extra innecesarias. Identifica tus **"Horas Críticas"** reales y refuerza el equipo solo cuando la gráfica te indique que la saturación es recurrente.

## 🛠️ Requisitos e Instalación

### 1. Sistema Operativo y Audio
Este sistema está diseñado para **Ubuntu / Linux**. Para la reproducción de alertas de voz, es necesario instalar el motor de audio externo:
```bash
sudo apt update && sudo apt install mpg123 -y
```
