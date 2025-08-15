import logging
from rich import logging as rich_logging
import asyncio
import dotenv
import os

from ddns_utils import router_automation_async, cloudflare, ip as ip_utils

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[rich_logging.RichHandler(rich_tracebacks=True)]
)

dotenv.load_dotenv("./config.env")
cloudflare.TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")


async def main():
    ipv6 = ip_utils.get_ip_if_changed(6, True)
    if ipv6 is None:
        return
    try:
        for record_id in os.getenv("CLOUDFLARE_IPV6_RECORD_IDS").split(","):
            cloudflare.update_record_ip(os.getenv("CLOUDFLARE_ZONE_ID"), record_id, ipv6)

        async with router_automation_async.RouterAutomationRunnerAsync(headless=True, screenshot=True, playwright_channel=os.getenv("PLAYWRIGHT_CHANNEL")) as runner:
            # 执行登录
            await runner.login()
            # 导航到端口映射页面
            await runner.goto_ipv6_port_mapping()
            # 修改 IP 地址
            for port_mapping_name in os.getenv("ROUTER_IPV6_PORT_MAPPING_NAMES").split(","):
                await runner.ipv6_port_mapping_change_ip(port_mapping_name, ipv6)
    except Exception as e:
        ip_utils.delete_saved_ip(6)
        raise e


if __name__ == '__main__':
    asyncio.run(main())
