import json
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class NxpPacket:
    type: str       # REQ, RES, MSG, ERR, ACK
    sender: str     # FROM: Agent ID
    receiver: str   # TO: Agent ID
    action: str = ""     # ACT: Action code
    context: str = ""    # CTX: Short context/topic
    value: str = ""      # VAL: The dense payload
    
    def serialize(self) -> str:
        """Serializes the packet to the ultra-compressed NXP format."""
        parts = [f"NX:{self.type}", f"FROM:{self.sender}", f"TO:{self.receiver}"]
        if self.action: parts.append(f"ACT:{self.action}")
        if self.context: parts.append(f"CTX:{self.context}")
        if self.value: parts.append(f"VAL:{self.value}")
        return f"[{'|'.join(parts)}]"
    
    @classmethod
    def parse(cls, packet_str: str) -> 'NxpPacket':
        """Parses an NXP format string back into a Packet object."""
        packet_str = packet_str.strip()
        if not (packet_str.startswith('[') and packet_str.endswith(']')):
            raise ValueError("Invalid NXP format. Must be enclosed in []")
        
        inner = packet_str[1:-1]
        parts = inner.split('|')
        
        data = {
            'type': '', 'sender': '', 'receiver': '',
            'action': '', 'context': '', 'value': ''
        }
        
        for part in parts:
            if ':' not in part: continue
            k, v = part.split(':', 1)
            if k == 'NX': data['type'] = v
            elif k == 'FROM': data['sender'] = v
            elif k == 'TO': data['receiver'] = v
            elif k == 'ACT': data['action'] = v
            elif k == 'CTX': data['context'] = v
            elif k == 'VAL': data['value'] = v
            
        return cls(**data)
