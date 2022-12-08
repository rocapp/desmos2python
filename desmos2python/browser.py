"""desmos2python/browser.py

Headless browser functionality
"""
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import JavascriptException
from functools import cached_property
from pathlib import Path
from desmos2python.utils import D2P_Resources
from typing import AnyStr
import json
from threading import RLock

__all__ = [
    'DesmosWebSession',
]


class DesmosCalcStrings:

    getExpressions: str = '''
    var exprs = Calc.getExpressions();
    return exprs.filter(el => (el.latex && el.lineStyle && !el.hidden));
    '''

    getState = 'return Calc.getState()'

    expressionAnalysis = \
        '''
        var analysis_results = {};
        Calc.observe('expressionAnalysis', () => {
        for (var id in Calc.expressionAnalysis) {
        analysis_results[id] = Calc.expressionAnalysis[id];
        });
        return JSON.stringify(analysis_results)
        '''
    
    def __init__(self):
        pass

    @property
    def take_svg_screenshot(self):
        return self.get_local_js(filename='take_svg_screenshot.js')

    def get_local_js(self, filename='take_svg_screenshot.js'):
        """load a javascript command from the resources directory"""
        js_path = D2P_Resources \
            .get_package_resources_path() \
            .joinpath("javascript", filename)
        js_string = js_path.read_text()
        return js_string



class DesmosWebSession(object):
    """connect to (possibly remote) desmos graphs.

    ...via headless selenium-powered browser session.
    """

    desmos_url_head = 'https://www.desmos.com/calculator/'

    def __init__(self, url='8tb0onyoep', title: AnyStr = None):
        self._user_title = title
        self.url = self.format_url(url)
        self.outpath = None
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
            _ = self.browser.execute_script(DesmosCalcStrings.getExpressions)
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
            js_string = DesmosCalcStrings.getExpressions
        if self.url != self.current_url:
            self.goto_url(self.url)
        out = self.browser.execute_script(js_string)
        return out

    def take_svg_screenshot(self):
        """take a screenshot, return svg string."""
        self.goto_url(url=self.url)
        sshot = self.execute_js(
            js_string=DesmosCalcStrings().take_svg_screenshot
        )
        return sshot

    def getState(self):
        """get the calculator state for the current url (self.url)"""
        self.goto_url(url=self.url)
        calc_state = self.execute_js(js_string=DesmosCalcStrings.getState)
        return calc_state

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

    #: default output directory for exports
    default_output_dir = D2P_Resources\
        .get_user_resources_path()

    def export_latex2json(self, latex_list=None, output_filename=None,
                          output_dir=None):
        """export latex_list -> output_filename (JSON list)"""
        if latex_list is None:
            latex_list = self.latex_list
        if output_filename is None:
            output_filename = self.output_filename
        if output_dir is None:
            output_dir = DesmosWebSession \
                .default_output_dir \
                .joinpath('latex_json')
        outpath = Path(output_dir) \
            .joinpath(output_filename)
        self.outpath = outpath
        with outpath.open(mode='w') as fp:
            json.dump(latex_list, fp)
        return outpath

    def export_calcState(self, calc_state=None, output_filename=None,
                         output_dir=None):
        """export calculator state"""
        if calc_state is None:
            calc_state = self.getState()
        if isinstance(calc_state, str):
            calc_state = json.loads(calc_state)
        if output_filename is None:
            output_filename = self.output_filename
        if output_dir is None:
            output_dir = DesmosWebSession \
                .default_output_dir \
                .joinpath('calcState_json')
        outpath = Path(output_dir) \
            .joinpath(output_filename) \
            .with_suffix('.json')
        with outpath.open(mode='w') as fp:
            json.dump(calc_state, fp)
        return outpath

    @property
    def svg_screenshot(self):
        return self.take_svg_screenshot()

    def export_svgScreenshot(self):
        """save svg screenshot (graph) -> .svg"""
        output_dir = \
            Path(DesmosWebSession.default_output_dir) \
            .joinpath('screenshots')
        output_path = output_dir \
            .joinpath(self.output_filename) \
            .with_suffix('.svg')
        output_path.write_text(self.svg_screenshot)
        return output_path
