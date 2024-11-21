from dataclasses import dataclass
from src.models.chain import ChainDTO

@dataclass()
class ProtocolDTO:
    """
    Data Transfer Object to store relevant protocol data.
    
    Attributes:
        chain (ChainDTO): The chain information
        protocol (str): The protocol name
    """

    chain: ChainDTO
    protocol: str
