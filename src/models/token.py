"""Simple DTO for token data."""
from dataclasses import dataclass, field
from src.models.chain import ChainDTO, RateLimitExceededException

from web3 import Web3, HTTPProvider
import pandas as pd
from requests import get, post
import time
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional, Union
from functools import lru_cache
import logging

        
        
SUPPLY_ABI = [{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]


@dataclass()
class TokenDTO:
    """
    Data Transfer Object to store relevant
    token data.
    """

    address: str
    name: str
    symbol: str
    decimals: int
    chain: ChainDTO
    price: Optional[float] = None
    supply: Optional[int] = None
    mcap: Optional[float] = None
    timestamp: Optional[int] = None
    
    def __post_init__(self):
        if self.price is None:
            self.price = self.get_current_price()
        
        if self.supply is None:
            self.supply = self.get_supply()/10**self.decimals
        
        if self.mcap is None:
            self.mcap = self.price * self.supply
        
        
    def get_supply(self, block_number=None):
        if not self.chain.rpc_url:
            raise ValueError(f"RPC URL is not set for {self.chain.network}")
    
        try:
            W3 = Web3(HTTPProvider(self.chain.rpc_url))
            contract = W3.eth.contract(address=Web3.to_checksum_address(self.address), abi=SUPPLY_ABI)
            contract_function = getattr(contract.functions, "totalSupply")
            
            if block_number is not None:
                data = contract_function().call(block_identifier=int(block_number))
            else:
                data = contract_function().call()
            
            return data
        except Exception as e:
            raise Exception(f'Error querying smart contract: {e}')
        
        
    def get_current_price(self) -> Optional[float]:
        """
        Fetches the current price of a token from the Coin Llama API and extracts the price.

        Args:
            token_address (str): The address of the token.

        Returns:
            Optional[float]: The current price of the token or None if an error occurs.
        """
        base_url = "https://coins.llama.fi/prices/current"
        url = f"{base_url}/{self.chain.network}:{self.address}?searchWidth=12h"
        
        response = get(url)
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            raise RateLimitExceededException("Rate limit exceeded.", retry_after=int(retry_after) if retry_after else None)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        price_info = data.get('coins', {}).get(f'{self.chain.network}:{self.address}', {})
        return price_info.get('price')