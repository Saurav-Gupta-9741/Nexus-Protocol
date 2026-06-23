from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .benchmark import BenchmarkEngine
from .protocol.nexus import NexusEngine

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
    Receives an English intent, compresses it into NXP,
    and returns a side-by-side benchmark comparison.
    """
    english_msg = req.english_text
    
    # Agent A compresses the intent into NXP
    nxp_packet_str = NexusEngine.encode_intent(
        sender="AGENT_A", 
        receiver="AGENT_B", 
        intent_description=english_msg
    )
    
    # Calculate the massive token and latency savings
    results = BenchmarkEngine.run_comparison(english_msg, nxp_packet_str)
    
    # Return the metrics payload for the Mission Control dashboard
    return {
        "original_english": english_msg,
        "nexus_packet": nxp_packet_str,
        "metrics": results
    }
