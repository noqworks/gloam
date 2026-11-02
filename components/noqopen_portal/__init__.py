"""NOQopen setup page for the ESPHome captive portal.

Serves the NOQopen Wi-Fi setup page in place of the stock portal page. The stock `captive_portal`
component keeps handling /config.json and /wifisave, so the provisioning logic is unchanged.
"""
import esphome.codegen as cg
from esphome.components import web_server_base
from esphome.components.web_server_base import CONF_WEB_SERVER_BASE_ID
import esphome.config_validation as cv
from esphome.const import CONF_ID

DEPENDENCIES = ["captive_portal"]
AUTO_LOAD = ["web_server_base"]

noqopen_portal_ns = cg.esphome_ns.namespace("noqopen_portal")
NoqopenPortal = noqopen_portal_ns.class_("NoqopenPortal", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(NoqopenPortal),
        cv.GenerateID(CONF_WEB_SERVER_BASE_ID): cv.use_id(web_server_base.WebServerBase),
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    base = await cg.get_variable(config[CONF_WEB_SERVER_BASE_ID])
    var = cg.new_Pvariable(config[CONF_ID], base)
    await cg.register_component(var, config)
