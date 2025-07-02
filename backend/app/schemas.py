from pydantic import BaseModel, field_validator
import ipaddress


class PingOutput(BaseModel):
    address: str
    packet_loss: int | None
    avg_ping_ms: float | None


class HostAddressInput(BaseModel):
    value: str

    @field_validator("value")
    @classmethod
    def verify_ip_address(cls, value: str):
        try:
            verified = ipaddress.IPv4Address(value)
            return str(verified)
        except:
            raise ValueError(f"Этот адрес невалиден: {value}")
