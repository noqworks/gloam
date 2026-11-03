"""NOQopen device pages for ESPHome.

Setup page: while the setup network is open, serves the NOQopen Wi-Fi setup page in place of the stock captive portal
page. The stock `captive_portal` component keeps handling /config.json and /wifisave, so provisioning is unchanged.

Control page (`panel: true`): on the home network, serves the NOQopen control page at / so the device can be used
without Home Assistant. The page talks to the stock `web_server` API (/events, /light/<name>/turn_on, …), which keeps
working next to the Home Assistant API; both act on the same entities.
"""
import esphome.codegen as cg
from esphome.components import web_server_base
from esphome.components.web_server_base import CONF_WEB_SERVER_BASE_ID
import esphome.config_validation as cv
from esphome.const import CONF_ID
import esphome.final_validate as fv

DEPENDENCIES = ["captive_portal"]
AUTO_LOAD = ["web_server_base"]

CONF_PANEL = "panel"

noqopen_portal_ns = cg.esphome_ns.namespace("noqopen_portal")
NoqopenPortal = noqopen_portal_ns.class_("NoqopenPortal", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(NoqopenPortal),
        cv.GenerateID(CONF_WEB_SERVER_BASE_ID): cv.use_id(web_server_base.WebServerBase),
        cv.Optional(CONF_PANEL, default=False): cv.boolean,
    }
).extend(cv.COMPONENT_SCHEMA)


def _final_validate(config):
    full = fv.full_config.get()
    if config[CONF_PANEL]:
        server = full.get("web_server")
        if server is None:
            raise cv.Invalid("'panel: true' needs the 'web_server' component (the control page uses its API)")
        if server.get("version") != 3:
            raise cv.Invalid("'panel: true' needs 'web_server' version 3")
    return config


FINAL_VALIDATE_SCHEMA = _final_validate


async def to_code(config):
    base = await cg.get_variable(config[CONF_WEB_SERVER_BASE_ID])
    var = cg.new_Pvariable(config[CONF_ID], base)
    await cg.register_component(var, config)
    if config[CONF_PANEL]:
        cg.add_define("USE_NOQOPEN_PANEL")
