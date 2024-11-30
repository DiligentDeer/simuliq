from dataclasses import dataclass
from typing import Optional

class RateLimitExceededException(Exception):
    """Exception raised for rate limit exceeded (429 Too Many Requests)."""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after

@dataclass(frozen=True, order=True)
class ChainDTO:
    """
    Data Transfer Object to store relevant chain data.
    
    Attributes:
        network (str): The network name
        network_id (int): The network identifier
        rpc_url (str): The RPC endpoint URL
    """

    network: str
    network_id: int
    rpc_url: str
    
    def __str__(self):
        return self.network
            
    def __repr__(self):
        return f"ChainDTO(network='{self.network}', network_id={self.network_id})"