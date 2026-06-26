import asyncio
import json

import httpx
import os
import redis.asyncio as aredis
from dotenv import load_dotenv
from fastapi import FastAPI

app = FastAPI(title="Sentinel")


load_dotenv()

ABUSEIPDB_KEY = os.getenv("ABUSEIPDB_API_KEY")
OTX_KEY = os.getenv("OTX_API_KEY")
r = aredis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True
)


async def check_abuseipdb(target: str):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": ABUSEIPDB_KEY, "Accept": "application/json"}
    params = {"ipAddress": target, "maxAgeInDays": 90}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers, params=params)
        data = response.json()
        return data.get("data", {})


async def check_otx(target: str):
    url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{target}/general"
    headers = {"X-OTX-API-KEY": OTX_KEY or ""}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)
        data = response.json()
        return data


@app.get("/check")
async def check_indicator(target: str):
    cache_key = f"IP:{target}"

    cached = await r.get(cache_key)
    if cached:
        return {"source": "cache", "data": json.loads(cached)}

    abuse_data, otx_data = await asyncio.gather(
        check_abuseipdb(target),
        check_otx(target),
    )

    result = {
        "target": target,
        "abuseipdb": abuse_data if not isinstance(abuse_data, Exception) else None,
        "otx": otx_data if not isinstance(otx_data, Exception) else None,
    }

    await r.set(cache_key, json.dumps(result), ex=86400)

    return {"source": "api", "data": result}
