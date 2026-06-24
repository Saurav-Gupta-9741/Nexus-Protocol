from .llm_client import GroqClient
from ..protocol.nexus import NexusEngine
from ..protocol.schema import NXPPacket
import json
import logging
import base64
import hashlib

logger = logging.getLogger(__name__)

from sentence_transformers import SentenceTransformer, util
import torch

class VectorTierCache:
    """True Semantic Cache using Dense Vector Embeddings (MiniLM + Cosine Similarity)."""
    def __init__(self, threshold=0.85):
        self.threshold = threshold
        self.tasks = []
        self.packets = []
        # Load lightweight, lightning-fast embedding model (Runs locally for free)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.task_embeddings = None
        
    def get(self, task: str):
        if not self.tasks:
            return None
            
        # Dense Vector Similarity Check
        query_embedding = self.model.encode(task, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, self.task_embeddings)[0]
        
        best_idx = torch.argmax(cos_scores).item()
        
        if cos_scores[best_idx].item() >= self.threshold:
            return self.packets[best_idx]
            
        return None
        
    def set(self, task: str, packet: str):
        self.tasks.append(task)
        self.packets.append(packet)
        self.task_embeddings = self.model.encode(self.tasks, convert_to_tensor=True)

# Global cache instance
global_cache = VectorTierCache()

class NexusAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.llm = GroqClient()

    def receive_english_task_and_send_packet(self, task_description: str, target_agent: str) -> str:
        """
        Agent A receives an English task, checks the Semantic Cache, and returns an NXP JSON packet.
        """
        logger.info(f"[{self.agent_id}] Received English task. Checking Semantic Cache...")
        
        # 1. TIER CACHE CHECK (Zero Cost LLM Bypassing)
        cached_packet = global_cache.get(task_description)
        if cached_packet:
            logger.info(f"[{self.agent_id}] CACHE HIT! Bypassing Groq LLM entirely.")
            llm_trace = {
                "system_prompt": "N/A (Cache Hit)",
                "user_prompt": "N/A (Cache Hit)",
                "raw_output": f"CACHE_HIT: {cached_packet}"
            }
            return cached_packet, llm_trace
            
        logger.info(f"[{self.agent_id}] Cache Miss. Calling Groq Llama 3.3...")
        
        # OFFLOAD MASSIVE PAYLOADS (Stateless Network Architecture)
        original_task = task_description
        base64_payload = None
        if len(task_description) > 500:
            base64_payload = base64.b64encode(task_description.encode('utf-8')).decode('utf-8')
            task_description = f"Offloaded massive payload. Set payload_ref to ATTACHED"
        
        # We instruct the LLM to act as the Nexus Protocol Encoder generating JSON
        system_prompt = (
            "You are a Nexus Protocol Encoder AI. Your ONLY job is to take an English task description "
            "and extract the parameters into a JSON object. "
            "You must output ONLY valid JSON matching this structure: \n"
            "{\n"
            '  "params": { "action": "...", "context": "..." },\n'
            '  "payload_ref": null\n'
            "}\n"
            "You may invent any keys inside 'params' to fit the task dynamically. No fixed enums.\n"
            "DO NOT OUTPUT ANYTHING EXCEPT THE JSON. NO EXPLANATIONS."
        )
        
        prompt = system_prompt + f"\n\nTask: {task_description}"
        
        # Send to LLM
        raw_json_str = self.llm.generate(prompt)
        
        # Clean up hallucinations
        if "{" in raw_json_str and "}" in raw_json_str:
            raw_json_str = raw_json_str[raw_json_str.find("{"):raw_json_str.rfind("}")+1]
        else:
            raw_json_str = '{"params": {"action": "UNKNOWN"}}'
            
        # Build the Pydantic packet
        try:
            parsed_data = json.loads(raw_json_str)
            packet = NXPPacket(
                sender=self.agent_id,
                receiver=target_agent,
                params=parsed_data.get("params", {}),
                payload_ref=parsed_data.get("payload_ref")
            )
        except Exception:
            packet = NXPPacket(sender=self.agent_id, receiver=target_agent, params={"error": "LLM output invalid"})
            
        # Sign the packet with HMAC
        packet.sign(NexusEngine.HMAC_SECRET)
        
        # Convert to string for network transport
        nxp_packet = packet.model_dump_json()
        
        # Cache the result for future zero-cost hits
        global_cache.set(original_task, nxp_packet)
        
        llm_trace = {
            "system_prompt": system_prompt,
            "user_prompt": f"Task: {task_description}",
            "raw_output": raw_json_str
        }
        
        # Attach the massive payload directly to the network string
        if base64_payload:
            nxp_packet = f"{nxp_packet}||PAYLOAD:{base64_payload}"
            
        return nxp_packet, llm_trace

    def receive_nxp_packet(self, nxp_packet: str) -> dict:
        """
        Agent B receives an NXP JSON packet, verifies HMAC, and decodes it gracefully.
        """
        logger.info(f"[{self.agent_id}] Received NXP network stream. Verifying HMAC and decoding...")
        
        fetched_memory = None
        
        # 1. Strip the payload off the packet string before parsing
        if "||PAYLOAD:" in nxp_packet:
            packet_part, payload_part = nxp_packet.split("||PAYLOAD:", 1)
            nxp_packet = packet_part
            fetched_memory = base64.b64decode(payload_part).decode('utf-8')
            
        # 2. Pydantic Parse and HMAC Verification
        try:
            decoded_intent = NexusEngine.decode_packet(nxp_packet)
        except Exception as e:
            logger.warning(f"[{self.agent_id}] Packet validation failed: {e}. Falling back to LLM decoder...")
            return {
                "error": str(e),
                "params": {"action": "FALLBACK_TRIGGERED"},
                "fetched_memory": fetched_memory
            }
            
        return {
            "params": decoded_intent.params,
            "payload_ref": decoded_intent.payload_ref,
            "fetched_memory": fetched_memory
        }
