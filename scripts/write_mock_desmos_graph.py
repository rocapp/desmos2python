# coding: utf-8
import json
import jinja2cli

out = jinja2cli.cli.render(
    'desmos2python/resources/templates/desmos_mock_graph.html.jinja2',
    {'calc_state_json': json.load(open('/home/rcapps/.desmos2python/calcState_json/withCortisolimagev3Circadianultradianglucosepatterns.json'))}, []
)
with open('/home/rcapps/pfun/resources/desmos_mock_graph.html', 'w') as f:
    f.write(out)
