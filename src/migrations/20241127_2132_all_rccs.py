import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        erc_20_base_abi = """[ { "constant": true, "inputs": [], "name": "name", "outputs": [ { "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "name": "_spender", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "approve", "outputs": [ { "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "totalSupply", "outputs": [ { "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "name": "_from", "type": "address" }, { "name": "_to", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "transferFrom", "outputs": [ { "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "decimals", "outputs": [ { "name": "", "type": "uint8" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "name": "_owner", "type": "address" } ], "name": "balanceOf", "outputs": [ { "name": "balance", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "symbol", "outputs": [ { "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "name": "_to", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "transfer", "outputs": [ { "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [ { "name": "_owner", "type": "address" }, { "name": "_spender", "type": "address" } ], "name": "allowance", "outputs": [ { "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "payable": true, "stateMutability": "payable", "type": "fallback" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "owner", "type": "address" }, { "indexed": true, "name": "spender", "type": "address" }, { "indexed": false, "name": "value", "type": "uint256" } ], "name": "Approval", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "from", "type": "address" }, { "indexed": true, "name": "to", "type": "address" }, { "indexed": false, "name": "value", "type": "uint256" } ], "name": "Transfer", "type": "event" } ] """ # lic lic_abi = '[{"inputs":[{"internalType":"string","name":"name_","type":"string"},{"internalType":"string","name":"symbol_","type":"string"},{"internalType":"uint256","name":"initialSupplyToSet","type":"uint256"},{"internalType":"uint8","name":"decimalsToSet","type":"uint8"},{"internalType":"address","name":"tokenOwner","type":"address"},{"components":[{"internalType":"bool","name":"_isMintable","type":"bool"},{"internalType":"bool","name":"_isBurnable","type":"bool"},{"internalType":"bool","name":"_isPausable","type":"bool"},{"internalType":"bool","name":"_isBlacklistEnabled","type":"bool"},{"internalType":"bool","name":"_isDocumentAllowed","type":"bool"},{"internalType":"bool","name":"_isWhitelistEnabled","type":"bool"},{"internalType":"bool","name":"_isMaxAmountOfTokensSet","type":"bool"},{"internalType":"bool","name":"_isForceTransferAllowed","type":"bool"}],"internalType":"struct FullFeatureToken.ERC20ConfigProps","name":"customConfigProps","type":"tuple"},{"internalType":"uint256","name":"maxTokenAmount","type":"uint256"},{"internalType":"string","name":"newDocumentUri","type":"string"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"AddrAlreadyBlacklisted","type":"error"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"AddrAlreadyUnblacklisted","type":"error"},{"inputs":[],"name":"BlacklistNotEnabled","type":"error"},{"inputs":[],"name":"BurningNotEnabled","type":"error"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"CannotBlacklistWhitelistedAddr","type":"error"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"CannotWhitelistBlacklistedAddr","type":"error"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"DestBalanceExceedsMaxAllowed","type":"error"},{"inputs":[],"name":"DocumentUriNotAllowed","type":"error"},{"inputs":[{"internalType":"uint8","name":"decimals","type":"uint8"}],"name":"InvalidDecimals","type":"error"},{"inputs":[{"internalType":"uint256","name":"maxTokenAmount","type":"uint256"}],"name":"InvalidMaxTokenAmount","type":"error"},{"inputs":[],"name":"MaxTokenAmountPerAddrLtPrevious","type":"error"},{"inputs":[],"name":"MintingNotEnabled","type":"error"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"NonZeroAddress","type":"error"},{"inputs":[],"name":"PausingNotEnabled","type":"error"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"RecipientBlacklisted","type":"error"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"RecipientNotWhitelisted","type":"error"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"SenderBlacklisted","type":"error"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"SenderNotWhitelisted","type":"error"},{"inputs":[],"name":"WhitelistNotEnabled","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"string","name":"newDocUri","type":"string"}],"name":"DocumentUriSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"newMaxTokenAmount","type":"uint256"}],"name":"MaxTokenAmountPerSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"addr","type":"address"}],"name":"UserBlacklisted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"addr","type":"address"}],"name":"UserUnBlacklisted","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address[]","name":"updatedAddresses","type":"address[]"}],"name":"UsersWhitelisted","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"blackList","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burnFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"documentUri","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getWhitelistedAddresses","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"initialDocumentUri","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"initialMaxTokenAmountPerAddress","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"initialSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"initialTokenOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isBlacklistEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isBurnable","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isDocumentUriAllowed","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isForceTransferAllowed","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isMaxAmountOfTokensSet","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isMintable","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isPausable","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isWhitelistEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxTokenAmountPerAddress","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"removeFromBlacklist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"newDocumentUri","type":"string"}],"name":"setDocumentUri","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"newMaxTokenAmount","type":"uint256"}],"name":"setMaxTokenAmountPerAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"updatedAddresses","type":"address[]"}],"name":"updateWhitelist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"whitelist","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"whitelistedAddresses","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'"""

        currencies = [{
            # gone
            'contract_address': '0x162539172b53E9a93b7d98Fb6c41682De558a320',
            'chain':'polygon',
            'name':'polyGONE',
            'short_name': 'GONE',
            'emoji': '🥔',
            'decimals': '18',
            'fee_divisor': '100',
            'fee_factor': '5',
            'fee_percentage_str': '5%'
        },{
            # tryan
            'contract_address': '0x550F908e06d1DA4FFEe6B1FB63730F88eCc4d230',
            'chain':'polygon',
            'name':'Tryan',
            'short_name': 'TRYAN',
            'emoji': '🧠',
            'decimals': '18',
            'fee_divisor': '100',
            'fee_factor': '5',
            'fee_percentage_str': '5%'
        },{
            # shroom
            'contract_address': '0x924B16Dfb993EEdEcc91c6D08b831e94135dEaE1',
            'chain':'polygon',
            'name':'$hroom',
            'short_name': 'shroom',
            'emoji': '🍄',
            'decimals': '18',
            'fee_divisor': '100',
            'fee_factor': '5',
            'fee_percentage_str': '5%'
        },{
            # bucket
            'contract_address': '0xB631937b9E75A66291E7570E8Ed3Db10Eb43A888',
            'chain':'polygon',
            'name':'Bucket',
            'short_name': 'bucket',
            'emoji': '🪣',
            'decimals': '18',
            'fee_divisor': '100',
            'fee_factor': '5',
            'fee_percentage_str': '5%'
        },{
            # poop
            'contract_address': '0xc6268A296c810024aa3AA2F5Cc2c255bF995AA44',
            'chain':'polygon',
            'name':'Poop',
            'short_name': 'POOP',
            'emoji': '💩',
            'decimals': '18',
            'fee_divisor': '100',
            'fee_factor': '5',
            'fee_percentage_str': '5%'
        },{
            # bone
            'contract_address': '0xF297C728cE19E9f61f76c4cF958c32e03E024c4B',
            'chain':'polygon',
            'name':'Bones',
            'short_name': 'bone',
            'emoji': '🦴',
            'decimals': '18',
            'fee_divisor': '100',
            'fee_factor': '5',
            'fee_percentage_str': '5%'
        },{
            # plunger
            'contract_address': '0x43ff18fa32e10873fd9519261004a85aE2c7a65d',
            'chain':'polygon',
            'name':'Plunger',
            'short_name': 'Plunger',
            'emoji': '🪠',
            'decimals': '18',
            'fee_divisor': '100',
            'fee_factor': '5',
            'fee_percentage_str': '5%'
        },{
            # tacoz
            'contract_address': '0x7eA837454E3c425E01A8432234140755Fc2aDD1c',
            'chain':'polygon',
            'name':'Taco',
            'short_name': 'TACO',
            'emoji': '🌮',
            'decimals': '18',
            'fee_divisor': '100',
            'fee_factor': '5',
            'fee_percentage_str': '5%'
        }]

        for currency in currencies:
            await cursor.execute("""
                INSERT INTO evm_currency
                (contract_address, chain, name, short_name, emoji, decimals, fee_divisor, fee_factor, fee_percentage_str,contract_abi)
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s);
                """, (
                    currency['contract_address'],
                    currency['chain'],
                    currency['name'],
                    currency['short_name'],
                    currency['emoji'],
                    int(currency['decimals']),
                    int(currency['fee_divisor']),
                    int(currency['fee_factor']),
                    currency['fee_percentage_str'],
                    erc_20_base_abi
                )
            )

            for sub in ['tipcoin','the23','toesling','lamainucoin','cryptocurrencymax','avatartraders','cryptofans']:
                await cursor.execute("""
                    INSERT INTO sub_currencies (subreddit, contract_address) VALUES 
                    (%s, %s);
                """, (sub,currency['contract_address']))
                await conn.commit()
