from .llm_client import OllamaClient
from ..protocol.nexus import NexusEngine
import json
import logging

logger = logging.getLogger(__name__)

class NexusAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.llm = OllamaClient()

    def receive_english_task_and_send_packet(self, task_description: str, target_agent: str) -> str:
        """
        Agent A receives an English task, thinks using Llama 3.1, and returns an NXP packet.
        """
        logger.info(f"[{self.agent_id}] Received English task. Using LLM to compress into NXP...")
        
        # We instruct the LLM to act as the Nexus Protocol Encoder
        system_prompt = (
            "You are a Nexus Protocol Encoder AI. Your ONLY job is to take an English task description "
            "and convert it into a deterministic NXP packet. "
            "The format MUST be strictly: [NX:MSG|FROM:{sender}|TO:{receiver}|ACT:{action}|CTX:{context}|VAL:{value}]\n"
            "ACT should be a single word like 'GEN_REPORT', 'CALCULATE', 'STORE'.\n"
            "CTX should be a single word context.\n"
            "VAL should be the extracted numerical value or primary entity.\n"
            "DO NOT OUTPUT ANYTHING EXCEPT THE BRACKETED PACKET. NO EXPLANATIONS."
        )
        
        prompt = system_prompt + f"\n\nSender: {self.agent_id}\nReceiver: {target_agent}\nTask: {task_description}"
        
        # Send to Ollama
        nxp_packet = self.llm.generate(prompt)
        
        # Clean up any hallucinations just in case
        if "[" in nxp_packet and "]" in nxp_packet:
            nxp_packet = nxp_packet[nxp_packet.find("["):nxp_packet.rfind("]")+1]
        else:
            # Absolute fallback if LLM breaks formatting
            nxp_packet = f"[NX:MSG|FROM:{self.agent_id}|TO:{target_agent}|ACT:UNKNOWN|CTX:null|VAL:null]"
            
        return nxp_packet

    def receive_nxp_packet(self, nxp_packet: str) -> dict:
        """
        Agent B receives an NXP packet and decodes it deterministically without needing an LLM.
        """
        logger.info(f"[{self.agent_id}] Received NXP packet. Decoding deterministically...")
        decoded_intent = NexusEngine.decode_packet(nxp_packet)
        return decoded_intent
