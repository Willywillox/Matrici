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
        self.giustificativi_map = self._load_giustificativi_map() if db_manager else {}
        self.tipologie_giustificativi = self._get_tipologie_uniche() if db_manager else []

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
                       Shrinkage, Produttivita, Service_Level_Target, Service_Level_Seconds,
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
                        'produttivita': row[6],
                        'service_level_target': row[7],
                        'service_level_seconds': row[8],
                        'asa_target_seconds': row[9],
                        'occupancy_target': row[10],
                        'interval_minutes': row[11]
                    }

        except Exception as e:
            print(f"Avviso: Impossibile caricare configurazioni Erlang: {e}")

        return configs

    def _load_giustificativi_map(self) -> Dict:
        """Carica mappatura Codice_Giustificativo -> Tipologia"""
        giust_map = {}

        try:
            if not self.db_manager:
                return giust_map

            # Assicurati che il DB sia connesso
            if not hasattr(self.db_manager, 'conn') or self.db_manager.conn is None:
                self.db_manager.connect()

            result = self.db_manager.execute_query("""
                SELECT Codice_Giustificativo, Tipologia
                FROM Giustificativi
            """)

            if result:
                for row in result:
                    codice = row[0]
                    tipologia = row[1] if row[1] else "Altro"
                    giust_map[codice] = tipologia

        except Exception as e:
            print(f"Avviso: Impossibile caricare giustificativi: {e}")

        return giust_map

    def _get_tipologie_uniche(self) -> List[str]:
        """Ottiene lista di tipologie uniche da giustificativi_map"""
        if not self.giustificativi_map:
            return []

        tipologie = sorted(set(self.giustificativi_map.values()))
        return tipologie

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
            # Inizializza contatori dinamici per tipologie giustificativi
            def create_stats_dict():
                stats = {
                    'presenti': 0,
                    'in_pausa': 0,
                    'in_produzione': 0,
                    'in_straordinario': 0,
                    'operatori_presenti': [],
                    'operatori_in_pausa': [],
                    'operatori_in_produzione': [],
                    'operatori_in_straordinario': []
                }
                # Aggiungi contatori per ogni tipologia di giustificativo
                for tipologia in self.tipologie_giustificativi:
                    stats[f'giust_{tipologia}'] = 0
                return stats

            stats_per_skill = defaultdict(create_stats_dict)

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

                    # Conta giustificativi per tipologia
                    giust_codice = operatore.get_giustificativo_at_time(orario)
                    if giust_codice and giust_codice in self.giustificativi_map:
                        tipologia = self.giustificativi_map[giust_codice]
                        key = f'giust_{tipologia}'
                        if key in stats_per_skill[skill]:
                            stats_per_skill[skill][key] += 1

            # Crea record per ogni skill
            for skill, stats in stats_per_skill.items():
                # Calcola FTE effettivi correttamente:
                # FTE = (Operatori_in_produzione × Ore_fascia) / 8
                ore_fascia = intervallo_minuti / 60.0  # Converti minuti in ore
                fte_effettivi = (stats['in_produzione'] * ore_fascia) / 8.0

                record = {
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
                }

                # Aggiungi colonne dinamiche per tipologie giustificativi
                for tipologia in self.tipologie_giustificativi:
                    key = f'giust_{tipologia}'
                    record[tipologia] = stats.get(key, 0)

                risultati.append(record)

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

            # Calcola Agenti_Richiesti (numero di teste) applicando formula inversa della shrinkage
            df_merged['Agenti_Richiesti'] = df_merged.apply(
                lambda row: self._calculate_required_agents_from_fte(
                    row['Skill'],
                    row['FTE_Richiesti']
                ),
                axis=1
            )
        else:
            # Se non abbiamo configurazioni Erlang, usa approssimazione base
            df_merged['Agenti_Richiesti'] = df_merged['FTE_Richiesti'].apply(lambda x: round(x) if x > 0 else 0)

        df_merged['Delta_FTE'] = df_merged['FTE_Effettivi'] - df_merged['FTE_Richiesti']

        # Calcola copertura percentuale
        df_merged['Copertura_%'] = df_merged.apply(
            lambda row: (row['FTE_Effettivi'] / row['FTE_Richiesti'] * 100)
            if row['FTE_Richiesti'] > 0 else 100,
            axis=1
        )

        # Calcola Gestibile Chiamate (numero di chiamate che possono essere gestite)
        df_merged['Gestibile_Chiamate'] = df_merged.apply(
            lambda row: self._calculate_gestibile_chiamate(
                row['Skill'],
                row['In_Produzione'],
                row.get('Produttivita_Target', 1.0)
            ),
            axis=1
        )

        # Calcola Capability (%): (Gestibile_Chiamate / Volumi_Attesi) × 100
        df_merged['Capability_%'] = df_merged.apply(
            lambda row: (row['Gestibile_Chiamate'] / row['Volumi_Attesi'] * 100)
            if row['Volumi_Attesi'] > 0 else 0,
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

    def _calculate_required_agents_from_fte(self, skill: str, fte_richiesti: float) -> int:
        """
        Calcola numero di teste (agenti) richiesti da FTE

        Formula inversa: Agenti = FTE * (1 - shrinkage)

        Args:
            skill: Skill/coda
            fte_richiesti: FTE richiesti (con shrinkage applicato)

        Returns:
            Numero di agenti richiesti (teste)
        """
        import math

        if fte_richiesti <= 0:
            return 0

        # Se abbiamo config per questa skill, usa la shrinkage configurata
        if skill in self.erlang_configs:
            config = self.erlang_configs[skill]
            shrinkage = config.get('shrinkage', 0.30)

            # Formula inversa: Agenti = FTE * (1 - shrinkage)
            agenti = fte_richiesti * (1 - shrinkage)

            # Arrotonda per eccesso (serve almeno questo numero di teste)
            return math.ceil(agenti)
        else:
            # Senza configurazione, approssima
            return math.ceil(fte_richiesti)

    def _calculate_gestibile_chiamate(self, skill: str, operatori_produzione: int, produttivita_target: float) -> int:
        """
        Calcola il numero di chiamate gestibili dagli operatori in produzione

        Args:
            skill: Nome dello skill
            operatori_produzione: Numero di operatori in produzione
            produttivita_target: Produttività target dal forecast (chiamate/ora per operatore)

        Returns:
            Numero totale di chiamate gestibili nella fascia oraria
        """
        if operatori_produzione <= 0:
            return 0

        # Usa produttività da configurazione Erlang se disponibile, altrimenti usa quella del forecast
        if skill in self.erlang_configs:
            config = self.erlang_configs[skill]
            aht_seconds = config.get('aht_seconds', 180)  # Default 3 minuti
            interval_minutes = config.get('interval_minutes', 15)

            # Calcola produttività oraria da AHT
            # AHT in secondi -> Chiamate all'ora = 3600 / AHT
            chiamate_ora_per_operatore = 3600.0 / aht_seconds if aht_seconds > 0 else 20.0

            # Frazione di ora per questa fascia
            frazione_ora = interval_minutes / 60.0

            # Chiamate gestibili = Operatori * Chiamate/ora * Frazione_ora
            chiamate_gestibili = operatori_produzione * chiamate_ora_per_operatore * frazione_ora
        else:
            # Usa produttività dal forecast o default
            # Assumiamo che produttivita_target sia chiamate/ora se > 1, altrimenti un fattore
            if produttivita_target > 1:
                chiamate_ora_per_operatore = produttivita_target
            else:
                chiamate_ora_per_operatore = 20.0  # Default: 20 chiamate/ora (3 min AHT)

            # Assumiamo fascia di 15 minuti se non abbiamo config
            frazione_ora = 15 / 60.0

            chiamate_gestibili = operatori_produzione * chiamate_ora_per_operatore * frazione_ora

        return int(round(chiamate_gestibili))

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

        # Aggregazione base
        agg_dict = {
            'Presenti': 'sum',
            'In_Produzione': 'sum',
            'In_Pausa': 'sum',
            'In_Straordinario': 'sum'
        }

        # Aggiungi aggregazione per tipologie giustificativi
        for tipologia in self.tipologie_giustificativi:
            if tipologia in df_all.columns:
                agg_dict[tipologia] = 'sum'

        rendiconto = df_all.groupby('Skill').agg(agg_dict).reset_index()

        # Converti contatori in ore
        rendiconto['Ore_Totali_Presenza'] = rendiconto['Presenti'] * ore_per_fascia
        rendiconto['Ore_Produzione'] = rendiconto['In_Produzione'] * ore_per_fascia
        rendiconto['Ore_Pausa'] = rendiconto['In_Pausa'] * ore_per_fascia
        rendiconto['Ore_Straordinario'] = rendiconto['In_Straordinario'] * ore_per_fascia

        # Converti giustificativi in ore
        for tipologia in self.tipologie_giustificativi:
            if tipologia in rendiconto.columns:
                rendiconto[f'Ore_{tipologia}'] = rendiconto[tipologia] * ore_per_fascia

        # Calcola FTE medio per il periodo
        # FTE = Ore_Produzione / 8 / Giorni_Lavorati
        giorni_lavorati = (data_fine - data_inizio).days + 1
        rendiconto['FTE_Medio'] = rendiconto['Ore_Produzione'] / 8.0 / giorni_lavorati

        # Seleziona colonne finali
        colonne_base = [
            'Skill',
            'Ore_Totali_Presenza',
            'Ore_Produzione',
            'Ore_Pausa',
            'Ore_Straordinario',
            'FTE_Medio'
        ]

        # Aggiungi colonne ore giustificativi
        colonne_giust = [f'Ore_{tip}' for tip in self.tipologie_giustificativi if f'Ore_{tip}' in rendiconto.columns]

        rendiconto = rendiconto[colonne_base + colonne_giust]

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
