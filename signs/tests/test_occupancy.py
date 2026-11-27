"""Exercise the installed HA occupancy templates against Gate MQTT reports."""
from datetime import datetime, timedelta
from pathlib import Path
import re
import unittest
from zoneinfo import ZoneInfo

from jinja2 import Environment
import yaml

PACKAGE = yaml.safe_load((Path(__file__).resolve().parents[2] /
                          'ha/packages/traffic_analytics.yaml').read_text())
SENSORS = {s['unique_id']: s for g in PACKAGE['template'] for s in g.get('sensor', [])}
CENTRAL = ZoneInfo('America/Chicago')


class OccupancyTests(unittest.TestCase):
    def setUp(self):
        self.clock = datetime(2026, 11, 27, 17, 1, tzinfo=CENTRAL)
        self.state = {
            'binary_sensor.msb_show_open': 'on',
            'binary_sensor.msb_gate_counter_online': 'on',
            'sensor.msb_gate_occupancy_sample_time': '2026-11-27 17:00:58',
            'sensor.msb_gate_occupancy_session': 'READY',
            'sensor.msb_gate_occupancy_raw': '0',
            'input_datetime.msb_signs_public_start_date': '2026-11-27',
            'input_datetime.msb_show_end_date': '2026-12-31',
            'input_datetime.msb_show_down_date': '2026-12-24',
            'input_datetime.msb_show_start_time': '17:00:00',
        }
        self.env = Environment()
        self.env.filters['regex_match'] = lambda s, pattern: re.match(pattern, s) is not None
        self.env.globals.update(is_number=lambda v: re.fullmatch(r'-?[0-9]+', v) is not None, now=lambda: self.clock, strptime=self.parse,
                                states=lambda e: self.state.get(e, 'unknown'),
                                is_state=lambda e, v: self.state.get(e) == v)

    @staticmethod
    def parse(value, fmt, fallback):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            return fallback

    def reading(self):
        self.state['sensor.msb_gate_occupancy_diagnostic'] = self.render_sensor('msb_gate_occupancy_diagnostic')
        return self.render_sensor('msb_in_park_cars_canonical')

    def test_off_show_receiver_readback(self):
        self.state['binary_sensor.msb_show_open'] = 'off'
        self.state['sensor.msb_gate_occupancy_session'] = 'TEST'
        for value in ('-3', '0', '12'):
            self.state['sensor.msb_gate_occupancy_raw'] = value
            self.assertEqual(self.reading(), 'unavailable')
            self.assertEqual(self.state['sensor.msb_gate_occupancy_diagnostic'], value)
        self.clock += timedelta(minutes=3)
        self.assertEqual(self.render_sensor('msb_gate_occupancy_diagnostic'), 'unavailable')

    def render_sensor(self, uid):
        spec = SENSORS[uid]
        if self.env.from_string(spec['availability']).render().strip() != 'True':
            return 'unavailable'
        return self.env.from_string(spec['state']).render().strip()

    def test_valid_zero_and_signed_readings(self):
        for value in ('0', '18', '-2'):
            self.state['sensor.msb_gate_occupancy_raw'] = value
            self.assertEqual(self.reading(), value)

    def test_bad_and_offline_inputs(self):
        for key, value in [('sensor.msb_gate_occupancy_raw', v)
                           for v in ('unknown', 'unavailable', '', 'invalid', '2.5')] + [
                ('sensor.msb_gate_occupancy_session', 'TEST'),
                ('sensor.msb_gate_occupancy_sample_time', 'rtc-not-ready'),
                ('sensor.msb_gate_occupancy_sample_time', '2026-11-27 16:59:59'),
                ('sensor.msb_gate_occupancy_sample_time', '2026-11-27 17:01:06'),
                ('binary_sensor.msb_gate_counter_online', 'off')]:
            with self.subTest(key=key, value=value):
                original = self.state[key]
                self.state[key] = value
                self.assertEqual(self.reading(), 'unavailable')
                self.state[key] = original

    def test_stale_retained_sample_and_recovery(self):
        self.clock += timedelta(minutes=3)
        self.assertEqual(self.reading(), 'unavailable')
        self.state['sensor.msb_gate_occupancy_sample_time'] = '2026-11-27 17:04:00'
        self.assertEqual(self.reading(), '0')

    def test_closed_reset_preseason_and_extension(self):
        for day, hour, minute, opened, expected in [
                (25, 17, 0, 'on', 'unavailable'), (27, 16, 59, 'off', 'unavailable'),
                (27, 21, 10, 'on', '0'), (27, 21, 20, 'off', 'unavailable')]:
            self.clock = self.clock.replace(day=day, hour=hour, minute=minute)
            self.state['binary_sensor.msb_show_open'] = opened
            self.state['sensor.msb_gate_occupancy_sample_time'] = self.clock.strftime('%Y-%m-%d %H:%M:%S')
            self.assertEqual(self.reading(), expected)

    def test_null_heartbeat_and_snapshot(self):
        mqtt_sensor = next(s for s in PACKAGE['mqtt']['sensor'] if s['unique_id'] == 'msb_gate_occupancy_sample_time')
        t = self.env.from_string(mqtt_sensor['value_template'])
        self.assertEqual(t.render(value_json={'now': '2026-11-27 17:01:00', 'inpark': None}), 'unknown')
        self.assertEqual(t.render(value_json={'now': '2026-11-27 17:01:00', 'inpark': 0}), '2026-11-27 17:01:00')
        attribute = SENSORS['msb_traffic_status_snapshot']['attributes']['in_park_cars']
        self.assertEqual(self.env.from_string(attribute).render(), 'None')

    def test_opening_night_analytics_with_unavailable_diagnostic(self):
        self.clock = self.clock.replace(hour=17, minute=30, second=42)
        self.state.update({
            'sensor.msb_gate_occupancy_diagnostic': 'unavailable',
            'sensor.msb_gate_occupancy_raw': '100',
            'sensor.msb_gate_occupancy_sample_time': '2026-11-27 17:30:38',
            'binary_sensor.msb_gate_counter_gate_counter_online': 'on',
            'binary_sensor.msb_gatecounter_analytics_active': 'on',
            # Controlled rates exercise the estimates. They are not field measurements.
            'sensor.msb_exit_rate_cars_min': '4',
            'sensor.msb_enter_rate_cars_min': '5',
            'sensor.msb_flow_delta_cars_min': '1',
        })
        chain = [
            ('msb_in_park_cars_canonical', '100'),
            ('msb_in_park_cars_band', 'medium'),
            ('msb_travel_time_estimate_min', '25.0'),
            ('msb_travel_time_band', 'busy'),
            ('msb_traffic_pressure', 'medium'),
            ('msb_traffic_status', 'busy'),
            ('msb_traffic_status_snapshot', 'busy'),
        ]
        for delay in (0, 121):
            self.clock += timedelta(seconds=delay)
            for uid, fresh_value in chain:
                value = self.render_sensor(uid)
                self.assertEqual(value, fresh_value if delay == 0 else 'unavailable', uid)
                self.state['sensor.' + uid] = value
