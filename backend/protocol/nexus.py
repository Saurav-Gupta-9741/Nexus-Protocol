from .schema import NxpPacket
from backend.agents.llm_client import OllamaClient

class NexusEngine:
    """The core engine that translates between English and the Nexus Protocol."""
    
    @staticmethod
    def encode_intent(sender: str, receiver: str, intent_description: str) -> str:
        """
        Uses the local LLM (Ollama on the College GPU) to compress the english intent into an NXP packet.
        """
        client = OllamaClient()
        
        system_prompt = f"""
        You are the Nexus Protocol (NXP) encoding engine.
        Convert the user's English intent into a single NXP packet.
        Format: [NX:<TYPE>|FROM:{sender}|TO:{receiver}|ACT:<ACTION>|CTX:<CONTEXT>|VAL:<VALUE>]
        Types: REQ, MSG. Keep it under 6 tokens.
        Do NOT reply with anything other than the exact bracketed packet.
        """
        
        nxp_packet = client.generate(prompt=intent_description, system_prompt=system_prompt)
        
        # Ensure it's cleanly formatted just in case the LLM adds text
        nxp_packet = nxp_packet.strip()
        if not nxp_packet.startswith("[NX:"):
            # Fallback format protection
            packet = NxpPacket("MSG", sender, receiver, "UNKNOWN", "general", "data")
            return packet.serialize()
            
        return nxp_packet

    @staticmethod
    def decode_packet(packet_str: str) -> NxpPacket:
        """Takes an incoming NXP packet string and parses it into an object."""
        return NxpPacket.parse(packet_str)
