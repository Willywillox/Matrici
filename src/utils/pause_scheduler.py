#!/usr/bin/env python3
"""
Sistema automatico di distribuzione pause intelligente

Distribuisce pause di 15 minuti tra operatori in modo ottimale:
- 3 slot disponibili: dopo 1h45, 2h, 2h15 dall'inizio turno
- Evita sovrapposizioni (spalma pause tra operatori)
- Considera turno e skill per bilanciamento
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional


class PauseScheduler:
    """Scheduler intelligente per distribuzione automatica pause"""

    # Slot pause disponibili (offset dall'inizio turno)
    SLOT_OFFSETS = [
        timedelta(hours=1, minutes=45),  # Slot 1: dopo 1h45
        timedelta(hours=2, minutes=0),   # Slot 2: dopo 2h
        timedelta(hours=2, minutes=15),  # Slot 3: dopo 2h15
    ]

    PAUSA_DURATA = timedelta(minutes=15)  # Durata pausa: 15 minuti

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def calcola_pause_automatiche(
        self,
        ora_inizio_turno: str,
        ora_fine_turno: str,
        skill: str,
        data_riferimento: str,
        id_sap_corrente: Optional[str] = None,
        num_pause: int = 1
    ) -> List[Tuple[str, str]]:
        """
        Calcola pause ottimali per operatore

        Args:
            ora_inizio_turno: Orario inizio turno (HH:MM:SS o HH:MM)
            ora_fine_turno: Orario fine turno
            skill: Skill operatore
            data_riferimento: Data turno (YYYY-MM-DD)
            id_sap_corrente: ID_SAP operatore corrente (None se nuovo)
            num_pause: Numero pause da assegnare (1-3)

        Returns:
            Lista di tuple (inizio_pausa, fine_pausa) in formato HH:MM:SS
        """

        # Parse orari
        try:
            inizio = self._parse_time(ora_inizio_turno)
            fine = self._parse_time(ora_fine_turno)
        except:
            # Se parsing fallisce, usa slot base
            return self._genera_pause_default(num_pause)

        # Verifica durata turno sufficiente
        durata_turno = self._calcola_durata(inizio, fine)
        if durata_turno < timedelta(hours=3):
            # Turno troppo corto per pause automatiche
            return []

        # Carica operatori esistenti stesso turno/skill/data
        operatori_esistenti = self._carica_operatori_simili(
            skill, data_riferimento, id_sap_corrente
        )

        # Analizza occupazione slot
        occupazione_slot = self._analizza_occupazione_slot(
            operatori_esistenti, inizio
        )

        # Seleziona slot ottimali (meno affollati)
        slot_selezionati = self._seleziona_slot_ottimali(
            occupazione_slot, num_pause
        )

        # Genera pause
        pause = []
        for slot_idx in slot_selezionati:
            offset = self.SLOT_OFFSETS[slot_idx]

            # Calcola orario pausa
            inizio_pausa = self._aggiungi_offset(inizio, offset)
            fine_pausa = self._aggiungi_offset(inizio_pausa, self.PAUSA_DURATA)

            # Verifica che pausa sia dentro turno
            if self._time_to_minutes(fine_pausa) <= self._time_to_minutes(fine):
                pause.append((
                    inizio_pausa.strftime('%H:%M:%S'),
                    fine_pausa.strftime('%H:%M:%S')
                ))

        return pause

    def _parse_time(self, time_str: str) -> datetime:
        """Parse stringa orario in datetime"""
        time_str = time_str.strip()

        # Prova vari formati
        for fmt in ['%H:%M:%S', '%H:%M']:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Formato orario non valido: {time_str}")

    def _calcola_durata(self, inizio: datetime, fine: datetime) -> timedelta:
        """Calcola durata tra due orari"""
        if fine < inizio:
            # Turno attraversa mezzanotte
            fine = fine + timedelta(days=1)
        return fine - inizio

    def _aggiungi_offset(self, base: datetime, offset: timedelta) -> datetime:
        """Aggiunge offset a orario base"""
        return base + offset

    def _time_to_minutes(self, dt: datetime) -> int:
        """Converte datetime in minuti dalla mezzanotte"""
        return dt.hour * 60 + dt.minute

    def _carica_operatori_simili(
        self,
        skill: str,
        data_riferimento: str,
        id_sap_corrente: Optional[str]
    ) -> List[Dict]:
        """
        Carica operatori con stesso skill e data

        Returns:
            Lista di dict con dati operatori
        """
        try:
            self.db_manager.connect()

            # Query operatori stesso skill e data
            query = """
                SELECT
                    ID_SAP,
                    Ora_Inizio_Turno,
                    Inizio_Pausa_1, Fine_Pausa_1,
                    Inizio_Pausa_2, Fine_Pausa_2,
                    Inizio_Pausa_3, Fine_Pausa_3,
                    Inizio_Pausa_4, Fine_Pausa_4,
                    Inizio_Pausa_5, Fine_Pausa_5
                FROM Anagrafica_Operatori
                WHERE Etichetta_Skill = ?
                  AND Data_Riferimento = ?
            """

            params = [skill, data_riferimento]

            # Escludi operatore corrente se specificato
            if id_sap_corrente:
                query += " AND ID_SAP != ?"
                params.append(id_sap_corrente)

            result = self.db_manager.execute_query(query, tuple(params))

            operatori = []
            for row in result:
                operatori.append({
                    'id_sap': row[0],
                    'inizio_turno': row[1],
                    'pause': [
                        (row[2], row[3]),   # Pausa 1
                        (row[4], row[5]),   # Pausa 2
                        (row[6], row[7]),   # Pausa 3
                        (row[8], row[9]),   # Pausa 4
                        (row[10], row[11]), # Pausa 5
                    ]
                })

            self.db_manager.close()
            return operatori

        except Exception as e:
            print(f"Errore caricamento operatori: {e}")
            return []

    def _analizza_occupazione_slot(
        self,
        operatori: List[Dict],
        inizio_turno_corrente: datetime
    ) -> List[int]:
        """
        Analizza quanti operatori hanno pause in ogni slot

        Args:
            operatori: Lista operatori esistenti
            inizio_turno_corrente: Inizio turno operatore corrente

        Returns:
            Lista con conteggio operatori per slot [slot1, slot2, slot3]
        """
        occupazione = [0, 0, 0]  # Contatori per 3 slot

        for operatore in operatori:
            # Parse inizio turno operatore
            try:
                inizio_turno_op = self._parse_time(operatore['inizio_turno'])
            except:
                continue

            # Per ogni pausa dell'operatore
            for inizio_pausa, fine_pausa in operatore['pause']:
                if not inizio_pausa or not fine_pausa:
                    continue

                try:
                    # Parse orario pausa
                    inizio_p = self._parse_time(inizio_pausa)

                    # Calcola offset dall'inizio turno
                    offset_minuti = self._time_to_minutes(inizio_p) - self._time_to_minutes(inizio_turno_op)

                    # Determina a quale slot appartiene (con tolleranza ±5 minuti)
                    for slot_idx, slot_offset in enumerate(self.SLOT_OFFSETS):
                        slot_minuti = int(slot_offset.total_seconds() / 60)

                        if abs(offset_minuti - slot_minuti) <= 5:
                            occupazione[slot_idx] += 1
                            break

                except:
                    continue

        return occupazione

    def _seleziona_slot_ottimali(
        self,
        occupazione: List[int],
        num_pause: int
    ) -> List[int]:
        """
        Seleziona slot meno affollati

        Args:
            occupazione: Conteggio operatori per slot
            num_pause: Numero pause da assegnare

        Returns:
            Lista indici slot selezionati (0, 1, 2)
        """
        # Crea lista tuple (indice, occupazione)
        slot_con_occupazione = [(i, occ) for i, occ in enumerate(occupazione)]

        # Ordina per occupazione crescente (meno affollati prima)
        slot_ordinati = sorted(slot_con_occupazione, key=lambda x: x[1])

        # Prendi primi num_pause slot
        slot_selezionati = [slot[0] for slot in slot_ordinati[:num_pause]]

        # Ordina per indice (cronologicamente)
        slot_selezionati.sort()

        return slot_selezionati

    def _genera_pause_default(self, num_pause: int) -> List[Tuple[str, str]]:
        """
        Genera pause di default se calcolo automatico fallisce

        Returns:
            Lista tuple (inizio, fine) con orari generici
        """
        # Pause di default a orari fissi (se parsing fallisce)
        pause_default = [
            ('10:45:00', '11:00:00'),  # Pausa metà mattina
            ('12:00:00', '12:15:00'),  # Pausa pranzo
            ('15:15:00', '15:30:00'),  # Pausa pomeriggio
        ]

        return pause_default[:num_pause]

    def visualizza_distribuzione(
        self,
        skill: str,
        data_riferimento: str
    ) -> Dict:
        """
        Visualizza distribuzione pause per skill e data

        Args:
            skill: Skill da analizzare
            data_riferimento: Data da analizzare

        Returns:
            Dict con statistiche distribuzione
        """
        operatori = self._carica_operatori_simili(skill, data_riferimento, None)

        # Conta operatori per slot
        slot_1h45 = 0
        slot_2h = 0
        slot_2h15 = 0

        for operatore in operatori:
            try:
                inizio_turno = self._parse_time(operatore['inizio_turno'])
            except:
                continue

            for inizio_pausa, fine_pausa in operatore['pause']:
                if not inizio_pausa:
                    continue

                try:
                    inizio_p = self._parse_time(inizio_pausa)
                    offset_minuti = self._time_to_minutes(inizio_p) - self._time_to_minutes(inizio_turno)

                    # Classifica in slot (tolleranza ±5 min)
                    if abs(offset_minuti - 105) <= 5:  # 1h45 = 105 min
                        slot_1h45 += 1
                    elif abs(offset_minuti - 120) <= 5:  # 2h = 120 min
                        slot_2h += 1
                    elif abs(offset_minuti - 135) <= 5:  # 2h15 = 135 min
                        slot_2h15 += 1
                except:
                    continue

        return {
            'skill': skill,
            'data': data_riferimento,
            'totale_operatori': len(operatori),
            'slot_1h45': slot_1h45,
            'slot_2h': slot_2h,
            'slot_2h15': slot_2h15,
            'bilanciamento': 'OK' if max(slot_1h45, slot_2h, slot_2h15) - min(slot_1h45, slot_2h, slot_2h15) <= 1 else 'Sbilanciato'
        }


# Funzione di utilità per uso rapido
def calcola_pause_automatiche(
    db_manager,
    ora_inizio_turno: str,
    skill: str,
    data_riferimento: str,
    id_sap_corrente: Optional[str] = None,
    num_pause: int = 1
) -> List[Tuple[str, str]]:
    """
    Wrapper per calcolo rapido pause

    Args:
        db_manager: Istanza DatabaseManager
        ora_inizio_turno: Orario inizio turno (HH:MM)
        skill: Skill operatore
        data_riferimento: Data (YYYY-MM-DD)
        id_sap_corrente: ID_SAP operatore (None se nuovo)
        num_pause: Numero pause (1-3)

    Returns:
        Lista tuple (inizio, fine) pause calcolate
    """
    scheduler = PauseScheduler(db_manager)

    # Usa orario fine fittizio se non fornito (8 ore dopo inizio)
    try:
        inizio = datetime.strptime(ora_inizio_turno, '%H:%M')
        fine = inizio + timedelta(hours=8)
        ora_fine_turno = fine.strftime('%H:%M')
    except:
        ora_fine_turno = "18:00"

    return scheduler.calcola_pause_automatiche(
        ora_inizio_turno,
        ora_fine_turno,
        skill,
        data_riferimento,
        id_sap_corrente,
        num_pause
    )
