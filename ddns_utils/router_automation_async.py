import asyncio
import logging
from typing import Optional
import re
from playwright.async_api import async_playwright, Page, Locator, expect

logger = logging.getLogger(__name__)
# 设置默认超时时间
# 注意：async_playwright 上下文管理器会处理启动和关闭
# expect 默认超时可以通过其方法设置，这里先设置一个全局的参考值
DEFAULT_TIMEOUT = 60000


class RouterAutomationRunnerAsync:
    def __init__(self, headless: bool = True, screenshot: bool = True, *, playwright_channel: str = "msedge"):
        self.screenshot = screenshot
        self.headless = headless
        self.playwright_channel = playwright_channel
        self.playwright = None
        self.browser = None
        self.page: Optional[Page] = None
        self.current_page: Optional[str] = None
        self.logged_in = False

    async def __aenter__(self):
        """异步上下文管理器入口，用于初始化 Playwright"""
        self.playwright = await async_playwright().start()
        # 注意：channel="msedge" 在异步 API 中可能行为略有不同或不被支持，根据实际情况调整
        # 如果遇到问题，可以尝试移除 channel 参数或使用 'chromium'
        self.browser = await self.playwright.chromium.launch(channel=self.playwright_channel, headless=self.headless)
        self.page = await self.browser.new_page()
        # 为页面设置默认超时
        self.page.set_default_timeout(DEFAULT_TIMEOUT)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口，用于清理资源"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def login(self):
        """执行登录操作"""
        if not self.page:
            raise RuntimeError("Playwright page not initialized. Use within async context manager.")

        logger.debug("进入登录页面中")
        await self.page.goto("http://192.168.1.1")
        self.current_page = "login"
        logger.debug("进入登录页面成功")
        # 使用 evaluate 执行页面上的 JavaScript 函数
        await self.page.evaluate("AdminuserSubmit1")
        await self.page.locator("input#txt_normalUsername").fill("user")
        await self.page.locator("input#txt_normalPassword").fill("abvcdfds")
        await self.page.evaluate("SubmitForm")
        # 等待登录成功的标识元素出现
        await expect(self.page.locator("#headerLogoutText")).to_be_visible(timeout=DEFAULT_TIMEOUT)
        self.current_page = "index"
        self.logged_in = True
        logger.debug("登录成功")
        if self.screenshot:
            await self.page.screenshot(path="./screenshots/login.png")

    async def goto_ipv6_port_mapping(self):
        """导航到 IPv6 端口映射页面"""
        if not self.logged_in:
            await self.login()
        if not self.page:
            raise RuntimeError("Playwright page not initialized. Use within async context manager.")

        logger.debug("进入 IPv6 端口映射页面中")
        await self.page.goto("http://192.168.1.1/html/bbsp/ipv6portmapping/ipv6portmapping.asp")
        self.current_page = "ipv6_port_mapping"
        logger.debug("进入 IPv6 端口映射页面成功")
        if self.screenshot:
            await self.page.screenshot(path="./screenshots/ipv6pm_page.png")

    async def ipv6_port_mapping_change_ip(self, name: str, ip: str):
        """修改指定名称的 IPv6 端口映射条目的内部客户端 IP"""
        # self.page.wait_for_timeout(2000) # 通常不推荐使用硬编码等待
        if len(name) > 10:
            name = name[:10] + "......"
        if self.current_page != "ipv6_port_mapping":
            await self.goto_ipv6_port_mapping()
        if not self.page:
            raise RuntimeError("Playwright page not initialized. Use within async context manager.")

        table = self.page.locator("#portMappingInst")
        # 使用 get_by_role 并结合 name 选项来定位包含特定文本的行
        # exact=False 允许部分匹配
        target_row = table.get_by_role("row", name=name, exact=False)
        # 等待目标行出现
        await target_row.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        logger.debug(f"找到 IPv6 端口映射条目: {name}")
        # 点击该行的复选框
        await target_row.get_by_role("checkbox").click()
        logger.debug("进入 IPv6 端口映射条目配置界面")
        # 定位并填充 IP 输入框
        ip_input = self.page.locator("#InternalClient")
        await ip_input.fill(ip)
        logger.debug(f"修改 IP 为 {ip}")
        if self.screenshot:
            await self.page.screenshot(path="./screenshots/ipv6pm_selected.png")
        # 点击提交按钮
        submit_button = self.page.locator("#btnApply_ex")
        await submit_button.click()
        logger.debug("提交修改")


# --- 使用示例 ---
async def main():
    # 配置日志（可选，用于查看调试信息）
    logging.basicConfig(level=logging.DEBUG)

    # 使用异步上下文管理器确保资源正确初始化和关闭
    async with RouterAutomationRunnerAsync(headless=False, screenshot=True) as runner:
        try:
            # 执行登录
            await runner.login()
            # 导航到端口映射页面
            await runner.goto_ipv6_port_mapping()
            # 修改 IP 地址
            await runner.ipv6_port_mapping_change_ip("LIO-AN00", "192.168.1.100")
            print("IP 地址修改成功！")
            # 可以在这里添加更多操作...
        except Exception as e:
            logger.error(f"自动化过程中发生错误: {e}")
            # 可以选择在此处截图保存错误状态
            if runner.page and runner.screenshot:
                try:
                    await runner.page.screenshot(path="./screenshots/error.png")
                except Exception as e:
                    logger.error(f"保存错误截图时发生错误: {e}")

# 运行异步主函数
# asyncio.run(main())
