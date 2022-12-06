"""desmos2python/browser.py

Headless browser functionality
"""
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import JavascriptException
from functools import cached_property
from pathlib import Path
import importlib
import importlib.resources
import importlib.util
from desmos2python.utils import D2P_Resources
from typing import AnyStr
import json
from threading import RLock

__all__ = [
    'DesmosWebSession',
]


class DesmosWebSession(object):
    """connect to (possibly remote) desmos graphs.

    ...via headless selenium-powered browser session.
    """

    desmos_url_head = 'https://www.desmos.com/calculator/'

    def __init__(self, url='8tb0onyoep', title: AnyStr = None):
        self._user_title = title
        self.url = self.format_url(url)
        self.outpath = None
        self.js_string = 'return Calc.getExpressions()'
        self.browser = None
        self.init_browser()
        self.lock = RLock()

    def format_url(self, url):
        if DesmosWebSession.desmos_url_head not in url:
            url = f'{DesmosWebSession.desmos_url_head}{url}'
        return url

    def init_browser(self):
        """initialize headless browser webdriver"""
        #: ref: https://pythonbasics.org/selenium-firefox-headless/
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.headless = True
        browser = webdriver.Firefox(options=fireFoxOptions)
        self.browser = browser

    def check_document_initialised(self):
        """Confirm document is initialized (useful for awaiting page load).

        ref: https://www.selenium.dev/documentation/webdriver/waits/
        """
        try:
            _ = self.browser.execute_script(self.js_string)
        except JavascriptException:
            return False
        else:
            return True

    def await_DOM(self, callback=None, timeout=10):
        """wait for browser DOM to be initialized"""
        _ = WebDriverWait(self.browser, timeout=timeout).until(
            lambda __: self.check_document_initialised()
        )
        return True

    def goto_url(self, url=None):
        """wrapper around `selenium.webdriver.Firefox.get(<url>)`."""
        if url is None:
            url = self.url
        elif url is not None:
            url = self.format_url(url)
        self.browser.get(url)
        self.await_DOM()  # ! wait for DOM to update...
        return self.browser

    @property
    def current_url(self):
        """get the current browser URL"""
        return self.browser.current_url

    @property
    def title(self):
        """Session title.

        Returns:
        `title` (string) If provided, the user-specified title, else
        ...returns the browser window's current title.
        """
        if self._user_title is None:
            return self.browser.title
        return self._user_title

    def execute_js(self, js_string=None):
        """execute `js_string` in the browser driver.

        (defaults to loading Calc.getExpressions())
        """
        if js_string is None:
            js_string = self.js_string
        if self.url != self.current_url:
            self.goto_url(self.url)
        out = self.browser.execute_script(js_string)
        return out

    def get_expressions_from_url(self, url=None):
        """navigate to the given url, return list of JSON"""
        self.goto_url(url=url)
        expressions_list = self.execute_js()
        return expressions_list

    @cached_property
    def expressions_list(self):
        """return complete dictionary JSON output of Calc.getExpressions()."""
        return self.get_expressions_from_url()

    @property
    def latex_list(self):
        #: ! exclude null values
        return [
            expression.get('latex') for expression in self.expressions_list
            if expression.get('latex') is not None
        ]

    @property
    def output_filename(self):
        output_filename = self.title.replace(' ', '_')
        output_filename = \
            ''.join([a for a in output_filename if a.isalnum()]) + \
            '.json'
        return output_filename

    #: default output directory for downloaded latex (*.json files)
    default_output_dir = D2P_Resources\
        .get_user_resources_path()\
        .joinpath('latex_json')

    def export_latex2json(self, latex_list=None, output_filename=None,
                          output_dir=None):
        """export latex_list -> output_filename (JSON list)"""
        if latex_list is None:
            latex_list = self.latex_list
        if output_filename is None:
            output_filename = self.output_filename
        if output_dir is None:
            output_dir = DesmosWebSession.default_output_dir
        outpath = Path(output_dir) \
            .joinpath(output_filename)
        self.outpath = outpath
        with outpath.open(mode='w') as fp:
            json.dump(latex_list, fp)
        return outpath

    @staticmethod
    def get_local_js():
        """deprecated"""
        js_string = \
            importlib.resources.open_text(
                'desmos2python.resources.javascript',
                'get_latex_desmos.js').read()
        return js_string
