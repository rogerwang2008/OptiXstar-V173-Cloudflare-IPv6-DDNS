import requests
import logging
from .ip import check_version


logger = logging.getLogger(__name__)

TOKEN = ""


def update_record_ip(zone_id: str, record_id: str, ip: str) -> bool:
    record_type = "A" if check_version(ip) == 4 else "AAAA"
    logger.info(f"Changing record to {record_type}: {ip}")

    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    data = {"content": ip, "type": record_type}
    response = requests.patch(url, headers=headers, json=data)
    logger.info(f"{response.json()}")
    return response.status_code == 200
