# **Usuario**

> NOTAS:
>
> - Los pasajeros solo podrán ver el núemro de placas del conductor al aceptar el viaje.
> - En el tipo de viaje _salida_ por default el punto de recogida es CU, no se puede elegir.

## | LOG IN / REGISTER |

1. Log: correo, contraseña
2. Reg: nombre completo, correo, contraseña

---

## | HOME |

### Panel 1

- Seleccionar tipo de viaje (entrada o salida de la escuela)
- Seleccionar tipo de rol (conductor o pasajero). Nota: **Esto es solo para los conductores**

### Panel 2

Caso: **_"¡Hola! Solicita un raite" (pasajero)_**

>     - No has solicitado ningun raite

Caso: **_"¡Han solicitado ser tu raite!" (pasajero)_**

Datos del conductor:

>     - Nombre
>     - Edad
>     - Sexo
>     - Carrera
>     - Calificación en la app
>     - Vehículo
>     - Capacidad de pasajeros

Datos del viaje:

>     - Tipo de viaje (entrada o salida de la escuela)
>     - Punto
>     - Destino (Siempre CU)
>     - Horario de llegada al destino
>     - Preferencias del viaje (con conductor del mismo sexo, usar la cajuela, etc.)

---

Caso: **_"¡Han aceptado tu raite!" (conductor)_**

Datos del pasajero

>     - Nombre
>     - Edad
>     - Sexo
>     - Carrera
>     - Calificación en la app
>     - Vehículo
>     - Preferencias del viaje (con conductor del mismo sexo, usar la cajuela, etc.)

Datos del viaje

>     - Tipo de viaje (entrada o salida de la escuela)
>     - Punto
>     - Destino (Siempre CU)
>     - Horario de llegada al destino
>     - Configuración (con conductor del mismo sexo, usar la cajuela, etc.)

---

Caso: **_"!Tienes un raite programado!" (pasajero y conductor)_**

_1. Pasajero:_

Datos del conductor:

>     - Nombre
>     - Edad
>     - Sexo
>     - Carrera
>     - Calificación en la app
>     - Vehículo
>     - Capacidad de pasajeros

Datos del viaje:

>     - Tipo de viaje (entrada o salida de la escuela)
>     - Punto
>     - Destino (Siempre CU)
>     - Horario de llegada al destino
>     - Preferencias del viaje (con conductor del mismo sexo, usar la cajuela, etc.)

---

_2. Conductor:_

Datos del pasajero

>     - Nombre
>     - Edad
>     - Sexo
>     - Carrera
>     - Calificación en la app
>     - Vehículo
>     - Preferencias del viaje (con conductor del mismo sexo, usar la cajuela, etc.)

Datos del viaje

>     - Tipo de viaje (entrada o salida de la escuela)
>     - Punto
>     - Destino (Siempre CU)
>     - Horario de llegada al destino
>     - Configuración (con conductor del mismo sexo, usar la cajuela, etc.)

---

## | PEDIR RAITE |

(pasajero)

1. Mapa para seleccionar punto (a la derecha en el layout)
   > Puntos: los que dispone el sistema para poder pedir raite
2. Pedir raite (se borra cada 24 horas)
3. Panel de detalle de punto (a la izquierda del layout)

---

## | DAR RAITE |

(conductor)

1. Mapa para seleccionar punto (a la derecha en el layout)
   - Puntos: hay un raite pedido para ese punto
2. Aceptar raite

---

---

# **Admin**

# **Pendientes**

> - ¿Cómo maneja leaflet los puntos? ¿Ya hay malls o tiendas rápidas mapeadas?
> - ¿Cómo se manejará la utenticación para que lo susuarios no puedan acceder más que a al página que les corresponde?
> - ¿Cómo funciona el admin default de django?
> - Se tien euq hacer el UML con base en este documento.
