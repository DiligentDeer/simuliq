from dataclasses import dataclass


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
    