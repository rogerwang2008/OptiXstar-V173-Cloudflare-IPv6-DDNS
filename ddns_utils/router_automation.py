from typing import Literal
import logging
import re
import playwright.sync_api
from playwright.sync_api import sync_playwright, Locator


logger = logging.getLogger(__name__)


playwright.sync_api.expect.set_options(timeout=30000)

class RouterAutomationRunner:
    def __init__(self, headless: bool = True, screenshot: bool = True):
        self.screenshot = screenshot
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(channel="msedge", headless=headless)
        # self.browser = self.playwright.webkit.launch(headless=False)
        self.page = self.browser.new_page()
        self.current_page: str | None = None
        self.logged_in = False

    def login(self):
        self.page.goto("http://192.168.1.1")
        self.current_page = "login"
        logger.debug("进入登录页面")
        self.page.evaluate("AdminuserSubmit1")
        self.page.locator("input#txt_normalUsername").fill("user")
        self.page.locator("input#txt_normalPassword").fill("abvcdfds")
        self.page.evaluate("SubmitForm")
        self.page.wait_for_selector("#headerLogoutText")
        self.current_page = "index"
        self.logged_in = True
        logger.debug("登录成功")
        if self.screenshot:
            self.page.screenshot(path="./screenshots/login.png")

    def goto_ipv6_port_mapping(self):
        if not self.logged_in:
            self.login()
        self.page.goto("http://192.168.1.1/html/bbsp/ipv6portmapping/ipv6portmapping.asp")
        self.current_page = "ipv6_port_mapping"
        logger.debug("进入 IPv6 端口映射页面")
        if self.screenshot:
            self.page.screenshot(path="./screenshots/ipv6pm_page.png")

    def ipv6_port_mapping_change_ip(self, name: str, ip: str):
        # self.page.wait_for_timeout(2000)
        if len(name) > 10:
            name = name[:10] + "......"
        if self.current_page != "ipv6_port_mapping":
            self.goto_ipv6_port_mapping()
        table = self.page.locator("#portMappingInst")
        # target_row = table.locator("css=tr", has_text=name)
        target_row = table.get_by_role("row", name=name, exact=False)
        target_row.wait_for()
        logger.debug(f"找到 IPv6 端口映射条目")
        target_row.get_by_role("checkbox").click()
        logger.debug("进入 IPv6 端口映射条目配置界面")
        ip_input = self.page.locator("#InternalClient")
        ip_input.fill(ip)
        logger.debug(f"修改 IP 为 {ip}")
        if self.screenshot:
            self.page.screenshot(path="./screenshots/ipv6pm_selected.png")
        submit_button = self.page.locator("#btnApply_ex")
        submit_button.click()
        logger.debug("提交修改")

    # def run(self, ip: str):
    #     self.login()
    #     self.goto_ipv6_port_mapping()
    #     self.ipv6_port_mapping_change_ip("LIO-AN00", ip)
