"""RIPZ: Zero-copy IPC binary protocol"""
import struct
import hashlib
from typing import Dict, Any
from enum import IntEnum
import json

class FrameType(IntEnum):
    STATE_SNAPSHOT = 0x01
    DELTA_UPDATE = 0x02
    CATALYST_ACTION = 0x03
    HEALTH_PULSE = 0x04
    SYNC_REQUEST = 0x05
    CYU_TRANSMISSION = 0x06

class RIPZEncoder:
    """Encode messages to RIPZ binary format"""
    
    @staticmethod
    def encode(frame_type: FrameType, seq: int, timestamp: int, payload: Dict[str, Any]) -> bytes:
        """
        Wire format:
        [FRAME_TYPE:1][SEQ:4][TIMESTAMP:8][PAYLOAD_LEN:4][PAYLOAD:N][CHECKSUM:4]
        """
        payload_json = json.dumps(payload).encode('utf-8')
        payload_len = len(payload_json)
        
        header = struct.pack(
            '!BIQ',
            int(frame_type),
            seq,
            timestamp
        )
        
        length_field = struct.pack('!I', payload_len)
        
        # Checksum (CRC32 of payload)
        checksum = struct.pack('!I', RIPZEncoder._crc32(payload_json))
        
        frame = header + length_field + payload_json + checksum
        return frame
    
    @staticmethod
    def _crc32(data: bytes) -> int:
        import zlib
        return zlib.crc32(data) & 0xffffffff

class RIPZDecoder:
    """Decode RIPZ binary frames"""
    
    @staticmethod
    def decode(frame: bytes) -> tuple[FrameType, int, int, Dict[str, Any]]:
        """
        Returns: (frame_type, seq, timestamp, payload)
        """
        if len(frame) < 17:  # Minimum: 1+4+8+4+0+4
            raise ValueError("Frame too short")
        
        frame_type, seq, timestamp = struct.unpack('!BIQ', frame[:13])
        payload_len = struct.unpack('!I', frame[13:17])[0]
        
        if len(frame) < 17 + payload_len + 4:
            raise ValueError("Incomplete frame")
        
        payload_json = frame[17:17+payload_len]
        checksum = struct.unpack('!I', frame[17+payload_len:17+payload_len+4])[0]
        
        # Verify checksum
        expected_crc = RIPZEncoder._crc32(payload_json)
        if checksum != expected_crc:
            raise ValueError(f"Checksum mismatch: {checksum} != {expected_crc}")
        
        payload = json.loads(payload_json.decode('utf-8'))
        return FrameType(frame_type), seq, timestamp, payload
