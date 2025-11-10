"""
Utility per gestione orari e time slots
"""
from typing import List


def genera_orari_15min() -> List[str]:
    """
    Genera lista di orari con step di 15 minuti

    Returns:
        Lista di stringhe formato 'HH:MM' da 00:00 a 23:45
    """
    orari = ['']  # Primo elemento vuoto per "nessun orario"
    for ora in range(24):
        for minuto in [0, 15, 30, 45]:
            orari.append(f"{ora:02d}:{minuto:02d}")
    return orari
