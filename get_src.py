import coin_search
import os
import requests
import json

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "KFC1IGGJ61EM5757AG5K3BD7Y2CYMC827Q")
def get_src(symbol):
    chain_info = coin_search.get_coin_contract_addr(symbol)
    if not chain_info:
        print(f"❌ 未找到 {symbol} 的合约地址")
        return json.dumps({"error": "Failed to find contract address for this cryptocurrency on Ethereum"}, ensure_ascii=False, indent=4)
    print("📖 正在获取该代币的合约源代码...")
    eth_address = chain_info["chains"]["ethereum"]
    
    url = (
        f"https://api.etherscan.io/v2/api"
        f"?chainid=1"
        f"&module=contract"
        f"&action=getsourcecode"
        f"&address={eth_address}"
        f"&apikey={ETHERSCAN_API_KEY}"
    )
    while True:
        response = requests.get(url)
        data = response.json()

        if data["status"] == "1":
            src = data["result"][0]["SourceCode"]
            return src
        else:
            print("源代码获取失败，正在尝试重新获取...")