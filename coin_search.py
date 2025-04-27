from pycoingecko import CoinGeckoAPI
import json

def get_coin_dict(symbol):
    # 遍历所有代币，匹配Symbol
    with open('coin_list.json', 'r', encoding='utf-8') as f:
        coins = json.load(f)
    matches = [coin for coin in coins if coin['symbol'] == symbol.lower()]
    # 如果在本地文件中找到匹配的代币
    if matches:
        for match in matches:
            if "ethereum" in match["platforms"]:
                return match
        return matches[0]
    return None


def get_coin_contract_addr(symbol):
    print(f"📖 正在获取 {symbol} 的链上信息...")
    symbol_dict = get_coin_dict(symbol)
    if not symbol_dict:
        print(f"⚠️  本地Coin List中找不到 {symbol} ，无法获取链上信息")
        return None
    token_id = symbol_dict['id']
    cg = CoinGeckoAPI()
    
    # 获取代币详情
    token_data = cg.get_coin_by_id(token_id)
    
    # 提取链和合约地址
    platforms = token_data.get('platforms', {})
    
    # 过滤空值
    chains = {chain: address for chain, address in platforms.items() if address}
    
    return {
        "name": token_data['name'],
        "id": token_id,
        "symbol": token_data['symbol'],
        "chains": chains
    }