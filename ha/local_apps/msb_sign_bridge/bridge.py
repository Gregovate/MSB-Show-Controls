"""MSB Sign Bridge 0.3.1. HA owns messages, colors, timing and show settings."""

import json
import logging
import queue
import signal
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import paho.mqtt.client as mqtt
import sacn
from PIL import Image, ImageDraw, ImageFont

from engine import playlist, validate

TOPIC = "msb/signs/bridge"
SIGNS = {"HWY 42": ("10.10.5.21", 357), "Front Entrance": ("10.10.5.20", 340)}
FONT = "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
STOP = threading.Event()
CONNECTED = threading.Event()
INBOX = queue.SimpleQueue()
LOG = logging.getLogger("sign_bridge")


def render(message):
    """Preserve the tested matrix half reversal, zigzag and GRB order."""
    image = Image.new("RGB", (80, 34), message["background"])
    draw = ImageDraw.Draw(image)
    for text, top in zip(message["lines"], (1, 18)):
        for size in range(20, 5, -1):
            font = ImageFont.truetype(FONT, size)
            left, upper, right, lower = draw.textbbox((0, 0), text, font=font)
            width, height = right - left, lower - upper
            if width <= 78 and height <= 14:
                break
        else:
            raise ValueError(f"Message {message['id']}: text does not fit: {text}")
        draw.text(((80-width)//2-left, top+(15-height)//2-upper), text,
                  font=font, fill=message["text_color"])
    pixels = [(0, 0, 0)] * 2720
    for y in range(34):
        offset = 1360 if y < 17 else 0
        row = 16-y if y < 17 else 33-y
        for x in range(80):
            position = 80-x if row % 2 == 0 else x+1
            red, green, blue = image.getpixel((x, y))
            pixels[offset + row*80 + position - 1] = (green, red, blue)
    return [tuple(v for pixel in pixels[i:i+170] for v in pixel)
            for i in range(0, 2720, 170)]


class Sign:
    """Own a separate sACN sender and rotation clock for each sign."""

    def __init__(self, name, lighting_ip):
        self.name, self.lighting_ip = name, lighting_ip
        self.sender = None
        self.phase = "idle"
        self.started = 0.0
        self.current = None
        self.last_frame = None
        self.status = "Waiting for Home Assistant"

    def release(self, reason):
        if self.sender is not None:
            self.sender.stop()
            self.sender = None
        self.current = None
        self.last_frame = None
        self.phase = "idle"
        self.status = reason

    def show(self, message):
        # Render first; a bad edit must not leave an old frame on a sign.
        frame = render(message)
        address, first = SIGNS[self.name]
        if self.sender is None:
            sender = sacn.sACNsender(
                bind_address=self.lighting_ip, bind_port=0,
                source_name="MSB Signs " + self.name, universeDiscovery=False,
            )
            try:
                for i in range(16):
                    sender.activate_output(first+i)
                    output = sender[first+i]
                    output.destination = address
                    output.multicast = False
                    output.priority = 150
                    output.dmx_data = frame[i]
                sender.start()
            except BaseException:
                sender.stop()
                raise
            self.sender = sender
        else:
            for i in range(16):
                self.sender[first+i].dmx_data = frame[i]
        self.last_frame = message
        self.status = " / ".join(message["lines"])

    def step(self, messages, lor_seconds, tick, continuous=False, urgent=False):
        if not messages:
            self.release("Released to LOR: no eligible messages")
            return
        # Emergency/explicit closure must interrupt an overlay or LOR interval
        # immediately, rather than wait for its previous rotation timer.
        if urgent and (self.phase != "overlay" or self.current not in [m["id"] for m in messages]):
            self.phase = "idle"
        if self.phase == "lor":
            if tick-self.started < lor_seconds:
                return
            self.phase = "idle"
        if self.phase == "idle":
            self.current = messages[0]["id"]
            self.started, self.phase = tick, "overlay"
        ids = [m["id"] for m in messages]
        if self.current not in ids:
            self.current, self.started = ids[0], tick
        index = ids.index(self.current)
        current = messages[index]
        if tick-self.started >= current["seconds"]:
            if index+1 == len(messages) and continuous:
                self.current, self.started = ids[0], tick
                current = messages[0]
                if current != self.last_frame:
                    self.show(current)
                return
            if index+1 == len(messages):
                self.release("Released to LOR")
                self.phase, self.started = "lor", tick
                return
            self.current, self.started = ids[index+1], tick
            current = messages[index+1]
        if current != self.last_frame:
            self.show(current)


def on_connect(client, userdata, flags, reason, properties):
    if reason != 0:
        LOG.error("MQTT login rejected: %s", reason)
        return
    client.subscribe(TOPIC + "/control", qos=1)
    client.subscribe(TOPIC + "/release", qos=1)
    client.publish(TOPIC + "/availability", "online", qos=1, retain=True)
    CONNECTED.set()
    LOG.info("MQTT connected; waiting for a fresh HA control snapshot")


def on_disconnect(client, userdata, flags, reason, properties):
    CONNECTED.clear()
    INBOX.put(("disconnect", None))


def on_message(client, userdata, message):
    if message.topic.endswith("/release"):
        if not message.retain:
            INBOX.put(("release", None))
        return
    try:
        config = validate(json.loads(message.payload))
        # Retained snapshots are allowed only within their original expiry.
        age = time.time()-float(config["sent_at"])
        if not -5 <= age < 35:
            raise ValueError("Control snapshot is stale or clock is incorrect")
        INBOX.put(("control", config))
    except Exception as exc:
        LOG.error("Rejected HA settings: %s", exc)
        INBOX.put(("invalid", str(exc)))


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    options = json.loads(Path("/data/options.json").read_text())
    signs = {name: Sign(name, options["lighting_ip"]) for name in SIGNS}
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="msb-sign-bridge")
    if options["mqtt_username"]:
        client.username_pw_set(options["mqtt_username"], options["mqtt_password"])
    client.will_set(TOPIC+"/availability", "offline", qos=1, retain=True)
    client.on_connect, client.on_disconnect, client.on_message = on_connect, on_disconnect, on_message
    client.reconnect_delay_set(1, 30)
    signal.signal(signal.SIGTERM, lambda *_: STOP.set())
    signal.signal(signal.SIGINT, lambda *_: STOP.set())
    config, fresh_until = None, 0.0
    blocked = False
    error = ""
    last_state, last_publish = None, 0.0
    client.connect_async(options["mqtt_host"], options["mqtt_port"], 15)
    client.loop_start()
    try:
        while not STOP.is_set():
            while True:
                try:
                    kind, value = INBOX.get_nowait()
                except queue.Empty:
                    break
                if kind == "control":
                    config = value
                    remaining = max(0, 35-(time.time()-float(config["sent_at"])))
                    fresh_until = time.monotonic()+remaining
                    # Release latches until HA confirms the master is OFF.
                    if not config["enabled"]:
                        blocked = False
                    error = ""
                elif kind == "release":
                    blocked = True
                else:
                    config = None
                    error = value or "MQTT disconnected"
            tick = time.monotonic()
            now = datetime.now(timezone.utc)
            healthy = CONNECTED.is_set() and config is not None and tick < fresh_until
            ctx = None
            for name, sign in signs.items():
                try:
                    if not healthy or blocked:
                        sign.release("Released to LOR: " + ("manual release" if blocked else "waiting for fresh HA settings"))
                    else:
                        messages, ctx = playlist(config, name, now)
                        sign.step(messages, config["lor_seconds"][name], tick, continuous=ctx["preshow"] or ctx["weather_closed"] or ctx["admissions_closed"] or ctx["clearing_queue"], urgent=ctx["weather_closed"] or ctx["admissions_closed"])
                except Exception as exc:
                    new_error = f"{name}: {exc}"
                    if error != new_error:
                        LOG.error("%s", new_error)
                    error = new_error
                    sign.release("Released to LOR: configuration error")
            state = {
                "hwy42": signs["HWY 42"].status,
                "front": signs["Front Entrance"].status,
                "controls_fresh": healthy,
                "gates_open": ctx["gates_open"] if ctx else False,
                "closing_time": ctx["closing_time"] if ctx else "Unavailable",
                "error": error,
                "version": "0.3.1",
                "wait_status": ctx.get("wait_status", "Waiting for HA") if ctx else "Waiting for HA",
                "schedule_status": ctx["schedule_status"] if ctx else "Waiting for settings",
            }
            body = json.dumps(state)
            if CONNECTED.is_set() and (body != last_state or tick-last_publish >= 10):
                client.publish(TOPIC+"/state", body, qos=1, retain=True)
                if body != last_state:
                    LOG.info("%s", body)
                last_state, last_publish = body, tick
            STOP.wait(0.1)
    finally:
        try:
            for sign in signs.values():
                sign.release("Bridge stopped")
        finally:
            if CONNECTED.is_set():
                client.publish(TOPIC+"/availability", "offline", qos=1, retain=True).wait_for_publish(2)
            client.disconnect()
            client.loop_stop()


if __name__ == "__main__":
    main()
