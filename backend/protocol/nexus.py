from .schema import NXPPacket

class NexusEngine:
    """The core engine that translates between English and the Nexus Protocol."""
    
    # We use a hardcoded secret for the hackathon demo, in production this would be an env var
    HMAC_SECRET = "super_secret_enterprise_key"
    
    @staticmethod
    def decode_packet(packet_json: str) -> NXPPacket:
        """Takes an incoming NXP packet JSON and parses it, verifying the HMAC signature."""
        return NXPPacket.verify_and_parse(packet_json, NexusEngine.HMAC_SECRET)
