import time

class BenchmarkEngine:
    @staticmethod
    def calculate_english_cost(text: str) -> dict:
        """Simulates the cost of an LLM generating and parsing English text."""
        # Rough estimation: 1 token = ~4 characters
        tokens = max(1, len(text) // 4)
        # Simulated slow agent generation/reading: ~0.02 seconds per token
        latency = tokens * 0.02
        # Cost estimate: $0.00002 per token (input+output)
        cost = tokens * 0.00002
        return {"tokens": tokens, "latency": round(latency, 3), "cost": cost}

    @staticmethod
    def calculate_nxp_cost(packet_str: str) -> dict:
        """Simulates the near-zero cost of sending a deterministic NXP packet."""
        # NXP packets are dense
        tokens = max(1, len(packet_str) // 4)
        # NXP parsing latency is sub-millisecond, plus minimal network hop
        latency = 0.005 
        cost = tokens * 0.00002
        return {"tokens": tokens, "latency": round(latency, 3), "cost": cost}

    @staticmethod
    def run_comparison(english_text: str, nxp_packet: str) -> dict:
        eng_metrics = BenchmarkEngine.calculate_english_cost(english_text)
        nxp_metrics = BenchmarkEngine.calculate_nxp_cost(nxp_packet)
        
        token_savings = 1 - (nxp_metrics["tokens"] / eng_metrics["tokens"])
        time_savings = 1 - (nxp_metrics["latency"] / eng_metrics["latency"])
        
        return {
            "english": eng_metrics,
            "nexus": nxp_metrics,
            "savings": {
                "tokens_percent": round(token_savings * 100, 2),
                "time_percent": round(time_savings * 100, 2)
            }
        }
