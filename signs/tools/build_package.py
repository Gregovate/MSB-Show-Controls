"""Embed the tested HA context into the installable package; no live HA writes."""
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
p = ROOT.parent / 'ha/packages/signs.yaml'
pkg = yaml.safe_load(p.read_text())
for key in ['msb_signs_wait_enabled']:
    pkg['input_boolean'].pop(key, None)
pkg['input_number'].pop('msb_signs_wait_minutes', None)
pkg['input_text'].pop('msb_signs_tonight_entity', None)
pkg['input_text'].pop('msb_signs_wait_entity', None)
# Keep installed legacy helpers inert, rather than silently resetting live controls.
for key in ['end_date','down_date','start_time','end_time']:
    pkg['input_datetime'].pop('msb_signs_public_'+key, None)
source = pkg['automation'][0]['actions'][0]['data']['payload']
messages = """{% set message_list = namespace(messages=[]) %}
{% for i in range(1,18) %}
  {% set p = 'msb_signs_message_' ~ i ~ '_' %}
  {% set message_list.messages = message_list.messages + [{
    'id': i, 'target': states('input_select.' ~ p ~ 'target'),
    'condition': states('input_select.' ~ p ~ 'condition'),
    'color_mode': states('input_select.' ~ p ~ 'color_mode'),
    'line1': states('input_text.' ~ p ~ 'line1'), 'line2': states('input_text.' ~ p ~ 'line2'),
    'background': states('input_text.' ~ p ~ 'background'),
    'text_color': states('input_text.' ~ p ~ 'text_color'),
    'order': states('input_number.' ~ p ~ 'order') | int(1),
    'seconds': states('input_number.' ~ p ~ 'seconds') | int(0)
  }] %}
{% endfor %}
"""
source = (ROOT / 'tools/ha_context.jinja2').read_text() + '\n' + messages + '''{{ {
  'schema': 3, 'sent_at': now().timestamp(),
  'enabled': is_state('input_boolean.msb_signs_enabled','on'),
  'gate_message_enabled': is_state('input_boolean.msb_signs_gate_message_enabled','on'),
  'screen_seconds': states('input_number.msb_signs_screen_seconds') | int(5),
  'lor_seconds': {
    'HWY 42': states('input_number.msb_signs_hwy42_lor_seconds') | int(30),
    'Front Entrance': states('input_number.msb_signs_front_lor_seconds') | int(30)
  },
  'ha': ha,
  'colors': {
    'open': states('input_text.msb_signs_color_open'),
    'closed': states('input_text.msb_signs_color_closed'),
    'light': states('input_text.msb_signs_color_light'),
    'moderate': states('input_text.msb_signs_color_moderate'),
    'busy': states('input_text.msb_signs_color_busy'),
    'very_busy': states('input_text.msb_signs_color_very_busy')
  },
  'messages': message_list.messages
} | to_json }}'''
pkg['automation'][0]['actions'][0]['data']['payload'] = source
# Retire the old manual-wait path. Slot 14 is enabled only on the Highway controller;
# missing HA data still suppresses it, and the engine enforces the target too.
for action in pkg['script']['msb_signs_load_operations']['sequence']:
    if action.get('target',{}).get('entity_id') == 'input_select.msb_signs_message_14_target':
        action['data']['option'] = 'HWY 42'
# Trigger immediate HA snapshots when controls or the known count sources change.
ids = pkg['automation'][0]['triggers'][2]['entity_id']
valid_ids = {d+'.'+k for d in ['input_boolean','input_number','input_select','input_text','input_datetime'] for k in pkg[d]}
ids[:] = [e for e in ids if not e.startswith(('input_boolean.msb_signs_', 'input_number.msb_signs_', 'input_select.msb_signs_', 'input_text.msb_signs_', 'input_datetime.msb_signs_')) or e in valid_ids]
for e in sorted(valid_ids | {'sensor.msb_traffic_status','sensor.msb_car_counter_enter_cars','sensor.msb_car_counter_show_total_cars'}):
    if e not in ids: ids.append(e)
p.write_text(yaml.safe_dump(pkg,sort_keys=False,allow_unicode=True,width=110))
