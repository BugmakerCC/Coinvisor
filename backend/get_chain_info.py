import coin_search
import json
import get_coin_info_market
import get_transactions
def get_chain_info(symbol):
    """
    获取代币的链上信息。
    :param symbol: 代币的符号，例如 "BTC"
    :return: 代币的链上信息字典
    """
    info = {}
    # 获取代币的链的信息
    chain_info = coin_search.get_coin_contract_addr(symbol)
    # 找不到该代币
    if not chain_info:
        info["Token ID"] = None
        info["Contract Address"] = None
        info["Unusual Transactions"] = None
        info["Error"] = "Failed to find its Token ID"
        return json.dumps(info, ensure_ascii=False, indent=4)
    else:
        info["Token ID"] = chain_info['name']
        # 找合约地址
        if 'ethereum' not in chain_info['chains'].keys():
            print(f"⚠️  {symbol} 在以太坊上找不到对应的合约地址")
            info["Contract Address"] = None
            info["Unusual Transactions"] = None
            info["Error"] = "The token does not have a contract address on Ethereum"
        else:
            info["Contract Address"] = chain_info['chains']['ethereum']
            # 找代币单价
            market_info = get_coin_info_market.get_coin_info_market(symbol)
            if not market_info:
                info["Unusual Transactions"] = None
                info["Error"] = "Failed to get price for this cryptocurrency on Binance"
            # 找异常交易
            else:
                token_price = market_info['lastPrice']
                chain_info["price"] = float(token_price)
                info["Unusual Transactions"] = get_transactions.get_big_tranasaction(chain_info)
    return info


if __name__ == "__main__":
    symbol = "BNB"
    result = get_chain_info(symbol)
    print(result)