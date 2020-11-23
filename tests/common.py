"""Test helper variables or methods."""
import json
import os

from unittest.mock import patch
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.carson import DOMAIN

CARSON_API_VERSION = "1.4.3"
CONF_AND_FORM_CREDS = {"username": "foo@bar.com", "password": "bar"}


async def setup_platform(hass, platform):
    """Set up the ring platform and prerequisites."""
    MockConfigEntry(
        domain=DOMAIN,
        data={
            "username": CONF_AND_FORM_CREDS["username"],
            "password": CONF_AND_FORM_CREDS["password"],
            "token": fixture_token(),
        },
    ).add_to_hass(hass)
    with patch("custom_components.carson.PLATFORMS", [platform]):
        assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()


def carson_load_fixture(filename):
    """Return file content from Carson fixture subfolder."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()


def fixture_building_id():
    """Return Fixture Building ID from Payload."""
    return json.loads(carson_load_fixture("carson_me.json"))["data"]["properties"][0][
        "id"
    ]


def fixture_een_subdomain():
    """Return Fixture EEN Subdomain from Payload."""
    return json.loads(carson_load_fixture("carson_eagleeye_session.json"))["data"][
        "activeBrandSubdomain"
    ]


def fixture_token():
    """Return Fixture Token from Payload."""
    return json.loads(carson_load_fixture("carson_login.json"))["data"]["token"]
