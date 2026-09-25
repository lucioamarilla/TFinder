"""Reproducción del bug de la carrera por vacante (AE1).

Este archivo NO se recopila con pytest (no matchea `test_*.py`).
Documenta el fallo que motivó las barreras de B06:

1. Sin el UPDATE condicional (`ocupar_vacante`) ni la reserva Redis
   (`reservar` en `services/vacante.py`), N solicitudes concurrentes
   contra una mesa con 1 vacante terminan TODAS en 201 y el contador
   `jugadores_actuales` supera a `jugadores_max`.

2. Con B06 (doble barrera: SET NX en Redis + UPDATE ... WHERE
   jugadores_actuales < jugadores_max), exactamente una gana: 1x201
   y 9x409 (ver `tests/test_carrera.py`).

Para reproducir el "antes", quitar el WHERE/RESERVA de forma temporal y
correr `tests/test_carrera.py`: se observa `codigos.count(201) == 10` y
`jugadores_actuales == 10 > jugadores_max == 1`.
"""