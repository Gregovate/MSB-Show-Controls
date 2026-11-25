"""Offline tests of actual HA templates and downstream rendering. No live MQTT."""
import copy
import json
from pathlib import Path
import sys
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import patch
import yaml
from jinja2 import Environment
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'ha/local_apps/msb_sign_bridge'))
import engine, bridge
ZONE=ZoneInfo('America/Chicago')
ANALYTICS=yaml.safe_load((ROOT.parent/'ha/packages/traffic_analytics.yaml').read_text())
QUEUE=yaml.safe_load((ROOT.parent/'ha/packages/sign2_queue_wait.yaml').read_text())
PACKAGE=yaml.safe_load((ROOT.parent/'ha/packages/signs.yaml').read_text())

def number(value):
 try:return float(value)==float(value) and abs(float(value))!=float('inf')
 except (TypeError,ValueError):return False

def state_fixture():
 state={}
 for domain in ['input_datetime','input_select']:
  for k,v in PACKAGE[domain].items():
   if 'initial' in v:state[domain+'.'+k]=str(v['initial'])
 for script in ['msb_signs_initialize','msb_signs_load_preshow','msb_signs_load_operations']:
  for action in PACKAGE['script'][script]['sequence']:
   if 'action' not in action or 'target' not in action:continue
   entities=action['target']['entity_id'];entities=entities if isinstance(entities,list) else [entities]
   data=action.get('data',{})
   for e in entities:state[e]=str(next(iter(data.values()))) if data else ('on' if action['action'].endswith('turn_on') else 'off')
 state.update({'input_boolean.msb_signs_enabled':'on','input_boolean.msb_signs_promotion_enabled':'off',
  'input_boolean.msb_signs_weather_closed':'off','input_select.msb_signs_admission_state':'Automatic',
  'input_datetime.msb_show_start_date':'2026-11-18','input_datetime.msb_show_end_date':'2026-12-31',
  'input_datetime.msb_show_down_date':'2026-12-24','input_datetime.msb_show_start_time':'17:00:00',
  'input_datetime.msb_show_end_time':'21:00:00','input_number.show_end_extension_min':'0',
  'input_text.msb_traffic_extension_date':'','input_boolean.msb_show_force_close':'off',
  'sensor.msb_traffic_status':'light','binary_sensor.msb_car_counter_online':'on',
  'binary_sensor.msb_gate_counter_online':'on','sensor.msb_car_counter_enter_cars':'123',
  'sensor.msb_car_counter_show_total_cars':'456','sensor.msb_gate_counter_in_park_cars':'45',
  'sensor.msb_sign2_queue_wait_minutes':'12.1'})
 return state

def payload(state,when='2026-11-27T18:00:00'):
 stamp=datetime.fromisoformat(when).replace(tzinfo=ZONE)
 def asdt(value):
  try:return datetime.fromisoformat(value)
  except (ValueError,TypeError):return None
 def timestamp(value,default=0):
  try:
   dt=asdt(value);return dt.replace(tzinfo=ZONE).timestamp() if dt.tzinfo is None else dt.timestamp()
  except (ValueError,TypeError):return default
 env=Environment();env.filters['to_json']=json.dumps
 env.globals.update(states=lambda e:state.get(e,'unknown'),is_state=lambda e,v:state.get(e)==v,
  is_number=number,now=lambda:stamp,timedelta=timedelta,
  today_at=lambda t:datetime.combine(stamp.date(),datetime.strptime(t,'%H:%M:%S').time(),ZONE),
  as_timestamp=timestamp,as_datetime=asdt,has_value=lambda e:state.get(e,'unknown') not in ['unknown','unavailable',''])
 attrs={}
 env.globals['state_attr']=lambda e,k:attrs.get(e,{}).get(k)
 clock=next(s for g in ANALYTICS['template'] for s in g.get('sensor',[]) if s.get('unique_id')=='msb_effective_entry_closing_time')
 state['sensor.msb_effective_entry_closing_time']=env.from_string(clock['state']).render().strip()
 attrs['sensor.msb_effective_entry_closing_time']={'public_start':env.from_string(clock['attributes']['public_start']).render().strip()}
 template=PACKAGE['automation'][0]['actions'][0]['data']['payload']
 return engine.validate(json.loads(env.from_string(template).render()))

class TestHAContract(unittest.TestCase):
 def setUp(self):self.state=state_fixture()
 def items(self,when='2026-11-27T18:00:00',sign='HWY 42'):
  cfg=payload(self.state,when);return engine.playlist(cfg,sign,datetime.now(ZONE))
 def test_real_count_entities(self):
  items,_=self.items();by={m['id']:m for m in items}
  self.assertEqual(by[12]['lines'],['TRAFFIC TONIGHT','123 CARS'])
  self.assertEqual(by[13]['lines'],['TRAFFIC SEASON','456 CARS'])
 def test_counter_season_date_does_not_enable_public_signs_early(self):
  items,ctx=self.items('2026-11-25T18:30:00')
  self.assertFalse(ctx['gates_open']);self.assertTrue(ctx['preshow'])
  self.assertEqual(next(m for m in items if m['id']==9)['lines'],['OPENS','NOV 27'])
 def test_thursday(self):
  items,_=self.items('2026-11-26T16:00:00')
  self.assertEqual(next(m for m in items if m['id']==9)['lines'],['OPEN TOMORROW','5 PM'])
 def test_friday_morning(self):
  items,ctx=self.items('2026-11-27T05:00:00');i=next(i for i,m in enumerate(items) if m['id']==9)
  self.assertEqual(items[i]['lines'],['OPEN TONIGHT','']);self.assertEqual(items[i+1]['lines'],['GATES OPEN','5 PM'])
 def test_advertising_boundaries(self):
  for t,allowed in [('04:59:59',False),('05:00:00',True),('08:00:00',False),('16:00:00',True),('21:00:00',False)]:
   with self.subTest(t=t):self.assertEqual(payload(self.state,'2026-11-25T'+t)['ha']['allowed'],allowed)
 def test_warmup_countdown_rotates_without_opening_counts(self):
  self.state['input_datetime.production_radio_on']='16:30:00'
  for day in ('2026-11-27','2026-11-28'):
   for sign in ('HWY 42','Front Entrance'):
    for clock,minutes in [('16:30:00','30 MINUTES'),('16:59:59','1 MINUTE')]:
     items,ctx=self.items(day+'T'+clock,sign)
     self.assertFalse(ctx['gates_open'])
     self.assertEqual(next(m['lines'] for m in items if m['id']==9),['GATES OPEN IN',minutes])
    self.assertFalse(any(m['lines'][0]=='GATES OPEN IN' for m in self.items(day+'T17:00:00',sign)[0]))
  for stamp in ['2026-11-28T16:29:59','2026-12-24T16:45:00','2026-11-26T16:45:00']:
   self.assertFalse(any(m['lines'][0]=='GATES OPEN IN' for m in self.items(stamp)[0]))
  self.state['input_boolean.msb_show_force_close']='on'
  self.assertEqual(self.items('2026-11-28T16:45:00')[0],[])
 def test_public_boundaries(self):
  for t,opened in [('16:59:59',False),('17:00:00',True),('20:59:59',True),('21:00:00',False)]:
   self.assertEqual(payload(self.state,'2026-11-27T'+t)['ha']['gates_open'],opened)
 def test_shared_extension_changes_time_and_window(self):
  self.state.update({'input_number.show_end_extension_min':'25','input_text.msb_traffic_extension_date':'20261127'})
  items,ctx=self.items('2026-11-27T21:15:00')
  self.assertTrue(ctx['gates_open']);self.assertEqual(ctx['closing_time'],'9:25 PM')
  self.assertEqual(next(m for m in items if m['id']==16)['lines'],['ENTRY CLOSES','9:25 PM'])
  self.assertFalse(payload(self.state,'2026-11-27T21:25:00')['ha']['gates_open'])
 def test_old_extension_expires(self):
  self.state.update({'input_number.show_end_extension_min':'25','input_text.msb_traffic_extension_date':'20261126'})
  self.assertFalse(payload(self.state,'2026-11-27T21:15:00')['ha']['gates_open'])
 def test_extension_across_midnight_uses_previous_operating_day(self):
  self.state.update({'input_datetime.msb_show_end_time':'23:50:00','input_number.show_end_extension_min':'25','input_text.msb_traffic_extension_date':'20261127'})
  c=payload(self.state,'2026-11-28T00:10:00')
  self.assertTrue(c['ha']['gates_open']);self.assertEqual(c['ha']['closing_time'],'12:15 AM')
  self.assertFalse(payload(self.state,'2026-11-28T00:15:00')['ha']['gates_open'])
 def test_invalid_public_hours_fail_closed(self):
  self.state['input_datetime.msb_show_end_time']='unavailable'
  self.assertFalse(payload(self.state)['ha']['allowed'])
 def test_existing_admin_end_time_is_used(self):
  self.state['input_datetime.msb_show_end_time']='22:00:00'
  self.assertEqual(payload(self.state)['ha']['closing_time'],'10:00 PM')
 def test_down_date(self):self.assertFalse(payload(self.state,'2026-12-24T18:00:00')['ha']['gates_open'])
 def test_weather_priority_after_hours_and_force_close(self):
  self.state.update({'input_boolean.msb_signs_weather_closed':'on','input_boolean.msb_show_force_close':'on'})
  for sign in ['HWY 42','Front Entrance']:
   items,_=self.items('2026-11-27T23:00:00',sign)
   self.assertEqual(len(items),1);self.assertEqual(items[0]['lines'],['CLOSED','WEATHER']);self.assertEqual(items[0]['background'],(12,0,0))
 def test_master_disable_releases_weather(self):
  self.state.update({'input_boolean.msb_signs_weather_closed':'on','input_boolean.msb_signs_enabled':'off'})
  self.assertEqual(self.items()[0],[])
 def test_no_automatic_closed_at_cutoff(self):self.assertEqual(self.items('2026-11-27T21:00:00')[0],[])
 def test_queue_clearing_does_not_say_closed(self):
  self.state['input_select.msb_signs_admission_state']='Clearing queue'
  items,ctx=self.items('2026-11-27T21:20:00')
  self.assertTrue(ctx['admitting']);self.assertEqual(next(m for m in items if m['id']==15)['lines'],['ALREADY IN LINE?','YOU MAY ENTER'])
  self.assertNotIn(16,[m['id'] for m in items]);self.assertFalse(any('CLOSED' in line for m in items for line in m['lines']))
 def test_closed_is_explicit(self):
  self.state['input_select.msb_signs_admission_state']='Closed'
  self.assertEqual(self.items()[0][0]['lines'],['ENTRY CLOSED','THANK YOU'])
 def test_traffic_is_pass_through_not_recalculated(self):
  self.state['sensor.msb_traffic_status']='busy'
  items,_=self.items();self.assertEqual(next(m for m in items if m['id']==5)['lines'],['TRAFFIC','BUSY'])
  self.state['sensor.msb_traffic_status']='closed'
  self.assertNotIn(5,[m['id'] for m in self.items()[0]])
 def test_sign2_wait_from_ha_only(self):
  self.assertEqual(next(m for m in self.items()[0] if m['id']==14)['lines'],['EST WAIT TIME','13 MIN'])
  self.assertNotIn(14,[m['id'] for m in self.items(sign='Front Entrance')[0]])
 def test_wait_cannot_be_misassigned_even_when_both_selected(self):
  self.state['input_select.msb_signs_message_14_target']='Both'
  self.assertNotIn(14,[m['id'] for m in self.items(sign='Front Entrance')[0]])
 def test_inpark_time_cannot_be_used_as_queue_wait(self):
  self.state.update({'sensor.msb_sign2_queue_wait_minutes':'unknown','sensor.msb_travel_time_estimate_min':'45'})
  self.assertNotIn(14,[m['id'] for m in self.items()[0]])
 def test_missing_wait_hidden(self):
  for value in ['unknown','unavailable','-1','nan']:
   self.state['sensor.msb_sign2_queue_wait_minutes']=value
   self.assertNotIn(14,[m['id'] for m in self.items()[0]])
 def test_missing_counts_not_zero(self):
  self.state['sensor.msb_car_counter_enter_cars']='unavailable'
  self.assertNotIn(12,[m['id'] for m in self.items()[0]])
 def test_offline_counter_hides_live_wait_and_traffic(self):
  self.state['binary_sensor.msb_car_counter_online']='off'
  self.assertTrue({5,12,13,14}.isdisjoint({m['id'] for m in self.items()[0]}))
 def test_old_schema_rejected(self):
  c=payload(self.state);c['schema']=2
  with self.assertRaises(AssertionError):engine.validate(c)
 def test_no_manual_wait_or_duplicate_public_hours_helpers(self):
  self.assertNotIn('msb_signs_wait_minutes',PACKAGE['input_number'])
  self.assertNotIn('msb_signs_public_end_time',PACKAGE['input_datetime'])
 def test_downstream_occupancy_availability(self):
  sensors={s['unique_id']:s for g in ANALYTICS['template'] for s in g.get('sensor',[])}
  env=Environment()
  for reading in ('0','-2','12','unavailable'):
   data={'sensor.msb_in_park_cars_canonical':reading,'binary_sensor.msb_show_open':'on'}
   env.globals.update(states=lambda k:data.get(k,'unknown'),is_state=lambda k,v:data.get(k)==v,is_number=number)
   render=lambda uid,field:env.from_string(sensors['msb_'+uid][field]).render().strip()
   for uid in ['traffic_status','traffic_status_snapshot','traffic_status_json','travel_time_estimate_min','lane_2_advisory']:
    self.assertEqual(render(uid,'availability')=='True',number(reading),uid)
   data['binary_sensor.msb_show_open']='off'
   self.assertEqual(render('traffic_status','state'),'closed')
   self.assertEqual(render('traffic_status','availability'),'True')
 def test_reviewed_traffic_sensor_definitions(self):
  import hashlib
  expected=json.loads((ROOT/'tests/analytics_preservation.json').read_text())
  actual={s['unique_id']:hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest() for g in ANALYTICS['template'] for s in g.get('sensor',[])}
  for uid,digest in expected.items():self.assertEqual(actual[uid],digest,uid)
 def test_package_generation_is_reproducible(self):
  import subprocess
  p=ROOT.parent/'ha/packages/signs.yaml';before=p.read_bytes()
  subprocess.run([sys.executable,str(ROOT/'tools/build_package.py')],check=True)
  self.assertEqual(before,p.read_bytes())

class TestQueueEstimator(unittest.TestCase):
 def setUp(self):
  self.state={'input_boolean.msb_sign2_wait_estimator_enabled':'on',
   'binary_sensor.msb_show_open':'on','binary_sensor.msb_car_counter_online':'on',
   'binary_sensor.msb_gate_counter_online':'on','input_boolean.lane_2_open':'off',
   'sensor.msb_in_park_cars_canonical':'90','sensor.msb_enter_rate_cars_s':str(5/60),
   'sensor.msb_exit_rate_cars_s':str(5/60),'sensor.msb_traffic_status':'moderate',
   'input_number.msb_sign2_vehicle_pitch_ft':'26.4','input_number.msb_sign2_free_flow_mph':'5'}
 def estimate(self):
  env=Environment();env.globals.update(states=lambda e:self.state.get(e,'unknown'),
    is_state=lambda e,v:self.state.get(e)==v,is_number=number)
  sensor=QUEUE['template'][0]['sensor'][0]
  if env.from_string(sensor['availability']).render().strip().lower()!='true':return None
  return int(env.from_string(sensor['state']).render().strip())
 def test_measured_segment_and_service_rate(self):self.assertEqual(self.estimate(),7)
 def test_downstream_backlog_constrains_service(self):
  self.state.update({'sensor.msb_in_park_cars_canonical':'150','sensor.msb_exit_rate_cars_s':str(2/60)})
  self.assertEqual(self.estimate(),16)
 def test_two_lane_upper_bias(self):
  self.state['input_boolean.lane_2_open']='on';self.assertEqual(self.estimate(),13)
 def test_light_load_free_flow(self):
  self.state.update({'sensor.msb_in_park_cars_canonical':'45','sensor.msb_traffic_status':'light'})
  self.assertEqual(self.estimate(),2)
 def test_stalled_loaded_park_does_not_fabricate_minutes(self):
  self.state.update({'sensor.msb_in_park_cars_canonical':'150','sensor.msb_exit_rate_cars_s':'0'})
  self.assertIsNone(self.estimate())
 def test_bad_data_offline_closed_or_disabled(self):
  for key,value in [('input_boolean.msb_sign2_wait_estimator_enabled','off'),('binary_sensor.msb_show_open','off'),
   ('binary_sensor.msb_gate_counter_online','off'),('input_boolean.lane_2_open','unknown'),
   ('sensor.msb_in_park_cars_canonical','-5'),('sensor.msb_enter_rate_cars_s','0'),
   ('sensor.msb_enter_rate_cars_s','unknown'),('sensor.msb_exit_rate_cars_s','-0.1')]:
   before=dict(self.state);self.state[key]=value
   with self.subTest(key=key):self.assertIsNone(self.estimate())
   self.state=before

class FakeSender:
 def __init__(self,**kw):self.outputs={};self.stopped=False
 def activate_output(self,u):self.outputs[u]=type('Output',(),{})()
 def __getitem__(self,u):return self.outputs[u]
 def start(self):pass
 def stop(self):self.stopped=True

class TestOutput(unittest.TestCase):
 def test_emergency_interrupts_lor(self):
  with patch.object(bridge,'render',return_value=[(0,)*510]*16),patch.object(bridge.sacn,'sACNsender',FakeSender):
   s=bridge.Sign('HWY 42','10.10.5.4');s.phase='lor';s.started=100
   m={'id':900,'lines':['CLOSED','WEATHER'],'background':(12,0,0),'text_color':(100,100,100),'seconds':7}
   s.step([m],60,101,continuous=True,urgent=True);self.assertEqual(s.current,900);self.assertEqual(s.phase,'overlay')
   sender=s.sender;s.step([],60,102);self.assertTrue(sender.stopped)
 def test_actual_render_mapping(self):
  with patch.object(bridge,'FONT','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
   frame=bridge.render({'id':1,'lines':['',''],'background':(1,2,3),'text_color':(0,0,0)})
  self.assertEqual(len(frame),16);self.assertTrue(all(u==(2,1,3)*170 for u in frame))
 def test_every_installed_message_renders(self):
  c=payload(state_fixture());c['ha'].update(clearing_queue=True,preshow=False,admitting=True)
  with patch.object(bridge,'FONT','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
   for m in engine.playlist(c,'HWY 42',datetime.now(ZONE))[0]:self.assertEqual(len(bridge.render(m)),16)

if __name__=='__main__':unittest.main(verbosity=2)
