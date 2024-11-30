import logging
from tqdm import tqdm
from src.data_transfer_objects.chainV2 import ChainDTO
from src.data_transfer_objects.tokenV2 import TokenDTO  
from src.data_transfer_objects.trade_pair import PairDTO  

from itertools import product
import pickle
import os
import time
import pandas as pd
from itertools import permutations

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FLASHLOAN_ASSET_SYMBOLS = ['USDC', 'USDT', 'DAI', 'WETH']

def load_data(filename):
    if not os.path.exists(filename):
        logging.error(f"The file {filename} does not exist.")
        raise FileNotFoundError(f"The file {filename} does not exist.")
    
    logging.info(f"Loading data from {filename}...")
    with open(filename, "rb") as f:
        data = pickle.load(f)
    logging.info(f"Data loaded successfully from {filename}")
    return data
    

def fetch_and_store_data(network: ChainDTO):
    logging.info(f"Starting fetch_and_store_data for network: {network.network}")
    
    logging.info("Fetching AAVE supported asset data...")
    
    # asset_data_df = network.get_aave_supported_asset_data()
        # Save asset data to csv
    # asset_data_df.to_csv(f'aave_supported_asset_data_ethereum.csv', index=False)
    # # Load asset data from csv
    asset_data_df = pd.read_csv(f'aave_supported_asset_data_ethereum.csv')
    
    logging.info(f"AAVE supported asset data fetched. Shape: {asset_data_df.shape}")


    logging.info("Fetching user position data...")
    
    # user_position_df = network.get_user_position_data(asset_data=asset_data_df)
        # Save asset data to csv
    # user_position_df.to_csv(f'aave_user_position_data_ethereum.csv', index=False)
    # # Load asset data from csv
    user_position_df = pd.read_csv(f'aave_user_position_data_ethereum.csv')
    
    logging.info(f"User position data fetched. Shape: {user_position_df.shape}")
    
    asset_object_dict = {}

    logging.info("Processing asset data and creating TokenDTO objects...")
    for _, row in tqdm(asset_data_df.iterrows(), total=len(asset_data_df), desc="Creating TokenDTO objects"):
        token = TokenDTO(
            address=row['assetAddress'],
            name=row['symbol'],
            symbol=row['symbol'],
            decimals=row['decimals'],
            network=network,
            price=row['price'],
        )
        asset_object_dict[row['symbol']] = token

    logging.info("Creating PairDTO objects...")
    trade_pair_hashmap = {}
    
    # Filter asset_object_dict to only include tokens symbols in FLASHLOAN_ASSET_SYMBOLS
    primary_asset_object_dict = {symbol: token for symbol, token in asset_object_dict.items() if symbol in FLASHLOAN_ASSET_SYMBOLS}
    secondary_asset_object_dict = {symbol: token for symbol, token in asset_object_dict.items() if symbol not in FLASHLOAN_ASSET_SYMBOLS}

    total_pairs = len(primary_asset_object_dict) * (len(primary_asset_object_dict) - 1)
    for token1, token2 in tqdm(permutations(primary_asset_object_dict.values(), 2), total=total_pairs, desc="Creating Primary PairDTO objects"):
        pair_dto = PairDTO(
            sell_token=token1,
            buy_token=token2,
            network=network
        )
        key = f"{token1.symbol}-{token2.symbol}"
        trade_pair_hashmap[key] = pair_dto

    total_pairs = len(primary_asset_object_dict) * len(secondary_asset_object_dict)
    for primary_token, secondary_token in tqdm(product(primary_asset_object_dict.values(), secondary_asset_object_dict.values()), total=total_pairs, desc="Creating PairDTO objects P <> S"):
        
        # Create pair from primary to secondary
        pair_dto_primary_to_secondary = PairDTO(
            sell_token=primary_token,
            buy_token=secondary_token,
            network=network
        )
        key_primary_to_secondary = f"{primary_token.symbol}-{secondary_token.symbol}"
        trade_pair_hashmap[key_primary_to_secondary] = pair_dto_primary_to_secondary

        # Create pair from secondary to primary
        pair_dto_secondary_to_primary = PairDTO(
            sell_token=secondary_token,
            buy_token=primary_token,
            network=network
        )
        key_secondary_to_primary = f"{secondary_token.symbol}-{primary_token.symbol}"
        trade_pair_hashmap[key_secondary_to_primary] = pair_dto_secondary_to_primary


    def save_data(filename):
        DATA_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pickle_data')
        os.makedirs(DATA_STORE_DIR, exist_ok=True)
        filepath = os.path.join(DATA_STORE_DIR, filename)
        logging.info(f"Saving data to {filepath}...")
        data_to_save = {
            "network": network.network,
            "batch_data_provider_address": network.batch_data_provider_address,
            "aave_pool_address": network.aave_pool_address,
            "aave_data_provider_address": network.aave_data_provider_address,
            "holder_query_id": network.holder_query_id,
            "user_position_df": user_position_df,
            "asset_data_df": asset_data_df,
            "asset_object_dict": asset_object_dict,
            "trade_pair_hashmap": trade_pair_hashmap
        }
        with open(filepath, "wb") as f:
            pickle.dump(data_to_save, f)
        logging.info(f"Data has been saved to {filepath}")

    current_timestamp = int(time.time())
    save_data(f"aave_data_{network.network.lower()}_{current_timestamp}.pkl")
    logging.info("fetch_and_store_data completed successfully")

# def fetch_and_store_data(network: ChainDTO):
#     logging.info(f"Starting fetch_and_store_data for network: {network.network}")
    
#     # Define paths for storing intermediate data
#     DATA_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pickle_data')
#     os.makedirs(DATA_STORE_DIR, exist_ok=True)
#     intermediate_data_path = os.path.join(DATA_STORE_DIR, f"intermediate_data_{network.network.lower()}.pkl")
    
#     # Load intermediate data if it exists
#     if os.path.exists(intermediate_data_path):
#         with open(intermediate_data_path, 'rb') as f:
#             intermediate_data = pickle.load(f)
#         logging.info(f"Loaded intermediate data from {intermediate_data_path}")
#     else:
#         intermediate_data = {
#             'asset_data_df': None,
#             'user_position_df': None,
#             'asset_object_dict': {},
#             'trade_pair_hashmap': {}
#         }

#     # Fetch AAVE supported asset data if not already present
#     if intermediate_data['asset_data_df'] is None:
#         logging.info("Fetching AAVE supported asset data...")
#         asset_data_df = pd.read_csv(f'aave_supported_asset_data_ethereum.csv')
#         intermediate_data['asset_data_df'] = asset_data_df
#         save_intermediate_data(intermediate_data, intermediate_data_path)
#     else:
#         asset_data_df = intermediate_data['asset_data_df']
#     logging.info(f"AAVE supported asset data fetched. Shape: {asset_data_df.shape}")

#     # Fetch user position data if not already present
#     if intermediate_data['user_position_df'] is None:
#         logging.info("Fetching user position data...")
#         user_position_df = pd.read_csv(f'aave_user_position_data_ethereum.csv')
#         intermediate_data['user_position_df'] = user_position_df
#         save_intermediate_data(intermediate_data, intermediate_data_path)
#     else:
#         user_position_df = intermediate_data['user_position_df']
#     logging.info(f"User position data fetched. Shape: {user_position_df.shape}")

#     # Create TokenDTO objects
#     asset_object_dict = intermediate_data['asset_object_dict']
#     logging.info("Processing asset data and creating TokenDTO objects...")
#     for _, row in tqdm(asset_data_df.iterrows(), total=len(asset_data_df), desc="Creating TokenDTO objects", leave=True):
#         if row['symbol'] not in asset_object_dict:
#             token = TokenDTO(
#                 address=row['assetAddress'],
#                 name=row['symbol'],
#                 symbol=row['symbol'],
#                 decimals=row['decimals'],
#                 network=network,
#                 price=row['price'],
#             )
#             asset_object_dict[row['symbol']] = token
#     save_intermediate_data(intermediate_data, intermediate_data_path)

#     # Filter asset_object_dict
#     primary_asset_object_dict = {symbol: token for symbol, token in asset_object_dict.items() if symbol in FLASHLOAN_ASSET_SYMBOLS}
#     secondary_asset_object_dict = {symbol: token for symbol, token in asset_object_dict.items() if symbol not in FLASHLOAN_ASSET_SYMBOLS}

#     # Create PairDTO objects
#     trade_pair_hashmap = intermediate_data['trade_pair_hashmap']
#     logging.info("Creating PairDTO objects...")

#     def create_pair_dto(token1, token2):
#         key = f"{token1.symbol}-{token2.symbol}"
#         if key not in trade_pair_hashmap:
#             try:
#                 pair_dto = PairDTO(sell_token=token1, buy_token=token2, network=network)
#                 trade_pair_hashmap[key] = pair_dto
#                 return True
#             except Exception as e:
#                 logging.error(f"Error creating PairDTO for {key}: {str(e)}")
#         return False

#     # Primary to Primary pairs
#     total_pairs = len(primary_asset_object_dict) * (len(primary_asset_object_dict) - 1)
#     primary_pairs = list(permutations(primary_asset_object_dict.values(), 2))
#     created_count = 0
#     for token1, token2 in tqdm(primary_pairs, total=total_pairs, desc="Creating Primary PairDTO objects", leave=True):
#         if create_pair_dto(token1, token2):
#             created_count += 1
#         if created_count % 10 == 0:  # Save every 10 new pairs
#             save_intermediate_data(intermediate_data, intermediate_data_path)

#     # Primary to Secondary pairs
#     total_pairs = len(primary_asset_object_dict) * len(secondary_asset_object_dict)
#     all_pairs = list(product(primary_asset_object_dict.values(), secondary_asset_object_dict.values()))
#     created_count = 0
#     for primary_token, secondary_token in tqdm(all_pairs, total=total_pairs, desc="Creating PairDTO objects P <> S", leave=True):
#         if create_pair_dto(primary_token, secondary_token):
#             created_count += 1
#         if create_pair_dto(secondary_token, primary_token):
#             created_count += 1
#         if created_count % 20 == 0:  # Save every 20 new pairs
#             save_intermediate_data(intermediate_data, intermediate_data_path)

#     # Save final data
#     current_timestamp = int(time.time())
#     final_filename = f"aave_data_{network.network.lower()}_{current_timestamp}.pkl"
#     save_final_data(network, user_position_df, asset_data_df, asset_object_dict, trade_pair_hashmap, final_filename)
#     logging.info("fetch_and_store_data completed successfully")

#     # Remove intermediate data file
#     os.remove(intermediate_data_path)
#     logging.info(f"Removed intermediate data file: {intermediate_data_path}")

# def save_intermediate_data(data, filepath):
#     with open(filepath, 'wb') as f:
#         pickle.dump(data, f)
#     logging.info(f"Saved intermediate data to {filepath}")

# def save_final_data(network, user_position_df, asset_data_df, asset_object_dict, trade_pair_hashmap, filename):
#     DATA_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pickle_data')
#     filepath = os.path.join(DATA_STORE_DIR, filename)
#     logging.info(f"Saving final data to {filepath}...")
#     data_to_save = {
#         "network": network.network,
#         "batch_data_provider_address": network.batch_data_provider_address,
#         "aave_pool_address": network.aave_pool_address,
#         "aave_data_provider_address": network.aave_data_provider_address,
#         "holder_query_id": network.holder_query_id,
#         "user_position_df": user_position_df,
#         "asset_data_df": asset_data_df,
#         "asset_object_dict": asset_object_dict,
#         "trade_pair_hashmap": trade_pair_hashmap
#     }
#     with open(filepath, "wb") as f:
#         pickle.dump(data_to_save, f)
#     logging.info(f"Final data has been saved to {filepath}")