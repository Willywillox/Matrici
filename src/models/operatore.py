"""
Modello per la gestione degli operatori
"""
from datetime import datetime, time, timedelta
from typing import List, Tuple, Optional


class Operatore:
    """Rappresenta un operatore con tutti i suoi dati"""

    def __init__(self, **kwargs):
        # Dati anagrafici
        self.id = kwargs.get('ID')
        self.nome = kwargs.get('Nome', '')
        self.cognome = kwargs.get('Cognome', '')
        self.id_sap = kwargs.get('ID_SAP', '')
        self.tipo_contratto = kwargs.get('Tipo_Contratto', '')
        self.fte = kwargs.get('FTE', 1.0)
        self.ore_settimana = kwargs.get('Ore_Settimana', 40.0)

        # Turno
        self.id_turno = kwargs.get('ID_Turno', '')
        self.ora_inizio_turno = self._parse_time(kwargs.get('Ora_Inizio_Turno'))
        self.ora_fine_turno = self._parse_time(kwargs.get('Ora_Fine_Turno'))
        self.ora_inizio_turno_spezzato = self._parse_time(kwargs.get('Ora_Inizio_Turno_Spezzato'))
        self.ora_fine_turno_spezzato = self._parse_time(kwargs.get('Ora_Fine_Turno_Spezzato'))

        # Straordinari
        self.straordinari = []
        for i in range(1, 4):
            inizio = self._parse_time(kwargs.get(f'Inizio_Strao_{i}'))
            fine = self._parse_time(kwargs.get(f'Fine_Strao_{i}'))
            if inizio and fine:
                self.straordinari.append((inizio, fine))

        # Pause
        self.pause = []
        for i in range(1, 6):
            inizio = self._parse_time(kwargs.get(f'Inizio_Pausa_{i}'))
            fine = self._parse_time(kwargs.get(f'Fine_Pausa_{i}'))
            if inizio and fine:
                self.pause.append((inizio, fine))

        # Giustificativi
        self.giustificativi = []
        for i in range(1, 6):
            tipo = kwargs.get(f'Tipo_Giust_{i}')
            inizio = self._parse_time(kwargs.get(f'Inizio_Giust_{i}'))
            fine = self._parse_time(kwargs.get(f'Fine_Giust_{i}'))
            if tipo and inizio and fine:
                self.giustificativi.append({
                    'tipo': tipo,
                    'inizio': inizio,
                    'fine': fine
                })

        # Skill
        self.etichetta_skill = kwargs.get('Etichetta_Skill', '')
        self.data_riferimento = kwargs.get('Data_Riferimento')

        # Cambi skill (da caricare separatamente)
        self.cambi_skill = []

    def _parse_time(self, value):
        """Converte un valore in oggetto time"""
        if value is None:
            return None

        if isinstance(value, time):
            return value

        if isinstance(value, datetime):
            return value.time()

        if isinstance(value, str):
            try:
                # Prova formato HH:MM o HH:MM:SS
                if ':' in value:
                    parts = value.split(':')
                    hour = int(parts[0])
                    minute = int(parts[1]) if len(parts) > 1 else 0
                    second = int(parts[2]) if len(parts) > 2 else 0
                    return time(hour, minute, second)
            except:
                pass

        return None

    def is_presente(self, orario: time) -> bool:
        """Verifica se l'operatore è presente all'orario specificato"""
        # Riconosce giorno di riposo: se turno è 00:00-00:00, l'operatore non è presente
        if self.ora_inizio_turno and self.ora_fine_turno:
            if (self.ora_inizio_turno == time(0, 0, 0) and
                self.ora_fine_turno == time(0, 0, 0)):
                return False

        # Controlla giustificativi (assenze totali)
        for giust in self.giustificativi:
            if giust['tipo'].lower() in ['assenza', 'ferie', 'malattia', 'permesso']:
                if giust['inizio'] <= orario <= giust['fine']:
                    return False

        # Controlla turno normale
        if self.ora_inizio_turno and self.ora_fine_turno:
            if self._is_in_range(orario, self.ora_inizio_turno, self.ora_fine_turno):
                return True

        # Controlla turno spezzato
        if self.ora_inizio_turno_spezzato and self.ora_fine_turno_spezzato:
            if self._is_in_range(orario, self.ora_inizio_turno_spezzato, self.ora_fine_turno_spezzato):
                return True

        # Controlla straordinari
        for inizio, fine in self.straordinari:
            if self._is_in_range(orario, inizio, fine):
                return True

        return False

    def is_in_pausa(self, orario: time) -> bool:
        """Verifica se l'operatore è in pausa all'orario specificato"""
        if not self.is_presente(orario):
            return False

        for inizio, fine in self.pause:
            if self._is_in_range(orario, inizio, fine):
                return True

        return False

    def is_in_straordinario(self, orario: time) -> bool:
        """Verifica se l'operatore è in straordinario all'orario specificato"""
        for inizio, fine in self.straordinari:
            if self._is_in_range(orario, inizio, fine):
                return True
        return False

    def get_skill_at_time(self, orario: time) -> str:
        """Ritorna la skill attiva all'orario specificato"""
        # Controlla cambi skill
        for cambio in self.cambi_skill:
            if cambio['ora_inizio'] <= orario <= cambio['ora_fine']:
                return cambio['skill']

        # Altrimenti skill di default
        return self.etichetta_skill

    def get_giustificativo_at_time(self, orario: time) -> Optional[str]:
        """Ritorna il codice del giustificativo attivo all'orario specificato (se presente)"""
        for giust in self.giustificativi:
            if self._is_in_range(orario, giust['inizio'], giust['fine']):
                return giust['tipo']
        return None

    def _is_in_range(self, orario: time, inizio: time, fine: time) -> bool:
        """Verifica se un orario è compreso in un range"""
        if fine < inizio:  # Range attraversa mezzanotte
            return orario >= inizio or orario <= fine
        else:
            return inizio <= orario <= fine

    def get_ore_lavorate(self) -> float:
        """Calcola le ore totali lavorate nella giornata"""
        ore = 0.0

        # Turno normale
        if self.ora_inizio_turno and self.ora_fine_turno:
            ore += self._calcola_durata(self.ora_inizio_turno, self.ora_fine_turno)

        # Turno spezzato
        if self.ora_inizio_turno_spezzato and self.ora_fine_turno_spezzato:
            ore += self._calcola_durata(self.ora_inizio_turno_spezzato, self.ora_fine_turno_spezzato)

        # Straordinari
        for inizio, fine in self.straordinari:
            ore += self._calcola_durata(inizio, fine)

        # Sottrai pause
        for inizio, fine in self.pause:
            ore -= self._calcola_durata(inizio, fine)

        # Sottrai giustificativi
        for giust in self.giustificativi:
            ore -= self._calcola_durata(giust['inizio'], giust['fine'])

        return max(0.0, ore)

    def get_ore_straordinario(self) -> float:
        """Calcola le ore di straordinario"""
        ore = 0.0
        for inizio, fine in self.straordinari:
            ore += self._calcola_durata(inizio, fine)
        return ore

    def _calcola_durata(self, inizio: time, fine: time) -> float:
        """Calcola la durata in ore tra due orari"""
        dt_inizio = datetime.combine(datetime.today(), inizio)
        dt_fine = datetime.combine(datetime.today(), fine)

        if fine < inizio:  # Attraversa mezzanotte
            dt_fine += timedelta(days=1)

        durata = (dt_fine - dt_inizio).total_seconds() / 3600
        return durata

    def __str__(self):
        return f"{self.cognome} {self.nome} ({self.id_sap})"

    def __repr__(self):
        return f"Operatore(id_sap='{self.id_sap}', nome='{self.nome}', cognome='{self.cognome}')"
