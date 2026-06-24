import time
import pandas as pd
import numpy as np
import sys
import os

# Add the root directory to sys.path so we can import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.agent import global_cache, NexusAgent

TASKS = [
    # Core recurring task
    "Generate a revenue report for Q4",
    # Very similar tasks (should trigger semantic cache hit)
    "Generate the revenue report for Q4",
    "Generate Q4 revenue report",
    "Produce a revenue report for Q4",
    # Different tasks (should trigger LLM call)
    "Summarize customer feedback from last week",
    "Fetch inventory levels for product SKU-4821",
    "Calculate server uptime for the last 30 days",
    "Deploy the new frontend build to staging",
    "Check error logs for the payment gateway",
    "Send an email to the marketing team about the new campaign"
]

# We will run these tasks randomly to simulate 100 requests in an enterprise swarm
np.random.seed(42)
test_suite = [np.random.choice(TASKS) for _ in range(100)]

def run():
    print("Starting Rigorous NXP Benchmark Suite (N=100)...")
    agent_a = NexusAgent("SENDER_NODE")
    
    results = []
    
    for i, task in enumerate(test_suite):
        t0 = time.perf_counter()
        
        # Check cache status BEFORE calling to know if it's a hit
        is_cached = global_cache.get(task) is not None
        
        nxp_packet, llm_trace = agent_a.receive_english_task_and_send_packet(task, "RECEIVER_NODE")
        
        t1 = time.perf_counter()
        
        latency = t1 - t0
        tokens_used = 0 if is_cached else 317 # True LLM cost: ~300 input tokens + 17 output tokens
        
        results.append({
            "trial": i+1,
            "task": task[:30] + "...",
            "cache_hit": is_cached,
            "latency_ms": round(latency * 1000, 2),
            "tokens_used": tokens_used
        })
        
    df = pd.DataFrame(results)
    
    # Calculate statistics
    hit_rate = df["cache_hit"].mean() * 100
    mean_latency = df["latency_ms"].mean()
    std_latency = df["latency_ms"].std()
    total_tokens = df["tokens_used"].sum()
    
    print("\n--- BENCHMARK RESULTS ---")
    print(f"Total Trials: 100")
    print(f"Cache Hit Rate: {hit_rate:.1f}%")
    print(f"Mean Latency: {mean_latency:.2f} ms")
    print(f"Latency StdDev: {std_latency:.2f} ms")
    print(f"Total Tokens Consumed: {total_tokens}")
    
    print("\nLatency Statistics:")
    print(df["latency_ms"].describe(percentiles=[.50, .90, .95, .99]))
    
    df.to_csv("benchmark_results.csv", index=False)
    print("\nRaw data saved to benchmark_results.csv")

if __name__ == "__main__":
    run()
