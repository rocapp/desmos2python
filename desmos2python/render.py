import base64
import json
import jinja2cli
from desmos2python.utils import D2P_Resources
from desmos2python.browser import DesmosWebSession

default_template_fpath = D2P_Resources.get_package_resources_path() \
    .joinpath('templates', 'desmos_mock_graph.html.jinja2')


def render_jinja_html(template_fpath = default_template_fpath,
                      data_fpath = None, data = {}, output_fpath=None):
    if data_fpath is not None:
        with open(data_fpath, 'r') as fp:
            data_new = json.load(fp)
            data_new.update(data)
            data = data_new
    out = jinja2cli.cli.render(template_fpath, data, [])
    if output_fpath is not None:
        with open(output_fpath, 'w') as f:
            f.write(out)
    return out


def format_html_string_for_driver(innerHtml: str):
    """Render html string (including css, javascript) for selenium driver.

    References:
    -----------
    ref: https://stackoverflow.com/questions/22538457/put-a-string-with-html-javascript-into-selenium-webdriver
    answer: https://stackoverflow.com/a/65446466/1871569
    """
    html_bs64 = base64.b64encode(innerHtml.encode('utf-8')).decode()
    return "data:text/html;base64," + html_bs64


def make_web_session_with_state(state_fname='withCortisolimagev3Circadianultradianglucosepatterns.json', ret_data=False):
    data_str = D2P_Resources.get_user_resources_path() \
                            .joinpath('calcState_json', state_fname) \
                            .read_text()
    data = {'calc_state_json': json.loads(data_str)}
    innerHtml = render_jinja_html(data=data)
    url_str = format_html_string_for_driver(innerHtml)
    dws = DesmosWebSession(url=url_str)
    if ret_data is True:
        return dws, data
    return dws


if __name__ == '__main__':
    dws = make_web_session_with_state()
    print('dws = ', dws)
    print()
