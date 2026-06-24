from pydantic import BaseModel, Field
from typing import Any
import time
import hmac
import hashlib
import json

class NXPPacket(BaseModel):
    """
    Enterprise-grade M2M Packet Schema using Pydantic.
    Features: Dynamic JSON params, HMAC-SHA256 signing, and TTL expiration.
    """
    version: str = "2.0"
    msg_id: str = Field(default_factory=lambda: str(time.time()))
    timestamp: float = Field(default_factory=time.time)
    sender: str
    receiver: str
    params: dict[str, Any] = Field(default_factory=dict) # LLM generates freely, no enums
    payload_ref: str | None = None
    ttl: int = 300 # seconds before packet expires
    checksum: str = "" # SHA-256 HMAC signature

    def sign(self, secret: str):
        # Create a dict without checksum for signing
        data = self.model_dump(exclude={"checksum"})
        data_str = json.dumps(data, sort_keys=True)
        self.checksum = hmac.new(secret.encode(), data_str.encode(), hashlib.sha256).hexdigest()
        return self

    @classmethod
    def verify_and_parse(cls, raw_json: str, secret: str):
        data = json.loads(raw_json)
        provided_checksum = data.get("checksum", "")
        
        # Verify HMAC
        check_data = {k: v for k, v in data.items() if k != "checksum"}
        data_str = json.dumps(check_data, sort_keys=True)
        expected_checksum = hmac.new(secret.encode(), data_str.encode(), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(provided_checksum, expected_checksum):
            raise ValueError("Packet checksum mismatch - possible tampering")
            
        pkt = cls(**data)
        if time.time() - pkt.timestamp > pkt.ttl:
            raise ValueError(f"Packet expired")
            
        return pkt
