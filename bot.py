from web3 import Web3
from eth_utils import to_hex
from eth_abi.abi import encode
from eth_account import Account
from eth_account.messages import encode_defunct
from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, secrets, json, time, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class PharosTestnet:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://testnet.pharosnetwork.xyz",
            "Referer": "https://testnet.pharosnetwork.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.pharosnetwork.xyz"
        self.RPC_URL = "https://testnet.dplabs-internal.com"
        self.WPHRS_CONTRACT_ADDRESS = "0x76aaaDA469D23216bE5f7C596fA25F282Ff9b364"
        self.USDC_CONTRACT_ADDRESS = "0xAD902CF99C2dE2f1Ba5ec4D642Fd7E49cae9EE37"
        self.USDT_CONTRACT_ADDRESS = "0xEd59De2D7ad9C043442e381231eE3646FC3C2939"
        self.FAUCET_ROUTER_ADDRESS = "0x11de0e754f1df7c7b0d559721b334809a9c0dfb7"
        self.SWAP_ROUTER_ADDRESS = "0x1A4DE519154Ae51200b0Ad7c90F7faC75547888a"
        self.POTITION_MANAGER_ADDRESS = "0xF8a1D4FF0f9b9Af7CE58E1fc1833688F3BFd6115"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},
            {"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}
        ]''')
        self.FAUCET_CONTRACT_ABI = [
            {
                "inputs": [
                    { "internalType": "address", "name": "_asset", "type": "address" },
                    { "internalType": "address", "name": "_account", "type": "address" },
                    { "internalType": "uint256", "name": "_amount", "type": "uint256" }
                ],
                "name": "mint",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        self.SWAP_CONTRACT_ABI = [
            {
                "inputs": [
                    { "internalType": "uint256", "name": "collectionAndSelfcalls", "type": "uint256" },
                    { "internalType": "bytes[]", "name": "data", "type": "bytes[]" }
                ],
                "name": "multicall",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            }
        ]
        self.ADD_LP_CONTRACT_ABI = [
            {
                "inputs": [
                    {
                        "components": [
                            { "internalType": "address", "name": "token0", "type": "address" },
                            { "internalType": "address", "name": "token1", "type": "address" },
                            { "internalType": "uint24", "name": "fee", "type": "uint24" },
                            { "internalType": "int24", "name": "tickLower", "type": "int24" },
                            { "internalType": "int24", "name": "tickUpper", "type": "int24" },
                            { "internalType": "uint256", "name": "amount0Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount0Min", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Min", "type": "uint256" },
                            { "internalType": "address", "name": "recipient", "type": "address" },
                            { "internalType": "uint256", "name": "deadline", "type": "uint256" },
                        ],
                        "internalType": "struct INonfungiblePositionManager.MintParams",
                        "name": "params",
                        "type": "tuple",
                    },
                ],
                "name": "mint",
                "outputs": [
                    { "internalType": "uint256", "name": "tokenId", "type": "uint256" },
                    { "internalType": "uint128", "name": "liquidity", "type": "uint128" },
                    { "internalType": "uint256", "name": "amount0", "type": "uint256" },
                    { "internalType": "uint256", "name": "amount1", "type": "uint256" },
                ],
                "stateMutability": "payable",
                "type": "function",
            },
        ]
        self.ref_code = "PNFXEcz1CWezuu3g" # U can change it with yours.
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.signatures = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Pharos Testnet{Fore.BLUE + Style.BRIGHT} Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            raise Exception(f"Generate Addres From Private Key Failed: {str(e)}")
        
    def generate_random_receiver(self):
        try:
            private_key_bytes = secrets.token_bytes(32)
            private_key_hex = to_hex(private_key_bytes)
            account = Account.from_key(private_key_hex)
            receiver = account.address
            
            return receiver
        except Exception as e:
            return None
        
    def generate_signature(self, account: str):
        try:
            encoded_message = encode_defunct(text="pharos")
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            return signature
        except Exception as e:
            raise Exception(f"Generate Signature From Private Key Failed: {str(e)}")
        
    def generate_swap_option(self, wphrs_amount: float, usdc_amount: float, usdt_amount: float):
        swap_option = random.choice([
            "WPHRStoUSDC", "WPHRStoUSDT", "USDCtoWPHRS",
            "USDTtoWPHRS", "USDCtoUSDT", "USDTtoUSDC"
        ])

        from_contract_address = (
            self.USDC_CONTRACT_ADDRESS if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            self.USDT_CONTRACT_ADDRESS if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            self.WPHRS_CONTRACT_ADDRESS
        )

        to_contract_address = (
            self.USDC_CONTRACT_ADDRESS if swap_option in ["WPHRStoUSDC", "USDTtoUSDC"] else
            self.USDT_CONTRACT_ADDRESS if swap_option in ["WPHRStoUSDT", "USDCtoUSDT"] else
            self.WPHRS_CONTRACT_ADDRESS
        )

        from_token = (
            "USDC" if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            "USDT" if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            "WPHRS"
        )

        to_token = (
            "USDC" if swap_option in ["WPHRStoUSDC", "USDTtoUSDC"] else
            "USDT" if swap_option in ["WPHRStoUSDT", "USDCtoUSDT"] else
            "WPHRS"
        )

        swap_amount = (
            usdc_amount if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            usdt_amount if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            wphrs_amount
        )

        return from_contract_address, to_contract_address, from_token, to_token, swap_amount
        
    async def get_web3_with_check(self, retries=3, timeout=60):
        for i in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs={"timeout": timeout}))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                await asyncio.sleep(3)
        raise Exception(f"Failed to Connect to RPC: {str(e)}")
        
    async def get_token_balance(self, address: str, contract_address: str):
        try:
            web3 = await self.get_web3_with_check()

            if contract_address == "PHRS":
                balance = web3.eth.get_balance(address)
            else:
                token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
                balance = token_contract.functions.balanceOf(address).call()

            token_balance = balance / (10 ** 18)

            return token_balance
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def perform_mint_faucet(self, account: str, address: str, asset_address: str):
        try:
            web3 = await self.get_web3_with_check()

            asset_address = web3.to_checksum_address(asset_address)
            target_address = web3.to_checksum_address(address)

            contract_address = web3.to_checksum_address(self.FAUCET_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.FAUCET_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(1000, "ether")
            mint_data = token_contract.functions.mint(asset_address, target_address, amount_to_wei)
            estimated_gas = mint_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            mint_tx = mint_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(mint_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_transfer(self, account: str, address: str, receiver: str, amount: float):
        try:
            web3 = await self.get_web3_with_check()
            
            amount_to_wei = web3.to_wei(amount, "ether")
            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            tx = {
                "to": receiver,
                "value": amount_to_wei,
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "gas": 21000,
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "chainId": web3.eth.chain_id
            }

            signed_tx = web3.eth.account.sign_transaction(tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_wrapped(self, account: str, address: str, amount: float):
        try:
            web3 = await self.get_web3_with_check()

            contract_address = web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(amount, "ether")
            wrap_data = token_contract.functions.deposit()
            estimated_gas = wrap_data.estimate_gas({"from": address, "value": amount_to_wei})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            wrap_tx = wrap_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(wrap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_unwrapped(self, account: str, address: str, amount: float):
        try:
            web3 = await self.get_web3_with_check()

            contract_address = web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(amount, "ether")
            unwrap_data = token_contract.functions.withdraw(amount_to_wei)
            estimated_gas = unwrap_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            unwrap_tx = unwrap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(unwrap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def approving_token(self, account: str, address: str, spender_address: str, contract_address: str, amount: float):
        try:
            web3 = await self.get_web3_with_check()
            
            spender = web3.to_checksum_address(spender_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(amount, "ether")

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount_to_wei:
                approve_data = token_contract.functions.approve(spender, 2**256 - 1)
                estimated_gas = approve_data.estimate_gas({"from": address})

                max_priority_fee = web3.to_wei(1, "gwei")
                max_fee = max_priority_fee

                approve_tx = approve_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                })

                signed_tx = web3.eth.account.sign_transaction(approve_tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                block_number = receipt.blockNumber
            
            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
        
    async def generate_multicall_data(self, address: str, from_contract_address: str, to_contract_address: str, swap_amount: str):
        try:
            web3 = await self.get_web3_with_check()
            
            encoded_data = encode(
                ["address", "address", "uint256", "address", "uint256", "uint256", "uint256"],
                [
                    web3.to_checksum_address(from_contract_address),
                    web3.to_checksum_address(to_contract_address),
                    500,
                    web3.to_checksum_address(address),
                    web3.to_wei(swap_amount, "ether"),
                    0,
                    0
                ]
            )

            multicall_data = [b'\x04\xe4\x5a\xaf' + encoded_data]

            return multicall_data
        except Exception as e:
            raise Exception(f"Generate Multicall Data Failed: {str(e)}")
        
    async def perform_swap(self, account: str, address: str, from_contract_address: str, to_contract_address: str, swap_amount: float):
        try:
            web3 = await self.get_web3_with_check()

            await self.approving_token(account, address, self.SWAP_ROUTER_ADDRESS, from_contract_address, swap_amount)

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.SWAP_CONTRACT_ABI)

            deadline = int(time.time()) + 300

            multicall_data = await self.generate_multicall_data(address, from_contract_address, to_contract_address, swap_amount)

            swap_data = token_contract.functions.multicall(deadline, multicall_data)

            estimated_gas = swap_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            swap_tx = swap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(swap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_add_liquidity(self, account, address, contract_address_1, contract_address_2, amount_1, amount_2):
        try:
            web3 = await self.get_web3_with_check()

            await self.approving_token(account, address, self.POTITION_MANAGER_ADDRESS, contract_address_1, amount_1)
            await self.approving_token(account, address, self.POTITION_MANAGER_ADDRESS, contract_address_2, amount_2)

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.POTITION_MANAGER_ADDRESS), abi=self.ADD_LP_CONTRACT_ABI)

            mint_params = {
                "token0": web3.to_checksum_address(contract_address_1),
                "token1": web3.to_checksum_address(contract_address_2),
                "fee": 500,
                "tickLower": -887220,
                "tickUpper": 887220,
                "amount0Desired": web3.to_wei(amount_1, "ether"),
                "amount1Desired": web3.to_wei(amount_2, "ether"),
                "amount0Min": 0,
                "amount1Min": 0,
                "recipient": web3.to_checksum_address(address),
                "deadline": int(time.time()) + 300
            }

            lp_data = token_contract.functions.mint(mint_params)

            estimated_gas = lp_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            lp_tx = lp_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(lp_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
    
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
    
    async def print_timer(self, min_delay: int, max_delay: int):
        for remaining in range(random.randint(min_delay, max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For Next Tx...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

    def print_question(self):
        mint = False
        tx_count = 0
        tx_amount = 0
        wrap_option = None
        wrap_amount = 0
        add_lp_count = 0
        swap_count = 0
        wphrs_amount = 0
        usdc_amount = 0
        usdt_amount = 0
        rotate = False

        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Check-In - Claim n Mint Faucet{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Send To Friends{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Wrapped - Unwrapped{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}4. Add Liquidity Pool{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}5. Swap WPHRS - USDC - USDT{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}6. Run All Features{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3/4] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3, 4, 5, 6]:
                    option_type = (
                        "Check-In - Claim n Mint Faucet" if option == 1 else 
                        "Send To Friends" if option == 2 else 
                        "Wrapped - Unwrapped" if option == 3 else
                        "Add Liquidity Pool" if option == 4 else
                        "Swap WPHRS - USDC - USDT" if option == 5 else
                        "Run All Features"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, 3, 4, 5 or 6.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, 3, 4, 5 or 6).{Style.RESET_ALL}")

        if option == 1:
            while True:
                mint = input(f"{Fore.BLUE + Style.BRIGHT}Mint USDC & USDT Faucet? [y/n] -> {Style.RESET_ALL}").strip()

                if mint in ["y", "n"]:
                    mint = mint == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        if option == 2:
            while True:
                try:
                    tx_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How Many Times Do You Want To Make a Transfer? -> {Style.RESET_ALL}").strip())
                    if tx_count > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    tx_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Amount for Each Transfers [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if tx_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

        elif option == 3:
            while True:
                try:
                    print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE + Style.BRIGHT}1. Wrapped PHRS to WPHRS{Style.RESET_ALL}")
                    print(f"{Fore.WHITE + Style.BRIGHT}2. Unwrapped WPHRS to PHRS{Style.RESET_ALL}")
                    wrap_option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                    if wrap_option in [1, 2]:
                        wrap_type = (
                            "Wrapped PHRS to WPHRS" if wrap_option == 1 else 
                            "Unwrapped WPHRS to PHRS"
                        )
                        print(f"{Fore.GREEN + Style.BRIGHT}{wrap_type} Selected.{Style.RESET_ALL}")
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

            while True:
                try:
                    wrap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Amount [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if wrap_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

        elif option == 4:
            while True:
                try:
                    add_lp_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How Many Times Do You Want To Add Liquidity Pool? -> {Style.RESET_ALL}").strip())
                    if add_lp_count > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        elif option == 5:
            while True:
                try:
                    swap_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How Many Times Do You Want To Make a Swap? -> {Style.RESET_ALL}").strip())
                    if swap_count > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    wphrs_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}WPHRS Swap Amount? [1 or 0.01 or 0.001, etc in decimals]-> {Style.RESET_ALL}").strip())
                    if wphrs_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    usdc_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}USDC Swap Amount? [1 or 0.01 or 0.001, etc in decimals]-> {Style.RESET_ALL}").strip())
                    if usdc_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    usdt_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}USDT Swap Amount? [1 or 0.01 or 0.001, etc in decimals]-> {Style.RESET_ALL}").strip())
                    if usdt_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        elif option == 6:
            while True:
                mint = input(f"{Fore.BLUE + Style.BRIGHT}Mint USDC & USDT Faucet? [y/n] -> {Style.RESET_ALL}").strip()

                if mint in ["y", "n"]:
                    mint = mint == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

            while True:
                try:
                    tx_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How Many Times Do You Want To Make a Transfer? -> {Style.RESET_ALL}").strip())
                    if tx_count > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    tx_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Amount for Each Transfers [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if tx_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

            while True:
                try:
                    print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE + Style.BRIGHT}1. Wrapped PHRS to WPHRS{Style.RESET_ALL}")
                    print(f"{Fore.WHITE + Style.BRIGHT}2. Unwrapped WPHRS to PHRS{Style.RESET_ALL}")
                    print(f"{Fore.WHITE + Style.BRIGHT}3. Skipped{Style.RESET_ALL}")
                    wrap_option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                    if wrap_option in [1, 2, 3]:
                        wrap_type = (
                            "Wrapped PHRS to WPHRS" if wrap_option == 1 else 
                            "Unwrapped WPHRS to PHRS" if wrap_option == 2 else
                            "Skipped"
                        )
                        print(f"{Fore.GREEN + Style.BRIGHT}{wrap_type} Selected.{Style.RESET_ALL}")
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, or 3.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, or 3).{Style.RESET_ALL}")

            if wrap_option in [1, 2]:
                while True:
                    try:
                        wrap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Amount [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                        if wrap_amount > 0:
                            break
                        else:
                            print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

            while True:
                try:
                    add_lp_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How Many Times Do You Want To Add Liquidity Pool? -> {Style.RESET_ALL}").strip())
                    if add_lp_count > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    swap_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How Many Times Do You Want To Make a Swap? -> {Style.RESET_ALL}").strip())
                    if swap_count > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    wphrs_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}WPHRS Swap Amount? [1 or 0.01 or 0.001, etc in decimals]-> {Style.RESET_ALL}").strip())
                    if wphrs_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    usdc_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}USDC Swap Amount? [1 or 0.01 or 0.001, etc in decimals]-> {Style.RESET_ALL}").strip())
                    if usdc_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    usdt_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}USDT Swap Amount? [1 or 0.01 or 0.001, etc in decimals]-> {Style.RESET_ALL}").strip())
                    if usdt_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
        
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Monosans Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return option, mint, tx_count, tx_amount, wrap_option, wrap_amount, add_lp_count, swap_count, wphrs_amount, usdc_amount, usdt_amount, choose, rotate
    
    async def check_connection(self, proxy=None):
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url="https://testnet.pharosnetwork.xyz", headers={}) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            return None
    
    async def user_login(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user/login?address={address}&signature={self.signatures[address]}&invite_code={self.ref_code}"
        headers = {
            **self.headers,
            "Authorization": "Bearer null",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result["data"]["jwt"]
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    async def user_profile(self, address: str, token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user/profile?address={address}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if "code" in result and result["code"] != 0:
                            await asyncio.sleep(5)
                            continue
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    async def sign_in(self, address: str, token: str, proxy=None, retries=10):
        url = f"{self.BASE_API}/sign/in?address={address}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if "code" in result and result["code"] not in [0, 1]:
                            await asyncio.sleep(5)
                            continue
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    async def phrs_faucet_status(self, address: str, token: str, proxy=None, retries=10):
        url = f"{self.BASE_API}/faucet/status?address={address}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if "code" in result and result["code"] != 0:
                            await asyncio.sleep(5)
                            continue
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def claim_faucet(self, address: str, token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/faucet/daily?address={address}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if "code" in result and result["code"] not in [0, 1]:
                            await asyncio.sleep(5)
                            continue
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def verify_task(self, address: str, token: str, task_id: str, tx_hash: str, proxy=None, retries=10):
        url = f"{self.BASE_API}/task/verify?address={address}&task_id={task_id}&tx_hash={tx_hash}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if "code" in result and result["code"] != 0:
                            await asyncio.sleep(5)
                            continue
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        message = "Checking Connection, Wait..."
        if use_proxy:
            message = "Checking Proxy Connection, Wait..."

        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}",
            end="\r",
            flush=True
        )

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if rotate_proxy:
            is_valid = None
            while is_valid is None:
                is_valid = await self.check_connection(proxy)
                if not is_valid:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Not 200 OK, {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Rotating Proxy...{Style.RESET_ALL}"
                    )
                    proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                    await asyncio.sleep(5)
                    continue

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
                )
                return True

        is_valid = await self.check_connection(proxy)
        if not is_valid:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Not 200 OK, {Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT}Skipping This Account{Style.RESET_ALL}"
            )
            return False
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
        )
        return True
        
    async def process_user_login(self, address: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        token = await self.user_login(address, proxy)
        if not token:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
            )
            return
        
        return token
    
    async def process_perform_mint_faucet(self, account: str, address: str, asset_address: str, token_name: str):
        tx_hash, block_number = await self.perform_mint_faucet(account, address, asset_address)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Mint 1000 {token_name} Faucet Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )
    
    async def process_perform_transfer(self, account: str, address: str, token: str, receiver: str, tx_amount: float, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        tx_hash, block_number = await self.perform_transfer(account, address, receiver, tx_amount)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Perform Transfer Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}Wait For Verifying Task...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(5)

            verify = await self.verify_task(address, token, "103", tx_hash, proxy)
            if verify and verify.get("code") == 0:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Verify  :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}                   "
                )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Verify  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}                   "
                )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_wrapped(self, account: str, address: str, wrap_amount: float):
        tx_hash, block_number = await self.perform_wrapped(account, address, wrap_amount)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Wrapped {wrap_amount} PHRS to WPHRS Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_unwrapped(self, account: str, address: str, wrap_amount: float):
        tx_hash, block_number = await self.perform_unwrapped(account, address, wrap_amount)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Unwrapped {wrap_amount} WPHRS to PHRS Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_add_liquidity(self, account: str, address: str, token: str, contract_address_1: str, contract_address_2: str, amount_1: float, amount_2: float, token_1: str, token_2: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        tx_hash, block_number = await self.perform_add_liquidity(account, address, contract_address_1, contract_address_2, amount_1, amount_2)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Add LP For {amount_1} {token_1} / {amount_2} {token_2} Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_swap(self, account: str, address: str, token: str, from_contract_address: str, to_contract_address: str, from_token: str, to_token: str, swap_amount: float, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        tx_hash, block_number = await self.perform_swap(account, address, from_contract_address, to_contract_address, swap_amount)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Swap {swap_amount} {from_token} to {to_token} Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_option_1(self, account: str, address: str, token: str, mint: bool, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        points = "N/A"
        profile = await self.user_profile(address, token, proxy)
        if profile and profile.get("msg") == "ok":
            points = profile.get("data", {}).get("user_info", {}).get("TotalPoints", 0)

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Balance   :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {points} PTS {Style.RESET_ALL}"
        )

        sign_in = await self.sign_in(address, token, proxy)
        if sign_in and sign_in.get("msg") == "ok":
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Claimed Successfully {Style.RESET_ALL}"
            )
        elif sign_in and sign_in.get("msg") == "already signed in today":
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Already Claimed {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
            )

        self.log(f"{Fore.CYAN+Style.BRIGHT}Faucets   :{Style.RESET_ALL}")

        faucet_status = await self.phrs_faucet_status(address, token, proxy)
        if faucet_status and faucet_status.get("msg") == "ok":
            is_able = faucet_status.get("data", {}).get("is_able_to_faucet", False)

            if is_able:
                claim = await self.claim_faucet(address, token, proxy)
                if claim and claim.get("msg") == "ok":
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}PHAROS  :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} 0.2 PHRS {Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT}Claimed Successfully{Style.RESET_ALL}"
                    )
                elif claim and claim.get("msg") == "user has not bound X account":
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}PHAROS  :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Not Eligible to Claim {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Bind X Account First {Style.RESET_ALL}"
                    )
                else:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}PHAROS  :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
                    )
            else:
                faucet_available_ts = faucet_status.get("data", {}).get("avaliable_timestamp", None)
                faucet_available_wib = datetime.fromtimestamp(faucet_available_ts).astimezone(wib).strftime('%x %X %Z')
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}PHAROS  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Already Claimed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Available at: {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{faucet_available_wib}{Style.RESET_ALL}"
                )
        else:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                f"{Fore.CYAN+Style.BRIGHT}PHAROS  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} GET Eligibility Status Failed {Style.RESET_ALL}"
            )

        for token_name in ["USDC", "USDT"]:
            asset_address = self.USDC_CONTRACT_ADDRESS if token_name == "USDC" else self.USDT_CONTRACT_ADDRESS

            if mint:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}{token_name}    :{Style.RESET_ALL}                       "
                )
                await self.process_perform_mint_faucet(account, address, asset_address, token_name)
                await self.print_timer(5, 10)

            else:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}{token_name}    :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Skipped {Style.RESET_ALL}"
                )

    async def process_option_2(self, account: str, address: str, token: str, tx_count: int, tx_amount: float, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Transfer  :{Style.RESET_ALL}                       ")
        await asyncio.sleep(5)

        for i in range(tx_count):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Tx - {i+1}{Style.RESET_ALL}                       "
            )

            receiver = self.generate_random_receiver()

            balance = await self.get_token_balance(address, "PHRS")
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} PHRS {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_amount} PHRS {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Receiver:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {receiver} {Style.RESET_ALL}"
            )

            if not balance or balance <= tx_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient PHRS Token Balance {Style.RESET_ALL}"
                )
                break

            await self.process_perform_transfer(account, address, token, receiver, tx_amount, use_proxy)
            await self.print_timer(5, 10)

    async def process_option_3(self, account: str, address: str, wrap_option: int, wrap_amount: float):
        if wrap_option == 1:
            self.log(f"{Fore.CYAN+Style.BRIGHT}Wrapped   :{Style.RESET_ALL}                      ")

            balance = await self.get_token_balance(address, "PHRS")
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} PHRS {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {wrap_amount} PHRS {Style.RESET_ALL}"
            )

            if not balance or balance <=  wrap_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient PHRS Token Balance {Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_wrapped(account, address, wrap_amount)
        
        elif wrap_option == 2:
            self.log(f"{Fore.CYAN+Style.BRIGHT}Unwrapped :{Style.RESET_ALL}                      ")

            balance = await self.get_token_balance(address, self.WPHRS_CONTRACT_ADDRESS)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} WPHRS {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {wrap_amount} WPHRS {Style.RESET_ALL}"
            )

            if not balance or balance <=  wrap_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient WPHRS Token Balance {Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_unwrapped(account, address, wrap_amount)

    async def process_option_4(self, account: str, address: str, token: str, add_lp_count: int, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Liquidity :{Style.RESET_ALL}                       ")

        for i in range(add_lp_count):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Add Liquidity{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} / {add_lp_count} {Style.RESET_ALL}                           "
            )

            contract_address_1 = self.WPHRS_CONTRACT_ADDRESS
            amount_1 = 0.001
            token_1 = "WPHRS"

            contract_address_2 = random.choice([self.USDC_CONTRACT_ADDRESS])
            amount_2 = 0.15 if contract_address_2 == self.USDC_CONTRACT_ADDRESS else 3.55
            token_2 = "USDC" if contract_address_2 == self.USDC_CONTRACT_ADDRESS else "USDT"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Type    :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} {token_1} / {token_2} {Style.RESET_ALL}                "
            )

            token_1_balance = await self.get_token_balance(address, contract_address_1)
            token_2_balance = await self.get_token_balance(address, contract_address_2)

            self.log(f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}")
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        > {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{token_1_balance} {token_1}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        > {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{token_2_balance} {token_2}{Style.RESET_ALL}"
            )

            self.log(f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}")
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        > {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{amount_1} {token_1}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        > {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{amount_2} {token_2}{Style.RESET_ALL}"
            )

            if not token_1_balance or token_1_balance <= amount_1:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient {token_1} Token Balance {Style.RESET_ALL}"
                )
                break
            if not token_2_balance or token_2_balance <= amount_2:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient {token_2} Token Balance {Style.RESET_ALL}"
                )
                break

            await self.process_perform_add_liquidity(account, address, token, contract_address_1, contract_address_2, amount_1, amount_2, token_1, token_2, use_proxy)
            await self.print_timer(15, 20)

    async def process_option_5(self, account: str, address: str, token: str, swap_count: int, wphrs_amount: float, usdc_amount: float, usdt_amount: float, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Swap      :{Style.RESET_ALL}                       ")

        for i in range(swap_count):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Swap{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} / {swap_count} {Style.RESET_ALL}                           "
            )

            from_contract_address, to_contract_address, from_token, to_token, swap_amount = self.generate_swap_option(wphrs_amount, usdc_amount, usdt_amount)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Type    :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} {from_token} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} {to_token} {Style.RESET_ALL}"
            )

            balance = await self.get_token_balance(address, from_contract_address)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} {from_token} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {swap_amount} {from_token} {Style.RESET_ALL}"
            )

            if not balance or balance <= swap_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient {from_token} Token Balance {Style.RESET_ALL}"
                )
                continue

            await self.process_perform_swap(account, address, token, from_contract_address, to_contract_address, from_token, to_token, swap_amount, use_proxy)
            await self.print_timer(15, 20)

    async def process_accounts(self, account: str, address: str, option: int, mint: bool, tx_count: int, tx_amount: float, wrap_option: int, wrap_amount: float, add_lp_count: int, swap_count: int, wphrs_amount: float, usdc_amount: float, usdt_amount: float, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            token = await self.process_user_login(address, use_proxy)
            if token:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}"
                )

                if option == 1:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT} Check-In - Claim n Mint Faucet {Style.RESET_ALL}"
                    )

                    await self.process_option_1(account, address, token, mint, use_proxy)

                elif option == 2:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT} Send To Friends {Style.RESET_ALL}"
                    )

                    await self.process_option_2(account, address, token, tx_count, tx_amount, use_proxy)

                elif option == 3:
                    wrap_type = "Wrap PHRS to WPHRS" if wrap_option == 1 else "Unwrap WPHRS to PHRS"
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT} {wrap_type} {Style.RESET_ALL}"
                    )
                    
                    await self.process_option_3(account, address, wrap_option, wrap_amount)

                elif option == 4:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT} Add Liquidity Pool {Style.RESET_ALL}"
                    )

                    await self.process_option_4(account, address, token, add_lp_count, use_proxy)

                elif option == 5:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT} Swap WPHRS - USDC - USDT  {Style.RESET_ALL}"
                    )

                    await self.process_option_5(account, address, token, swap_count, wphrs_amount, usdc_amount, usdt_amount, use_proxy)

                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT} Run All Features {Style.RESET_ALL}"
                    )

                    await self.process_option_1(account, address, token, mint, use_proxy)
                    await asyncio.sleep(5)

                    await self.process_option_2(account, address, token, tx_count, tx_amount, use_proxy)
                    await asyncio.sleep(5)

                    await self.process_option_3(account, address, wrap_option, wrap_amount)
                    await asyncio.sleep(5)
                    
                    await self.process_option_4(account, address, token, add_lp_count, use_proxy)
                    await asyncio.sleep(5)

                    await self.process_option_5(account, address, token, swap_count, wphrs_amount, usdc_amount, usdt_amount, use_proxy)
                    await asyncio.sleep(5)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            option, mint, tx_count, tx_amount, wrap_option, wrap_amount, add_lp_count, swap_count, wphrs_amount, usdc_amount, usdt_amount, use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        signature = self.generate_signature(account)

                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if address and signature:
                            self.signatures[address] = signature

                            await self.process_accounts(account, address, option, mint, tx_count, tx_amount, wrap_option, wrap_amount, add_lp_count, swap_count, wphrs_amount, usdc_amount, usdt_amount, use_proxy, rotate_proxy)
                            await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                seconds = 10
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = PharosTestnet()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Pharos Testnet - BOT{Style.RESET_ALL}                                       "                              
        )
