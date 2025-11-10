"""
Modulo per calcoli Erlang C e pianificazione workforce

Fornisce funzionalità per:
- Calcolo Erlang C (probabilità di attesa)
- Calcolo Service Level
- Determinazione FTE richiesti
- Gestione shrinkage e occupancy
- Calcoli basati su AHT e volumi
"""

import math
from typing import Dict, Optional, Tuple


class ErlangCalculator:
    """Calculator per formule Erlang C e workforce planning"""

    def __init__(self):
        """Inizializza calculator con valori default"""
        self.default_config = {
            'aht_seconds': 180,           # Average Handle Time (3 minuti)
            'shrinkage': 0.30,            # Shrinkage 30% (pause, formazione, ecc.)
            'occupancy_target': 0.85,     # Occupancy target 85%
            'service_level_target': 0.80, # Service Level target 80%
            'service_level_seconds': 20,  # Risposta entro 20 secondi
            'interval_minutes': 30        # Intervallo di calcolo (30 minuti)
        }

    def factorial(self, n: int) -> int:
        """Calcola fattoriale"""
        if n <= 1:
            return 1
        return math.factorial(n)

    def erlang_c(self, agents: int, traffic_intensity: float) -> float:
        """
        Calcola Erlang C - probabilità che una chiamata debba attendere

        Args:
            agents: Numero di agenti disponibili
            traffic_intensity: Intensità traffico in Erlang (lambda * AHT)

        Returns:
            Probabilità di attesa (0-1)
        """
        if agents <= 0 or traffic_intensity <= 0:
            return 0.0

        if traffic_intensity >= agents:
            # Sistema sovraccarico
            return 1.0

        try:
            # Formula Erlang C
            # P(W>0) = (A^N / N!) * (N / (N - A)) / Sum

            # Calcola numeratore
            numerator = (traffic_intensity ** agents / self.factorial(agents)) * \
                       (agents / (agents - traffic_intensity))

            # Calcola denominatore (sommatoria)
            summation = 0
            for k in range(agents):
                summation += traffic_intensity ** k / self.factorial(k)

            summation += (traffic_intensity ** agents / self.factorial(agents)) * \
                        (agents / (agents - traffic_intensity))

            erlang_c_value = numerator / summation

            return min(max(erlang_c_value, 0.0), 1.0)  # Limita tra 0 e 1

        except (OverflowError, ZeroDivisionError):
            return 1.0 if traffic_intensity >= agents else 0.0

    def service_level(self, agents: int, traffic_intensity: float,
                     target_seconds: int, aht_seconds: int) -> float:
        """
        Calcola Service Level - % chiamate risposte entro target

        Args:
            agents: Numero agenti
            traffic_intensity: Intensità traffico in Erlang
            target_seconds: Secondi target per risposta
            aht_seconds: Average Handle Time in secondi

        Returns:
            Service Level (0-1)
        """
        if agents <= 0 or traffic_intensity <= 0:
            return 0.0

        if traffic_intensity >= agents:
            return 0.0  # Sistema sovraccarico

        # Probabilità di attesa
        pw = self.erlang_c(agents, traffic_intensity)

        if pw == 0:
            return 1.0  # Tutte le chiamate risposte immediatamente

        # Service Level = 1 - Pw * e^(-(N-A)/AHT * t)
        try:
            exponent = -(agents - traffic_intensity) / aht_seconds * target_seconds
            sl = 1 - pw * math.exp(exponent)
            return min(max(sl, 0.0), 1.0)
        except (OverflowError, ValueError):
            return 0.0

    def calculate_traffic_intensity(self, calls_per_interval: float,
                                    aht_seconds: int,
                                    interval_minutes: int = 30) -> float:
        """
        Calcola intensità traffico in Erlang

        Args:
            calls_per_interval: Numero chiamate nell'intervallo
            aht_seconds: Average Handle Time in secondi
            interval_minutes: Durata intervallo in minuti

        Returns:
            Traffic intensity in Erlang (A = λ × AHT)
        """
        if calls_per_interval <= 0 or aht_seconds <= 0:
            return 0.0

        # Converti AHT in frazione dell'intervallo
        interval_seconds = interval_minutes * 60
        aht_fraction = aht_seconds / interval_seconds

        # Traffic intensity = calls × AHT (come frazione dell'intervallo)
        return calls_per_interval * aht_fraction

    def required_agents(self, calls_per_interval: float, aht_seconds: int,
                       service_level_target: float = 0.80,
                       target_seconds: int = 20,
                       interval_minutes: int = 30,
                       max_agents: int = 200) -> int:
        """
        Calcola numero agenti necessari per raggiungere Service Level target

        Args:
            calls_per_interval: Chiamate nell'intervallo
            aht_seconds: Average Handle Time
            service_level_target: Service Level desiderato (0-1)
            target_seconds: Tempo risposta target
            interval_minutes: Durata intervallo
            max_agents: Massimo numero agenti da testare

        Returns:
            Numero minimo agenti necessari
        """
        if calls_per_interval <= 0 or aht_seconds <= 0:
            return 0

        # Calcola traffic intensity
        traffic = self.calculate_traffic_intensity(
            calls_per_interval, aht_seconds, interval_minutes
        )

        if traffic == 0:
            return 0

        # Inizia con numero minimo agenti (ceil del traffico)
        min_agents = math.ceil(traffic)

        # Cerca numero minimo agenti che soddisfa SL target
        for agents in range(min_agents, max_agents + 1):
            sl = self.service_level(agents, traffic, target_seconds, aht_seconds)
            if sl >= service_level_target:
                return agents

        return max_agents  # Fallback

    def required_fte(self, calls_per_interval: float, aht_seconds: int,
                    service_level_target: float = 0.80,
                    target_seconds: int = 20,
                    shrinkage: float = 0.30,
                    interval_minutes: int = 30,
                    concurrency: int = 1) -> float:
        """
        Calcola FTE richiesti considerando shrinkage e concurrency

        Args:
            calls_per_interval: Chiamate/chat nell'intervallo
            aht_seconds: Average Handle Time
            service_level_target: Service Level target
            target_seconds: Tempo risposta target
            shrinkage: Percentuale shrinkage (0-1)
            interval_minutes: Durata intervallo
            concurrency: Numero interazioni simultanee per agente (default 1 per voice)

        Returns:
            FTE necessari (con shrinkage e concurrency applicati)
        """
        # Per chat con concurrency > 1, l'agente può gestire più chat simultaneamente
        # Quindi il traffic intensity effettivo è ridotto dalla concurrency

        if concurrency > 1:
            # Con concurrency, calcola gli agenti necessari considerando le chat simultanee
            # Traffic intensity viene "diviso" dalla concurrency
            traffic = self.calculate_traffic_intensity(calls_per_interval, aht_seconds, interval_minutes)

            # Con concurrency, ogni agente può gestire N chat, quindi serve traffic/concurrency agenti base
            # Ma dobbiamo comunque garantire il service level, quindi usiamo formula specifica
            effective_calls = calls_per_interval / concurrency
            base_agents = self.required_agents(
                effective_calls, aht_seconds,
                service_level_target, target_seconds, interval_minutes
            )

            # Però l'agente deve comunque avere capacità, quindi aggiungiamo un fattore
            # Il minimo è ceil(traffic/concurrency) per gestire il carico
            import math
            min_agents_for_load = math.ceil(traffic / concurrency)
            base_agents = max(base_agents, min_agents_for_load)
        else:
            # Voice standard (concurrency = 1)
            base_agents = self.required_agents(
                calls_per_interval, aht_seconds,
                service_level_target, target_seconds, interval_minutes
            )

        # Applica shrinkage: FTE = Agents / (1 - Shrinkage)
        if shrinkage >= 1.0:
            shrinkage = 0.30  # Default se valore invalido

        fte = base_agents / (1 - shrinkage)

        return round(fte, 2)

    def calculate_occupancy(self, traffic_intensity: float, agents: int) -> float:
        """
        Calcola occupancy effettiva

        Args:
            traffic_intensity: Intensità traffico in Erlang
            agents: Numero agenti

        Returns:
            Occupancy (0-1)
        """
        if agents <= 0:
            return 0.0

        occupancy = traffic_intensity / agents
        return min(max(occupancy, 0.0), 1.0)

    def calculate_interval_requirements(self,
                                       calls: float,
                                       config: Optional[Dict] = None) -> Dict:
        """
        Calcola tutti i requisiti per un intervallo temporale

        Args:
            calls: Numero chiamate/chat previste nell'intervallo
            config: Configurazione parametri (usa default se None)

        Returns:
            Dict con tutti i calcoli:
            - traffic_intensity: Erlang
            - required_agents: Agenti base necessari
            - required_fte: FTE con shrinkage
            - service_level: SL raggiunto
            - occupancy: Occupancy prevista
            - concurrency: Concurrency (per chat)
        """
        # Usa config fornita o default
        cfg = config if config else self.default_config

        aht = cfg.get('aht_seconds', self.default_config['aht_seconds'])
        shrinkage = cfg.get('shrinkage', self.default_config['shrinkage'])
        sl_target = cfg.get('service_level_target', self.default_config['service_level_target'])
        sl_seconds = cfg.get('service_level_seconds', self.default_config['service_level_seconds'])
        interval = cfg.get('interval_minutes', self.default_config['interval_minutes'])
        concurrency = cfg.get('concurrency', 1)

        # Calcola traffic intensity
        traffic = self.calculate_traffic_intensity(calls, aht, interval)

        # Calcola agenti necessari (considera concurrency se > 1)
        if concurrency > 1:
            effective_calls = calls / concurrency
            agents = self.required_agents(effective_calls, aht, sl_target, sl_seconds, interval)
            import math
            min_agents_for_load = math.ceil(traffic / concurrency)
            agents = max(agents, min_agents_for_load)
        else:
            agents = self.required_agents(calls, aht, sl_target, sl_seconds, interval)

        # Calcola FTE con shrinkage e concurrency
        fte = self.required_fte(calls, aht, sl_target, sl_seconds, shrinkage, interval, concurrency)

        # Calcola SL effettivo
        sl = self.service_level(agents, traffic, sl_seconds, aht)

        # Calcola occupancy
        occupancy = self.calculate_occupancy(traffic, agents)

        return {
            'traffic_intensity': round(traffic, 2),
            'required_agents': agents,
            'required_fte': fte,
            'service_level': round(sl * 100, 2),  # Come percentuale
            'occupancy': round(occupancy * 100, 2),  # Come percentuale
            'calls': calls,
            'aht_seconds': aht,
            'concurrency': concurrency
        }

    def calculate_daily_requirements(self,
                                    intervals_data: list,
                                    config: Optional[Dict] = None) -> Dict:
        """
        Calcola requisiti per un'intera giornata

        Args:
            intervals_data: Lista di dict con 'interval' e 'calls'
            config: Configurazione parametri

        Returns:
            Dict con calcoli per ogni intervallo e sommari giornalieri
        """
        results = []
        total_calls = 0
        peak_fte = 0

        for interval_data in intervals_data:
            calls = interval_data.get('calls', 0)
            interval_name = interval_data.get('interval', 'Unknown')

            # Calcola per questo intervallo
            req = self.calculate_interval_requirements(calls, config)
            req['interval'] = interval_name
            results.append(req)

            total_calls += calls
            peak_fte = max(peak_fte, req['required_fte'])

        return {
            'intervals': results,
            'total_calls': total_calls,
            'peak_fte': peak_fte,
            'average_fte': round(sum(r['required_fte'] for r in results) / len(results), 2) if results else 0
        }


# Funzioni helper per uso rapido
def quick_fte_calculation(calls: float, aht_seconds: int = 180,
                         shrinkage: float = 0.30) -> float:
    """
    Calcolo rapido FTE per un intervallo

    Args:
        calls: Numero chiamate
        aht_seconds: AHT in secondi (default 180 = 3 minuti)
        shrinkage: Shrinkage percentuale (default 0.30 = 30%)

    Returns:
        FTE necessari
    """
    calc = ErlangCalculator()
    return calc.required_fte(calls, aht_seconds, shrinkage=shrinkage)


def quick_service_level(agents: int, calls: float,
                       aht_seconds: int = 180) -> float:
    """
    Calcolo rapido Service Level

    Args:
        agents: Numero agenti disponibili
        calls: Chiamate nell'intervallo
        aht_seconds: AHT in secondi

    Returns:
        Service Level % (0-100)
    """
    calc = ErlangCalculator()
    traffic = calc.calculate_traffic_intensity(calls, aht_seconds)
    sl = calc.service_level(agents, traffic, 20, aht_seconds)
    return round(sl * 100, 2)


if __name__ == '__main__':
    # Test del modulo
    print("=== TEST ERLANG C CALCULATOR ===\n")

    calc = ErlangCalculator()

    # Scenario test: 100 chiamate/30min, AHT 3min
    calls = 100
    aht = 180

    print(f"Scenario: {calls} chiamate/30min, AHT {aht}s\n")

    # Calcola requisiti
    result = calc.calculate_interval_requirements(calls)

    print(f"Traffic Intensity: {result['traffic_intensity']} Erlang")
    print(f"Agenti necessari: {result['required_agents']}")
    print(f"FTE richiesti (con shrinkage 30%): {result['required_fte']}")
    print(f"Service Level atteso: {result['service_level']}%")
    print(f"Occupancy: {result['occupancy']}%")

    print("\n=== Test completato ===")
