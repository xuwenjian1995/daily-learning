#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/9 14:42
import os, sys, re, json, traceback, time
from selenium import webdriver





if __name__ == "__main__":
    chrome_capabilities = {
        "browserName": "chrome",
        "version": "",
        "platform": "ANY",
        "javascriptEnabled": True,

    }
    browser = webdriver.Remote("http://10.1.253.53:4444/wd/hub", desired_capabilities=chrome_capabilities)
    browser.set_window_size(900,1300)
    browser.get("http://10.1.253.53:11111/pdf/20.pdf")
    for i in range(5):
        print(browser.page_source)
        time.sleep(1)
    js_scroll = "document.documentElement.scrollTop "
    browser.get_screenshot_as_file("/tmp/test1.png")
    browser.quit()
