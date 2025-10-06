import os, requests, json
from datetime import datetime

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_token():
    r = requests.post("https://oauth.battle.net/token",
                      data={"grant_type":"client_credentials"},
                      auth=(CLIENT_ID, CLIENT_SECRET))
    return r.json()["access_token"]

def get_auctions(region, realm_id, token):
    url = f"https://{region}.api.blizzard.com/data/wow/connected-realm/{realm_id}/auctions"
    params = {"namespace": f"dynamic-{region}", "locale": "en_US", "access_token": token}
    return requests.get(url, params=params).json()["auctions"]

def extract_prices(auctions, item_ids):
    prices = {}
    for auc in auctions:
        item_id = auc["item"]["id"]
        if item_id in item_ids and "buyout" in auc:
            gold = auc["buyout"] / 10000
            if item_id not in prices or gold < prices[item_id]:
                prices[item_id] = gold
    return prices

if __name__ == "__main__":
    with open("data/items.json") as f:
        item_ids = json.load(f)

    token = get_token()
    realms = [1403, 512]  # example EU realm IDs (Draenor, Silvermoon, etc.)

    results = {}
    for realm_id in realms:
        auctions = get_auctions("eu", realm_id, token)
        results[realm_id] = extract_prices(auctions, item_ids)

    # Save
    output = {"timestamp": str(datetime.utcnow()), "results": results}
    with open("output/results.json", "w") as f:
        json.dump(output, f, indent=2)

