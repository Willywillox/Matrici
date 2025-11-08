"""
Modulo per il calcolo della capability per fasce orarie
"""
from datetime import datetime, time, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict
import pandas as pd
from utils.erlang_calculator import ErlangCalculator


class CapabilityCalculator:
    """Calcola la capability degli operatori per fasce orarie"""

    def __init__(self, operatori: List, forecast: List = None, db_manager=None):
        """
        Args:
            operatori: Lista di oggetti Operatore
            forecast: Lista di dict con forecast (opzionale)
            db_manager: DatabaseManager per caricare config Erlang (opzionale)
        """
        self.operatori = operatori
        self.forecast = forecast or []
        self.db_manager = db_manager
        self.erlang_calculator = ErlangCalculator()
        self.erlang_configs = self._load_erlang_configs() if db_manager else {}

    def _load_erlang_configs(self) -> Dict:
        """Carica configurazioni Erlang C per skill"""
        configs = {}

        try:
            if not self.db_manager:
                return configs

            # Assicurati che il DB sia connesso
            if not hasattr(self.db_manager, 'conn') or self.db_manager.conn is None:
                self.db_manager.connect()

            result = self.db_manager.execute_query("""
                SELECT Skill, Tipo_Canale, AHT_Seconds, Concurrency, Tempo_Pausa_Minuti,
                       Shrinkage, Service_Level_Target, Service_Level_Seconds,
                       ASA_Target_Seconds, Occupancy_Target, Interval_Minutes
                FROM Erlang_Config
            """)

            if result:
                for row in result:
                    skill = row[0]
                    configs[skill] = {
                        'tipo_canale': row[1],
                        'aht_seconds': row[2],
                        'concurrency': row[3],
                        'tempo_pausa_minuti': row[4],
                        'shrinkage': row[5],
                        'service_level_target': row[6],
                        'service_level_seconds': row[7],
                        'asa_target_seconds': row[8],
                        'occupancy_target': row[9],
                        'interval_minutes': row[10]
                    }

        except Exception as e:
            print(f"Avviso: Impossibile caricare configurazioni Erlang: {e}")

        return configs

    def genera_fasce_orarie(self, data: datetime, intervallo_minuti: int = 15) -> List[datetime]:
        """
        Genera le fasce orarie per una giornata

        Args:
            data: Data di riferimento
            intervallo_minuti: Intervallo in minuti (15 o 30)

        Returns:
            Lista di datetime rappresentanti l'inizio di ogni fascia
        """
        fasce = []
        inizio = datetime.combine(data.date(), time(0, 0))
        fine = datetime.combine(data.date(), time(23, 59))

        current = inizio
        while current <= fine:
            fasce.append(current)
            current += timedelta(minutes=intervallo_minuti)

        return fasce

    def calcola_capability_per_fascia(
        self,
        data: datetime,
        intervallo_minuti: int = 15
    ) -> pd.DataFrame:
        """
        Calcola la capability per ogni fascia oraria

        Returns:
            DataFrame con colonne: Fascia_Oraria, Skill, Presenti, In_Pausa,
                                  In_Produzione, In_Straordinario, FTE_Effettivi
        """
        fasce = self.genera_fasce_orarie(data, intervallo_minuti)
        risultati = []

        for fascia in fasce:
            orario = fascia.time()

            # Raggruppa per skill
            stats_per_skill = defaultdict(lambda: {
                'presenti': 0,
                'in_pausa': 0,
                'in_produzione': 0,
                'in_straordinario': 0,
                'operatori_presenti': [],
                'operatori_in_pausa': [],
                'operatori_in_produzione': [],
                'operatori_in_straordinario': []
            })

            for operatore in self.operatori:
                if operatore.is_presente(orario):
                    skill = operatore.get_skill_at_time(orario)

                    stats_per_skill[skill]['presenti'] += 1
                    stats_per_skill[skill]['operatori_presenti'].append(operatore.id_sap)

                    if operatore.is_in_pausa(orario):
                        stats_per_skill[skill]['in_pausa'] += 1
                        stats_per_skill[skill]['operatori_in_pausa'].append(operatore.id_sap)
                    else:
                        stats_per_skill[skill]['in_produzione'] += 1
                        stats_per_skill[skill]['operatori_in_produzione'].append(operatore.id_sap)

                    if operatore.is_in_straordinario(orario):
                        stats_per_skill[skill]['in_straordinario'] += 1
                        stats_per_skill[skill]['operatori_in_straordinario'].append(operatore.id_sap)

            # Crea record per ogni skill
            for skill, stats in stats_per_skill.items():
                fte_effettivi = stats['in_produzione']  # Operatori effettivamente produttivi

                risultati.append({
                    'Fascia_Oraria': fascia,
                    'Skill': skill,
                    'Presenti': stats['presenti'],
                    'In_Pausa': stats['in_pausa'],
                    'In_Produzione': stats['in_produzione'],
                    'In_Straordinario': stats['in_straordinario'],
                    'FTE_Effettivi': fte_effettivi,
                    'Operatori_Presenti': ', '.join(stats['operatori_presenti']),
                    'Operatori_In_Pausa': ', '.join(stats['operatori_in_pausa']),
                    'Operatori_In_Produzione': ', '.join(stats['operatori_in_produzione']),
                    'Operatori_In_Straordinario': ', '.join(stats['operatori_in_straordinario'])
                })

        df = pd.DataFrame(risultati)

        # Aggiungi dati forecast se disponibili
        if self.forecast:
            df = self._merge_forecast(df, data)

        return df

    def _merge_forecast(self, df_capability: pd.DataFrame, data: datetime) -> pd.DataFrame:
        """Merge dei dati di capability con i forecast"""
        # Crea DataFrame dai forecast
        forecast_records = []
        for f in self.forecast:
            if isinstance(f.get('Data_Riferimento'), datetime):
                if f['Data_Riferimento'].date() == data.date():
                    forecast_records.append({
                        'Fascia_Oraria': f['Fascia_Oraria'],
                        'Skill': f['Skill'],
                        'Volumi_Attesi': f.get('Volumi_Attesi', 0),
                        'Produttivita_Target': f.get('Produttivita_Target', 1),
                        'FTE_Richiesti': f.get('FTE_Richiesti', 0)
                    })

        if not forecast_records:
            # Aggiungi colonne vuote
            df_capability['Volumi_Attesi'] = 0
            df_capability['Produttivita_Target'] = 0
            df_capability['FTE_Richiesti'] = 0
            df_capability['Delta_FTE'] = 0
            df_capability['Copertura_%'] = 100
            return df_capability

        df_forecast = pd.DataFrame(forecast_records)

        # Merge
        df_merged = df_capability.merge(
            df_forecast,
            on=['Fascia_Oraria', 'Skill'],
            how='left'
        )

        # Calcola delta e copertura
        df_merged['Volumi_Attesi'].fillna(0, inplace=True)
        df_merged['FTE_Richiesti'].fillna(0, inplace=True)
        df_merged['Produttivita_Target'].fillna(1, inplace=True)

        # === CALCOLO ERLANG C ===
        # Se abbiamo configurazione Erlang e volumi previsti, ricalcola FTE_Richiesti
        if self.erlang_configs:
            df_merged['FTE_Richiesti'] = df_merged.apply(
                lambda row: self._calculate_required_fte_erlang(
                    row['Skill'],
                    row['Volumi_Attesi'],
                    row['FTE_Richiesti']  # Fallback se Erlang non disponibile
                ),
                axis=1
            )

        df_merged['Delta_FTE'] = df_merged['FTE_Effettivi'] - df_merged['FTE_Richiesti']

        # Calcola copertura percentuale
        df_merged['Copertura_%'] = df_merged.apply(
            lambda row: (row['FTE_Effettivi'] / row['FTE_Richiesti'] * 100)
            if row['FTE_Richiesti'] > 0 else 100,
            axis=1
        )

        return df_merged

    def _calculate_required_fte_erlang(self, skill: str, volumi: float, fallback_fte: float) -> float:
        """
        Calcola FTE richiesti usando Erlang C

        Args:
            skill: Skill/coda
            volumi: Volumi previsti (chiamate/contatti)
            fallback_fte: Valore di fallback se Erlang non configurato

        Returns:
            FTE richiesti calcolati con Erlang C
        """
        # Se non ci sono volumi, ritorna 0
        if volumi <= 0:
            return 0

        # Se non abbiamo config per questa skill, usa fallback
        if skill not in self.erlang_configs:
            return fallback_fte

        config = self.erlang_configs[skill]

        # Calcola FTE usando Erlang C
        try:
            fte_richiesti = self.erlang_calculator.required_fte(
                calls_per_interval=volumi,
                aht_seconds=config['aht_seconds'],
                service_level_target=config['service_level_target'],
                target_seconds=config['service_level_seconds'],
                shrinkage=config['shrinkage'],
                interval_minutes=config['interval_minutes'],
                concurrency=config.get('concurrency', 1)
            )

            return fte_richiesti

        except Exception as e:
            print(f"Errore calcolo Erlang per skill {skill}: {e}")
            return fallback_fte

    def calcola_rendiconto_per_servizio(
        self,
        data_inizio: datetime,
        data_fine: datetime,
        intervallo_minuti: int = 15
    ) -> pd.DataFrame:
        """
        Calcola il rendiconto ore per servizio/skill

        Returns:
            DataFrame con: Skill, Ore_Totali, Ore_Produzione, Ore_Pausa, Ore_Straordinario
        """
        # Genera tutte le fasce nel periodo
        current_date = data_inizio
        all_results = []

        while current_date <= data_fine:
            df_day = self.calcola_capability_per_fascia(current_date, intervallo_minuti)
            df_day['Data'] = current_date.date()
            all_results.append(df_day)
            current_date += timedelta(days=1)

        if not all_results:
            return pd.DataFrame()

        df_all = pd.concat(all_results, ignore_index=True)

        # Calcola ore per skill
        ore_per_fascia = intervallo_minuti / 60.0

        rendiconto = df_all.groupby('Skill').agg({
            'Presenti': 'sum',
            'In_Produzione': 'sum',
            'In_Pausa': 'sum',
            'In_Straordinario': 'sum'
        }).reset_index()

        rendiconto['Ore_Totali_Presenza'] = rendiconto['Presenti'] * ore_per_fascia
        rendiconto['Ore_Produzione'] = rendiconto['In_Produzione'] * ore_per_fascia
        rendiconto['Ore_Pausa'] = rendiconto['In_Pausa'] * ore_per_fascia
        rendiconto['Ore_Straordinario'] = rendiconto['In_Straordinario'] * ore_per_fascia

        # Rimuovi colonne intermedie
        rendiconto = rendiconto[[
            'Skill',
            'Ore_Totali_Presenza',
            'Ore_Produzione',
            'Ore_Pausa',
            'Ore_Straordinario'
        ]]

        return rendiconto

    def calcola_rendiconto_per_persona(
        self,
        data_inizio: datetime,
        data_fine: datetime
    ) -> pd.DataFrame:
        """
        Calcola il rendiconto ore per persona

        Returns:
            DataFrame con: ID_SAP, Nome, Cognome, Ore_Lavorate, Ore_Straordinario, etc.
        """
        rendiconto = []

        for operatore in self.operatori:
            ore_lavorate = operatore.get_ore_lavorate()
            ore_straordinario = operatore.get_ore_straordinario()

            # Calcola ore per skill
            # (questa è una semplificazione - andrebbe fatto per fascia)
            skill_principale = operatore.etichetta_skill

            rendiconto.append({
                'ID_SAP': operatore.id_sap,
                'Nome': operatore.nome,
                'Cognome': operatore.cognome,
                'FTE': operatore.fte,
                'Skill_Principale': skill_principale,
                'Ore_Lavorate': ore_lavorate,
                'Ore_Straordinario': ore_straordinario,
                'Ore_Ordinarie': ore_lavorate - ore_straordinario
            })

        df = pd.DataFrame(rendiconto)

        # Ordina per cognome
        df = df.sort_values('Cognome')

        return df

    def get_dettaglio_fascia(
        self,
        fascia: datetime,
        skill: str = None
    ) -> Dict:
        """
        Ritorna il dettaglio di una specifica fascia oraria

        Returns:
            Dict con dettagli operatori presenti, in pausa, etc.
        """
        orario = fascia.time()
        dettaglio = {
            'fascia': fascia,
            'operatori_presenti': [],
            'operatori_in_pausa': [],
            'operatori_in_produzione': [],
            'operatori_in_straordinario': []
        }

        for operatore in self.operatori:
            if skill and operatore.get_skill_at_time(orario) != skill:
                continue

            if operatore.is_presente(orario):
                dettaglio['operatori_presenti'].append({
                    'id_sap': operatore.id_sap,
                    'nome': f"{operatore.cognome} {operatore.nome}",
                    'skill': operatore.get_skill_at_time(orario)
                })

                if operatore.is_in_pausa(orario):
                    dettaglio['operatori_in_pausa'].append({
                        'id_sap': operatore.id_sap,
                        'nome': f"{operatore.cognome} {operatore.nome}"
                    })
                else:
                    dettaglio['operatori_in_produzione'].append({
                        'id_sap': operatore.id_sap,
                        'nome': f"{operatore.cognome} {operatore.nome}",
                        'skill': operatore.get_skill_at_time(orario)
                    })

                if operatore.is_in_straordinario(orario):
                    dettaglio['operatori_in_straordinario'].append({
                        'id_sap': operatore.id_sap,
                        'nome': f"{operatore.cognome} {operatore.nome}"
                    })

        return dettaglio
