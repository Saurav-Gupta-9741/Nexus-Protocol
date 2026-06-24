from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .benchmark import BenchmarkEngine
from .protocol.nexus import NexusEngine
from .agents.agent import NexusAgent

app = FastAPI(title="Nexus Protocol Engine")

# Allow the Next.js frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BenchmarkRequest(BaseModel):
    english_text: str

@app.post("/api/benchmark")
async def run_benchmark(req: BenchmarkRequest):
    """
    Receives an English intent, runs it through the real Multi-Agent System (Agent A -> Agent B),
    and returns a side-by-side benchmark comparison.
    """
    english_msg = req.english_text
    
    # 1. Instantiate the real agents
    agent_a = NexusAgent(agent_id="AGENT_A")
    agent_b = NexusAgent(agent_id="AGENT_B")
    
    # 2. Agent A compresses the intent into NXP via Ollama
    nxp_packet_str, llm_trace = agent_a.receive_english_task_and_send_packet(
        task_description=english_msg, 
        target_agent="AGENT_B"
    )
    
    # 3. Agent B receives and deterministically decodes the packet
    # (In a true distributed system, this would happen over a network socket)
    decoded_task = agent_b.receive_nxp_packet(nxp_packet_str)
    
    # 4. Calculate the massive token and latency savings
    # (We only measure the LLM packet size, not the raw network data attached to it)
    llm_packet_only = nxp_packet_str.split("||PAYLOAD:")[0] if "||PAYLOAD:" in nxp_packet_str else nxp_packet_str
    
    is_cache_hit = "Cache Hit" in llm_trace["system_prompt"]
    results = BenchmarkEngine.run_comparison(english_msg, llm_packet_only, is_cache_hit)
    
    # Return the metrics payload for the Mission Control dashboard
    return {
        "original_english": english_msg,
        "nexus_packet": nxp_packet_str,
        "decoded_payload": decoded_task,
        "metrics": results,
        "llm_trace": llm_trace
    }
