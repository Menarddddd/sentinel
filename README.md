Sentinel
A small FastAPI project that checks if an IP is known for malicious activity. It queries AbuseIPDB and AlienVault OTX, then caches the results in Redis so it doesn't spam the APIs on repeated requests.

I built this while learning how to work with external threat intel APIs and async requests. Everything is in main.py because I wanted to keep it simple for now.

What it does
Takes an IP address
Checks it against AbuseIPDB and OTX
Caches the result in Redis for 24 hours
Returns the combined data

Tech used
FastAPI
httpx (async)
Redis (caching)
AbuseIPDB + AlienVault OTX APIs

How to run
Clone the repo
Create a .env file with your keys:
env
ABUSEIPDB_API_KEY=your_key
OTX_API_KEY=your_key
REDIS_URL=redis://localhost:6379

Start Redis (I used Docker)
Run the app:
uvicorn main:app --reload
Then hit /check?target=8.8.8.8
