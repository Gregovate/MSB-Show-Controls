"""Store kiosk season car sheets using the park's row lookup and sheet helpers."""
import asyncio
from datetime import date
import logging
from functools import partial
from types import SimpleNamespace

import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError

from .car_sheet import import_sheet

DOMAIN = "msb_show_sheet"
CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({vol.Optional("rehearsal_workbook"): vol.All(str, vol.Match(r"^[A-Za-z0-9_-]+$"))})}, extra=vol.ALLOW_EXTRA
)
LOG = logging.getLogger(__name__)


async def async_setup(hass, config):
    # All device fetches, Google API calls and connection setup run off the HA event loop.
    lock = asyncio.Lock()
    settings = hass.config.path("msb-show-sheets.json")

    rehearsal = config[DOMAIN].get("rehearsal_workbook")
    report = hass.config.path("msb-rehearsal-buckets.csv") if rehearsal else None

    async def sync(call):
        day = call.data.get("closing_date")
        try:
            async with lock:
                count = await hass.async_add_executor_job(
                    partial(import_sheet, rehearsal_book=rehearsal, report_file=report), SimpleNamespace(credentials=settings, write=True),
                    date.fromisoformat(day) if day else None
                )
        except Exception as exc:
            raise HomeAssistantError(f"Car sheet sync failed: {exc}") from exc
        LOG.info("Car sheet sync complete: %s rows written", count)

    hass.services.async_register(DOMAIN, "sync", sync,
                                 schema=vol.Schema({vol.Optional("closing_date"): str}))
    return True
