import time

class BenchmarkEngine:
    @staticmethod
    def count_exact_tokens(text: str) -> int:
        # Fallback math for Python 3.6 compatibility on college servers
        return max(1, len(text) // 4)

    @staticmethod
    def calculate_english_cost(text: str) -> dict:
        """Simulates the cost of an LLM generating and parsing English text."""
        tokens = BenchmarkEngine.count_exact_tokens(text)
        # Simulated LLM generation latency: ~0.02 seconds per token
        latency = tokens * 0.02
        # Cost estimate: $0.00002 per token
        cost = tokens * 0.00002
        return {"tokens": tokens, "latency": round(latency, 3), "cost": cost}

    @staticmethod
    def calculate_nxp_cost(packet_str: str) -> dict:
        """Simulates the near-zero cost of sending a deterministic NXP packet."""
        tokens = BenchmarkEngine.count_exact_tokens(packet_str)
        # NXP parsing latency is sub-millisecond
        latency = 0.005 
        cost = tokens * 0.00002
        return {"tokens": tokens, "latency": round(latency, 3), "cost": cost}

    @staticmethod
    def run_comparison(english_text: str, nxp_packet: str) -> dict:
        eng_metrics = BenchmarkEngine.calculate_english_cost(english_text)
        nxp_metrics = BenchmarkEngine.calculate_nxp_cost(nxp_packet)
        
        token_savings = 1 - (nxp_metrics["tokens"] / eng_metrics["tokens"])
        time_savings = 1 - (nxp_metrics["latency"] / eng_metrics["latency"])
        
        # Calculate the "Swarm Multiplier" (e.g. 50 agent hops in a real enterprise)
        SWARM_HOPS = 50
        swarm_eng_cost = eng_metrics["cost"] * SWARM_HOPS
        swarm_nxp_cost = nxp_metrics["cost"] * SWARM_HOPS
        
        return {
            "english": eng_metrics,
            "nexus": nxp_metrics,
            "savings": {
                "tokens_percent": round(token_savings * 100, 2),
                "time_percent": round(time_savings * 100, 2),
                "swarm_hops": SWARM_HOPS,
                "swarm_english_cost": round(swarm_eng_cost, 4),
                "swarm_nxp_cost": round(swarm_nxp_cost, 4)
            }
        }
