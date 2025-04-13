from typing import Optional, Dict, List
from collections import defaultdict
from dataclasses import dataclass
import requests
import asyncio
import yaml
import json
import sys

#@dataclass
#class Endpoint
#--- This dataclass illustrates the schema/model the config yaml file will need to follow. 
#--- The load_endpoints will raise ValueError if the contents of the data passed does not match the below schema
@dataclass
class Endpoint:
    name: str
    url: str
    method: str = 'GET'
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None

# Function to load configuration from the YAML file
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to perform health checks
async def check_health(endpoint: Endpoint) -> str:
    url = endpoint.url
    method = endpoint.method
    headers = endpoint.headers
    body = json.loads(endpoint.body) if endpoint.body else None

    try:
        response = requests.request(method, url, headers=headers, json=body)
        
        #Below condition will only evaluate True if the response status_code is in range of 200-299 and the response time in ms is 500ms or less
        if (200 <= response.status_code < 300) and ((response.elapsed.total_seconds() * 1000) <= 500):
            return "UP"
        else:
            return "DOWN"
    except requests.RequestException:
        return "DOWN"

#param data: list
#returns a list of Endpoint objects
def load_endpoints(data: List[dict]) ->  List[Endpoint]:
    endpoints = []
    for d in data:
        try:
            endpoints.append(Endpoint(**d))
        except TypeError as e:
            raise ValueError(f"Invalid endpoint definition: {d}") from e
    return endpoints

# Main function to monitor endpoints
async def monitor_endpoints(file_path):
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})
    endpoints = load_endpoints(load_config(file_path))
    
    async def _handle_domain_stats(endpoint: Endpoint, result: str, domain_stats: defaultdict):
        domain = endpoint.url.split("//")[-1].split("/")[0].split(":")[0]
        domain_stats[domain]["total"] += 1
        if result == "UP":
            domain_stats[domain]["up"] += 1

    async def _handle_print(domain, stats):
        print(f"{domain}, has {round(100 * stats["up"] / stats["total"])}% availability percentage")

    while True:
        results = await asyncio.gather(*[
            check_health(endpoint) 
            for endpoint in endpoints
        ])

        await asyncio.gather(*[
            _handle_domain_stats(endpoint=endpoint, result=result, domain_stats=domain_stats)
            for endpoint, result in zip(endpoints, results)
        ])

        await asyncio.gather(*[
            _handle_print(domain, stats)
            for domain, stats in domain_stats.items()
        ])

        print("---")
        await asyncio.sleep(15)

async def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <config_file_path>")
        sys.exit(1)

    config_file = sys.argv[1]
    try:
        await monitor_endpoints(config_file)
    except:
        print("\nMonitoring stopped by user.")

# Entry point of the program
if __name__ == "__main__":
    asyncio.run(main())
