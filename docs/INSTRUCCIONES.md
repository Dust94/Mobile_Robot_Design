# Instrucciones de Uso - Simulador de Robot Móvil

## Instalación y Ejecución

### 1. Instalar Dependencias

Abrir PowerShell en la carpeta del proyecto y ejecutar:

```powershell
pip install -r requirements.txt
```

### 2. Ejecutar la Aplicación

```powershell
python main.py
```

## Guía Paso a Paso

### Configuración Inicial

1. **Seleccionar Tipo de Robot**
   - Diferencial Centrado: Robot con 2 ruedas motrices, centro de masa en el origen
   - Diferencial Descentrado: Robot con 2 ruedas motrices, centro de masa desplazado
   - Cuatro Ruedas Centrado: Robot 4×4, centro de masa en el origen
   - Cuatro Ruedas Descentrado: Robot 4×4, centro de masa desplazado

2. **Configurar Parámetros Físicos**
   - **Masa**: Peso del robot (kg)
   - **Coef. fricción estático**: Coeficiente entre ruedas y suelo (típicamente 0.3-1.2)
   - **Largo y Ancho**: Dimensiones del chasis (m)
   - **Radio de rueda**: Radio de las ruedas (m)

3. **Configurar Tren de Rodaje**
   
   Para **Diferencial**:
   - **Distancia entre ruedas**: Separación entre las 2 ruedas motrices (m)
   - **Dist. rueda loca - eje**: Distancia de la rueda loca al eje de las motrices (m)
   
   Para **Cuatro Ruedas**:
   - **Distancia ancho**: Separación lateral entre ruedas (m)
   - **Distancia largo**: Separación frontal entre ruedas (m)

4. **Configurar Centro de Masa** (solo para descentrado)
   - **A**: Desplazamiento en X (adelante/atrás) (m)
   - **B**: Desplazamiento en Y (izquierda/derecha) (m)
   - **C**: Desplazamiento en Z (altura) (m)

5. **Seleccionar Perfil de Movimiento**
   
   **Modo A - Rampa-Constante-Rampa**:
   - Velocidad lineal objetivo (m/s)
   - Velocidad angular objetivo (rad/s)
   - Tiempo de aceleración (s)
   - Tiempo constante (s)
   - Tiempo de desaceleración (s)
   
   **Modo B - Velocidades Fijas**:
   - Velocidad lineal constante (m/s)
   - Velocidad angular constante (rad/s)
   - Duración total (s)

6. **Seleccionar Perfil de Terreno**
   
   - **Plano**: Sin inclinación
   - **Inclinación Simple**: Un eje (pitch), ángulo 0-90°
   - **Inclinación Compuesta**: Dos ejes (pitch y roll), ángulos 0-90°

7. **Aplicar Parámetros**
   - Hacer clic en el botón "Aplicar Parámetros"
   - El sistema validará la configuración
   - Si hay errores, se mostrarán en el panel inferior con instrucciones de corrección

### Ejecutar Simulación

1. **Iniciar**: Hacer clic en "Iniciar" en el panel inferior
   - La simulación comenzará en tiempo real
   - Las gráficas se actualizarán automáticamente

2. **Monitorear**: Ver el progreso en las diferentes pestañas
   - **Trayectoria**: Recorrido del robot con vectores de velocidad
   - **Velocidad del Robot**: Velocidades lineal y angular vs. tiempo
   - **Velocidad de Ruedas**: Velocidades angulares de cada rueda
   - **Fuerzas por Rueda**: Fuerzas tangenciales y normales
   - **Aceleraciones**: Aceleraciones lineal y angular
   - **Torque por Rueda**: Torque en cada rueda
   - **Potencia**: Potencias individuales y total
   - **Tabla de Resultados**: Estadísticas y energía total
   - **Vista 3D**: Terreno y recorrido (solo para terrenos inclinados)

3. **Detener**: Hacer clic en "Detener" para pausar la simulación

4. **Reiniciar**: Hacer clic en "Reiniciar" para limpiar y empezar de nuevo

## Controles de Parámetros

Cada parámetro tiene tres formas de edición:

1. **Slider (Barra deslizante)**: Arrastre para cambiar el valor
2. **Campo numérico**: Escriba el valor y presione Enter o haga clic fuera
3. **Selector de unidades**: Cambie entre unidades disponibles (el valor se convierte automáticamente)

**Nota**: Todos los resultados se muestran en unidades SI, independientemente de la unidad seleccionada para entrada.

## Ejemplos de Configuración

### Ejemplo 1: Robot Diferencial en Línea Recta

- Tipo: Diferencial Centrado
- Masa: 15 kg
- Coef. fricción: 0.6
- Distancia entre ruedas: 0.5 m
- Radio rueda: 0.08 m
- Perfil: Modo B - Velocidades Fijas
  - Velocidad lineal: 1.0 m/s
  - Velocidad angular: 0.0 rad/s
  - Duración: 10 s
- Terreno: Plano

### Ejemplo 2: Robot 4×4 con Giro en Terreno Inclinado

- Tipo: Cuatro Ruedas Centrado
- Masa: 25 kg
- Coef. fricción: 0.8
- Distancias: 0.6 m × 0.8 m
- Radio rueda: 0.12 m
- Perfil: Modo A
  - Vel. lineal: 1.5 m/s
  - Vel. angular: 0.5 rad/s
  - Tiempos: 3s / 8s / 3s
- Terreno: Inclinación Simple, 20°

### Ejemplo 3: Robot Diferencial Descentrado

- Tipo: Diferencial Descentrado
- Masa: 12 kg
- Centro de masa: A=0.1, B=0.05, C=0.15 m
- Distancia entre ruedas: 0.4 m
- Perfil: Modo A con aceleraciones suaves
- Terreno: Inclinación Compuesta (pitch=15°, roll=10°)

## Interpretación de Resultados

### Tabla de Resultados

La tabla muestra para cada variable:
- **Mínimo**: Valor mínimo alcanzado durante la simulación
- **Máximo**: Valor máximo alcanzado
- **Promedio**: Media aritmética de todos los valores
- **Moda**: Valor más frecuente (o mediana para datos continuos)

### Energía Total

La energía total consumida (J) se calcula integrando la potencia total en el tiempo:

```
E = ∫ |P(t)| dt
```

Donde P(t) es la potencia total del robot.

### Vectores de Velocidad

En la gráfica de trayectoria, los vectores rojos representan la velocidad lineal del robot:
- **Dirección**: Indica hacia dónde se mueve el robot
- **Longitud**: Proporcional a la magnitud de la velocidad

## Validaciones Automáticas

El sistema valida automáticamente:

✅ **Parámetros físicos positivos**: masa, dimensiones, radios
✅ **Coherencia geométrica**: radios vs. distancias entre ruedas
✅ **Ángulos válidos**: inclinaciones entre 0° y 90°
✅ **Tiempos no negativos**: en todos los perfiles de movimiento
✅ **Centro de masa coherente**: dentro de las dimensiones del robot

Si una validación falla, aparecerá un mensaje en el panel inferior indicando:
- **Qué parámetro** tiene el problema
- **Por qué** falla la validación
- **Cómo** corregirlo

## Solución de Problemas

### La aplicación no inicia

- Verificar que Python 3.9+ esté instalado: `python --version`
- Instalar dependencias: `pip install -r requirements.txt`
- Verificar que matplotlib y numpy estén instalados correctamente

### Las gráficas no se actualizan

- Asegurarse de hacer clic en "Aplicar Parámetros" antes de "Iniciar"
- Verificar que los parámetros pasen la validación

### Error "división por cero"

- Verificar que el radio de rueda sea mayor que 0
- Verificar que las distancias entre ruedas sean mayores que 0

### El robot no se mueve

- Verificar que las velocidades objetivo no sean 0
- En Modo A, verificar que al menos uno de los tiempos sea mayor que 0

### Valores extraños en las fuerzas

- Verificar el coeficiente de fricción (típicamente 0.3-1.5)
- Verificar que la masa sea realista
- Verificar los ángulos de inclinación (no exceder 45° para robots normales)

## Contacto y Soporte

Para preguntas, sugerencias o reportar problemas, consulte la documentación del código o contacte al desarrollador.

---

**¡Disfrute simulando robots móviles!** 🤖

