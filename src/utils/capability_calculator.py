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

                    # Conta giustificativi per tipologia (operatori presenti)
                    giust_codice = operatore.get_giustificativo_at_time(orario)
                    if giust_codice and giust_codice in self.giustificativi_map:
                        tipologia = self.giustificativi_map[giust_codice]
                        key = f'giust_{tipologia}'
                        if key in stats_per_skill[skill]:
                            stats_per_skill[skill][key] += 1
                else:
                    # Operatore NON presente - verifica se ha un giustificativo attivo (ferie, malattia, etc.)
                    giust_codice = operatore.get_giustificativo_at_time(orario)
                    if giust_codice and giust_codice in self.giustificativi_map:
                        # Usa lo skill dell'operatore per categorizzare il giustificativo
                        skill = operatore.etichetta_skill
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
            # Parse data_riferimento
            data_forecast = f.get('Data_Riferimento')
            if isinstance(data_forecast, str):
                try:
                    data_forecast = datetime.strptime(data_forecast, '%Y-%m-%d')
                except:
                    continue

            # Verifica che sia la data corretta
            if not isinstance(data_forecast, datetime):
                continue
            if data_forecast.date() != data.date():
                continue

            # Parse fascia_oraria - converte stringa "HH:MM" in datetime per il merge
            fascia_value = f['Fascia_Oraria']

            if isinstance(fascia_value, str):
                # Caso 1: String "HH:MM" - combina con data
                try:
                    # Controlla se è un datetime completo come stringa
                    if ' ' in fascia_value or 'T' in fascia_value:
                        # È un datetime completo come stringa
                        fascia_datetime = pd.to_datetime(fascia_value)
                    else:
                        # È solo ora "HH:MM"
                        time_parts = fascia_value.split(':')
                        hour = int(time_parts[0])
                        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                        fascia_datetime = datetime.combine(data.date(), datetime.min.time().replace(hour=hour, minute=minute))
                except:
                    continue
            elif isinstance(fascia_value, datetime):
                # Caso 2: Già datetime - verifica che abbia la data corretta
                if fascia_value.date() != data.date():
                    # Se ha una data diversa, prendi solo l'ora e combina con data corrente
                    fascia_datetime = datetime.combine(data.date(), fascia_value.time())
                else:
                    fascia_datetime = fascia_value
            else:
                # Caso 3: Altro tipo (es: pd.Timestamp) - converti
                try:
                    fascia_datetime = pd.to_datetime(fascia_value)
                    # Assicura data corretta
                    if fascia_datetime.date() != data.date():
                        fascia_datetime = datetime.combine(data.date(), fascia_datetime.time())
                except:
                    continue

            forecast_records.append({
                'Fascia_Oraria': fascia_datetime,
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

        # Aggiungi produttività oraria per skill (per visibilità)
        df_merged['Produttivita_Oraria'] = df_merged['Skill'].apply(
            lambda skill: self._calculate_produttivita(skill)
        )

        return df_merged

    def _calculate_required_fte_erlang(self, skill: str, volumi: float, fallback_fte: float) -> float:
        """
        Calcola FTE richiesti usando la produttività calcolata

        Formula corretta:
        1. Agenti (teste) = Volume / Produttività
        2. FTE = Agenti / (1 - shrinkage)

        FTE rappresenta il Full Time Equivalent che include lo shrinkage

        Args:
            skill: Skill/coda
            volumi: Volumi previsti (chiamate/contatti) nella fascia
            fallback_fte: Valore di fallback se Erlang non configurato

        Returns:
            FTE richiesti calcolati con produttività e shrinkage
        """
        # Se non ci sono volumi, ritorna 0
        if volumi <= 0:
            return 0

        # Se non abbiamo config per questa skill, usa fallback
        if skill not in self.erlang_configs:
            return fallback_fte

        config = self.erlang_configs[skill]

        # Calcola produttività oraria usando shrinkage, occupancy e AHT
        produttivita_oraria = self._calculate_produttivita(skill)

        # Determina la frazione di ora per questa fascia
        interval_minutes = config.get('interval_minutes', 15)
        frazione_ora = interval_minutes / 60.0

        # Produttività per questa fascia
        produttivita_fascia = produttivita_oraria * frazione_ora

        if produttivita_fascia > 0:
            # Calcola AGENTI necessari (numero di teste)
            agenti_richiesti = volumi / produttivita_fascia

            # Converti Agenti in FTE considerando lo shrinkage
            # FTE = Agenti / (1 - shrinkage)
            # Perché: Agenti = FTE × (1 - shrinkage)
            shrinkage = config.get('shrinkage', 0.30)
            fte_richiesti = agenti_richiesti / (1 - shrinkage)
        else:
            # Fallback se produttività è zero
            fte_richiesti = fallback_fte

        return fte_richiesti

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

    def _calculate_produttivita(self, skill: str, volume_riferimento: int = 100) -> float:
        """
        Calcola la produttività (chiamate/ora) per uno skill usando Erlang C

        Formula nuova (basata su Erlang C):
        1. Calcola occupancy (Available) da Erlang C per volume di riferimento
        2. Minuto Utile = 60 × (1 - shrinkage) × (1 - occupancy)
        3. Produttività oraria = (Minuto Utile × 60) / AHT

        Per BO: Available = 0 (nessun tempo di attesa)

        Args:
            skill: Nome dello skill
            volume_riferimento: Volume chiamate di riferimento per calcolo Erlang (default 100)

        Returns:
            Produttività in chiamate/ora per operatore
        """
        if skill in self.erlang_configs:
            config = self.erlang_configs[skill]
            aht_seconds = config.get('aht_seconds', 180)
            shrinkage = config.get('shrinkage', 0.30)
            sl_target = config.get('service_level_target', 0.80)
            sl_seconds = config.get('service_level_seconds', 20)
            interval_minutes = config.get('interval_minutes', 30)
            tipo_canale = config.get('tipo_canale', 'Voice')

            try:
                if tipo_canale == 'BO':
                    # BO: Nessun Service Level, Available = 0
                    occupancy = 0.0
                else:
                    # Voice/Chat: Calcola occupancy con Erlang C
                    traffic = self.erlang_calculator.calculate_traffic_intensity(
                        volume_riferimento, aht_seconds, interval_minutes
                    )
                    agenti = self.erlang_calculator.required_agents(
                        volume_riferimento, aht_seconds, sl_target, sl_seconds, interval_minutes
                    )
                    occupancy = self.erlang_calculator.calculate_occupancy(traffic, agenti)

                # Calcola Minuto Utile: 60 × (1 - shrinkage) × (1 - occupancy)
                minuto_utile = 60 * (1 - shrinkage) * (1 - occupancy)

                # Produttività oraria: (Minuto Utile × 60) / AHT
                if aht_seconds > 0:
                    produttivita_oraria = (minuto_utile * 60) / aht_seconds
                else:
                    produttivita_oraria = 0

                return produttivita_oraria

            except Exception as e:
                # Fallback in caso di errore
                print(f"Errore calcolo produttività Erlang per {skill}: {e}")
                # Usa formula semplificata
                if aht_seconds > 0:
                    return (60 * (1 - shrinkage) * 0.7 * 60) / aht_seconds
                else:
                    return 10.0
        else:
            # Default: formula semplificata senza Erlang C
            # Assumo occupancy 70%, shrinkage 30%
            return (60 * 0.70 * 0.70 * 60) / 180  # ~ 9.8 chiamate/ora

    def _calculate_gestibile_chiamate(self, skill: str, operatori_produzione: int, produttivita_target: float) -> int:
        """
        Calcola il numero di chiamate gestibili dagli operatori in produzione

        Args:
            skill: Nome dello skill
            operatori_produzione: Numero di operatori in produzione
            produttivita_target: Produttività target dal forecast (chiamate/ora per operatore) - usato solo come fallback

        Returns:
            Numero totale di chiamate gestibili nella fascia oraria
        """
        if operatori_produzione <= 0:
            return 0

        # Calcola produttività oraria usando Erlang C (shrinkage + occupancy + AHT)
        produttivita_oraria = self._calculate_produttivita(skill)

        # Determina la frazione di ora per questa fascia
        if skill in self.erlang_configs:
            interval_minutes = self.erlang_configs[skill].get('interval_minutes', 15)
        else:
            interval_minutes = 15  # Default: 15 minuti

        frazione_ora = interval_minutes / 60.0

        # Chiamate gestibili = Operatori * Produttività/ora * Frazione_ora
        chiamate_gestibili = operatori_produzione * produttivita_oraria * frazione_ora

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
        print(f"[DEBUG] Inizio calcolo rendiconto per servizio: {len(self.operatori)} operatori")
        print(f"[DEBUG] Periodo: {data_inizio.strftime('%Y-%m-%d')} - {data_fine.strftime('%Y-%m-%d')}")
        print(f"[DEBUG] Tipologie giustificativi: {self.tipologie_giustificativi}")

        # Genera tutte le fasce nel periodo
        current_date = data_inizio
        all_results = []

        while current_date <= data_fine:
            df_day = self.calcola_capability_per_fascia(current_date, intervallo_minuti)
            if not df_day.empty:
                print(f"[DEBUG] Data {current_date.strftime('%Y-%m-%d')}: {len(df_day)} righe, colonne: {df_day.columns.tolist()[:5]}...")
            else:
                print(f"[DEBUG] Data {current_date.strftime('%Y-%m-%d')}: DataFrame vuoto")
            df_day['Data'] = current_date.date()
            all_results.append(df_day)
            current_date += timedelta(days=1)

        if not all_results:
            print("[DEBUG] Nessun risultato generato")
            return pd.DataFrame()

        df_all = pd.concat(all_results, ignore_index=True)
        print(f"[DEBUG] DataFrame concatenato: {len(df_all)} righe")

        if df_all.empty:
            print("[DEBUG] DataFrame concatenato vuoto, ritorno DataFrame vuoto")
            return pd.DataFrame()

        if 'Skill' not in df_all.columns:
            print(f"[ERROR] Colonna 'Skill' mancante! Colonne presenti: {df_all.columns.tolist()}")
            return pd.DataFrame()

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

        # Calcola Ore Ordinarie da Turno (produzione escluso straordinario)
        rendiconto['Ore_Ordinarie_Turno'] = rendiconto['Ore_Produzione'] - rendiconto['Ore_Straordinario']

        # Calcola Estensione Straordinario = Ore_Strao / Ore_Ordinarie_Turno
        rendiconto['Estensione_Straordinario_%'] = rendiconto.apply(
            lambda row: (row['Ore_Straordinario'] / row['Ore_Ordinarie_Turno'] * 100)
            if row['Ore_Ordinarie_Turno'] > 0 else 0,
            axis=1
        )

        # Calcola Ore Assenze Totali (escluso Form)
        ore_assenze_totali = pd.Series(0, index=rendiconto.index)
        for tipologia in self.tipologie_giustificativi:
            col_name = f'Ore_{tipologia}'
            # Escludi "Form" dal conteggio assenze
            if col_name in rendiconto.columns and tipologia != 'Form':
                ore_assenze_totali += rendiconto[col_name].fillna(0)

        rendiconto['Ore_Assenze_Totali'] = ore_assenze_totali

        # Calcola Ore Pianificate = Ore Ordinarie + Assenze + (eventualmente Malattia già inclusa in Assenze)
        # Ore_Pianificate = Ore_Ordinarie_Turno + Ore_Assenze_Totali
        rendiconto['Ore_Pianificate'] = rendiconto['Ore_Ordinarie_Turno'] + rendiconto['Ore_Assenze_Totali']

        # Calcola Assenteismo = Ore_Assenze_Totali / Ore_Pianificate
        rendiconto['Assenteismo_%'] = rendiconto.apply(
            lambda row: (row['Ore_Assenze_Totali'] / row['Ore_Pianificate'] * 100)
            if row['Ore_Pianificate'] > 0 else 0,
            axis=1
        )

        # Seleziona colonne finali
        colonne_base = [
            'Skill',
            'Ore_Totali_Presenza',
            'Ore_Produzione',
            'Ore_Ordinarie_Turno',
            'Ore_Pausa',
            'Ore_Straordinario',
            'Estensione_Straordinario_%',
            'FTE_Medio'
        ]

        # Aggiungi colonne ore giustificativi
        colonne_giust = [f'Ore_{tip}' for tip in self.tipologie_giustificativi if f'Ore_{tip}' in rendiconto.columns]

        # Aggiungi colonne di calcolo assenteismo
        colonne_assenze = [
            'Ore_Assenze_Totali',
            'Ore_Pianificate',
            'Assenteismo_%'
        ]

        rendiconto = rendiconto[colonne_base + colonne_giust + colonne_assenze]

        return rendiconto

    def calcola_rendiconto_per_persona(
        self,
        data_inizio: datetime,
        data_fine: datetime,
        intervallo_minuti: int = 15
    ) -> pd.DataFrame:
        """
        Calcola il rendiconto ore per persona con dettaglio giustificativi

        Returns:
            DataFrame con: ID_SAP, Nome, Cognome, Skill, Ore_Produzione, Ore_Pausa,
                          Ore_Straordinario, Ore_{Giustificativi}, metriche calcolate
        """
        print(f"[DEBUG] Inizio calcolo rendiconto per persona: {len(self.operatori)} operatori")
        print(f"[DEBUG] Periodo: {data_inizio.strftime('%Y-%m-%d')} - {data_fine.strftime('%Y-%m-%d')}")
        print(f"[DEBUG] Tipologie giustificativi: {self.tipologie_giustificativi}")

        # Genera fasce orarie per il periodo
        fasce_orarie = []
        current_date = data_inizio
        while current_date <= data_fine:
            fasce_day = self.genera_fasce_orarie(current_date, intervallo_minuti)
            fasce_orarie.extend(fasce_day)
            current_date += timedelta(days=1)

        print(f"[DEBUG] Fasce orarie generate: {len(fasce_orarie)}")

        if not fasce_orarie:
            print("[DEBUG] Nessuna fascia oraria generata, ritorno DataFrame vuoto")
            return pd.DataFrame()

        # Processa ogni operatore per ogni fascia
        records_per_persona = []
        ore_per_fascia = intervallo_minuti / 60.0
        fasce_processate = set()

        for op in self.operatori:
            for fascia_oraria in fasce_orarie:
                orario = fascia_oraria.time()

                # Crea chiave univoca per evitare duplicati
                chiave = (op.id_sap, fascia_oraria)
                if chiave in fasce_processate:
                    continue
                fasce_processate.add(chiave)

                # Inizializza record
                skill = op.get_skill_at_time(orario) if hasattr(op, 'get_skill_at_time') else op.etichetta_skill

                record = {
                    'ID_SAP': op.id_sap,
                    'Nome': op.nome,
                    'Cognome': op.cognome,
                    'Skill': skill if skill else 'N/A',
                    'Fascia_Oraria': fascia_oraria,
                    'In_Produzione': 0,
                    'In_Pausa': 0,
                    'In_Straordinario': 0,
                }

                # Inizializza giustificativi
                for tipologia in self.tipologie_giustificativi:
                    record[tipologia] = 0

                # Verifica stato operatore
                if op.is_presente(orario):
                    # Operatore presente
                    if op.is_in_pausa(orario):
                        record['In_Pausa'] = 1
                    else:
                        record['In_Produzione'] = 1

                    if op.is_in_straordinario(orario):
                        record['In_Straordinario'] = 1

                    # Verifica giustificativo
                    giust_codice = op.get_giustificativo_at_time(orario)
                    if giust_codice and giust_codice in self.giustificativi_map:
                        tipologia = self.giustificativi_map[giust_codice]
                        record[tipologia] = 1

                else:
                    # Operatore non presente - verifica se ha giustificativo
                    giust_codice = op.get_giustificativo_at_time(orario)
                    if giust_codice and giust_codice in self.giustificativi_map:
                        tipologia = self.giustificativi_map[giust_codice]
                        record[tipologia] = 1

                # Aggiungi solo se c'è qualche attività
                ha_attivita = (record['In_Produzione'] > 0 or
                              record['In_Pausa'] > 0 or
                              record['In_Straordinario'] > 0 or
                              any(record[tip] > 0 for tip in self.tipologie_giustificativi))

                if ha_attivita:
                    records_per_persona.append(record)

        print(f"[DEBUG] Record creati: {len(records_per_persona)}")

        if not records_per_persona:
            print("[DEBUG] Nessun record creato, ritorno DataFrame vuoto")
            return pd.DataFrame()

        df_persone = pd.DataFrame(records_per_persona)
        print(f"[DEBUG] DataFrame creato con colonne: {df_persone.columns.tolist()}")
        print(f"[DEBUG] Righe nel DataFrame: {len(df_persone)}")

        # Aggregazione per persona
        agg_dict = {
            'Nome': 'first',
            'Cognome': 'first',
            'Skill': 'first',
            'In_Produzione': 'sum',
            'In_Pausa': 'sum',
            'In_Straordinario': 'sum'
        }

        # Aggiungi aggregazione per tipologie giustificativi
        for tipologia in self.tipologie_giustificativi:
            if tipologia in df_persone.columns:
                agg_dict[tipologia] = 'sum'

        print(f"[DEBUG] Aggregazione con chiavi: {list(agg_dict.keys())}")

        try:
            rendiconto = df_persone.groupby('ID_SAP').agg(agg_dict).reset_index()
            print(f"[DEBUG] Aggregazione completata, righe: {len(rendiconto)}")
        except Exception as e:
            print(f"[ERROR] Errore durante aggregazione: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

        # Converti contatori in ore
        rendiconto['Ore_Produzione'] = rendiconto['In_Produzione'] * ore_per_fascia
        rendiconto['Ore_Pausa'] = rendiconto['In_Pausa'] * ore_per_fascia
        rendiconto['Ore_Straordinario'] = rendiconto['In_Straordinario'] * ore_per_fascia

        # Converti giustificativi in ore
        for tipologia in self.tipologie_giustificativi:
            if tipologia in rendiconto.columns:
                rendiconto[f'Ore_{tipologia}'] = rendiconto[tipologia] * ore_per_fascia

        # Calcola Ore Ordinarie da Turno
        rendiconto['Ore_Ordinarie_Turno'] = rendiconto['Ore_Produzione'] - rendiconto['Ore_Straordinario']

        # Calcola Estensione Straordinario
        rendiconto['Estensione_Straordinario_%'] = rendiconto.apply(
            lambda row: (row['Ore_Straordinario'] / row['Ore_Ordinarie_Turno'] * 100)
            if row['Ore_Ordinarie_Turno'] > 0 else 0,
            axis=1
        )

        # Calcola Ore Assenze Totali (escluso Form)
        ore_assenze_totali = pd.Series(0, index=rendiconto.index)
        for tipologia in self.tipologie_giustificativi:
            col_name = f'Ore_{tipologia}'
            if col_name in rendiconto.columns and tipologia != 'Form':
                ore_assenze_totali += rendiconto[col_name].fillna(0)

        rendiconto['Ore_Assenze_Totali'] = ore_assenze_totali

        # Calcola Ore Pianificate
        rendiconto['Ore_Pianificate'] = rendiconto['Ore_Ordinarie_Turno'] + rendiconto['Ore_Assenze_Totali']

        # Calcola Assenteismo
        rendiconto['Assenteismo_%'] = rendiconto.apply(
            lambda row: (row['Ore_Assenze_Totali'] / row['Ore_Pianificate'] * 100)
            if row['Ore_Pianificate'] > 0 else 0,
            axis=1
        )

        # Calcola FTE medio
        giorni_lavorati = (data_fine - data_inizio).days + 1
        rendiconto['FTE_Medio'] = rendiconto['Ore_Produzione'] / 8.0 / giorni_lavorati

        # Seleziona colonne finali
        colonne_base = [
            'ID_SAP',
            'Cognome',
            'Nome',
            'Skill',
            'Ore_Produzione',
            'Ore_Ordinarie_Turno',
            'Ore_Pausa',
            'Ore_Straordinario',
            'Estensione_Straordinario_%',
            'FTE_Medio'
        ]

        # Aggiungi colonne ore giustificativi
        colonne_giust = [f'Ore_{tip}' for tip in self.tipologie_giustificativi if f'Ore_{tip}' in rendiconto.columns]

        # Aggiungi colonne di calcolo assenteismo
        colonne_assenze = [
            'Ore_Assenze_Totali',
            'Ore_Pianificate',
            'Assenteismo_%'
        ]

        colonne_finali = colonne_base + colonne_giust + colonne_assenze

        # Verifica che tutte le colonne esistano
        colonne_mancanti = [col for col in colonne_finali if col not in rendiconto.columns]
        if colonne_mancanti:
            print(f"[WARNING] Colonne mancanti: {colonne_mancanti}")
            # Rimuovi colonne mancanti dalla selezione
            colonne_finali = [col for col in colonne_finali if col in rendiconto.columns]

        print(f"[DEBUG] Colonne finali selezionate: {colonne_finali}")

        rendiconto = rendiconto[colonne_finali]

        # Ordina per cognome
        rendiconto = rendiconto.sort_values('Cognome')

        print(f"[DEBUG] Rendiconto finale: {len(rendiconto)} righe, {len(rendiconto.columns)} colonne")
        print(f"[DEBUG] Colonne finali: {rendiconto.columns.tolist()}")

        return rendiconto

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
