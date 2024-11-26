# PumpFun-Sniper
Snipe low cap gems on `pump.fun` using this simple Python script.

# Description
This Python script enables you to purchase low-cap gems on `pump.fun` and sell them for profit ahead of others. It's designed to be minimalist, relying primarily on the APIs provided by `pump.fun` and requiring no additional dependencies, so no module installations are needed. The script continuously monitors newly launched coins based on specific filters, ensuring that each coin meets certain criteria like minimum market cap and social presence (e.g., website, Telegram). Once a suitable coin is identified, the script uses the minimum SOL value provided to make a purchase. The purchased coins are then monitored and sold when they reach a specified profit threshold, which is set to 50% by default but can be adjusted as needed.

# Usage
To get started with the script, you’ll need the following:
- Solana Wallet Private Key – Required for secure access.
- Seed Phrase (optional) – If you prefer not to use the private key.
- Ensure the primary account has some SOL. Safe to use 10-20 SOL as it helps snipe a lot more coins.

Clone the repository:
```
git clone https://github.com/Web3TechDev/PumpFun-Sniper.git
cd PumpFun-Sniper
```

Run the script as follows:
```
python3 pumpfun_sniper.py  --max-coins 5 --min 0.1 --private-key c316a0895a2ae4620c28af7913573e20ea4f0c60002274bd34c3f67210d65f75
```
or
```
python3 pumpfun_sniper.py  --max-coins 5 --min 0.1 --seed-phrase 'chicken law traction era debt formation offset directory science novel auction appetite'
```
<img src="https://github.com/Web3TechDev/PumpFun-Sniper/blob/main/1.jpg?raw=true" width=70% height=70%>
