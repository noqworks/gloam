#include "noqopen_portal.h"
#include "portal_page.h"
#ifdef USE_NOQOPEN_PANEL
#include "panel_page.h"
#include "icon_png.h"
#endif

#include <string>

#include "esphome/core/application.h"
#include "esphome/core/log.h"
#include "esphome/components/captive_portal/captive_portal.h"

namespace esphome::noqopen_portal {

static const char *const TAG = "noqopen_portal";

void NoqopenPortal::setup() { this->base_->add_handler_without_auth(this); }

void NoqopenPortal::dump_config() {
  ESP_LOGCONFIG(TAG, "NOQopen setup page: %u bytes", static_cast<unsigned>(sizeof(PAGE_GZ)));
#ifdef USE_NOQOPEN_PANEL
  ESP_LOGCONFIG(TAG, "NOQopen control page: %u bytes", static_cast<unsigned>(sizeof(PANEL_GZ)));
#endif
}

bool NoqopenPortal::setup_open_() {
  auto *portal = captive_portal::global_captive_portal;
  return portal != nullptr && portal->is_active();
}

bool NoqopenPortal::canHandle(AsyncWebServerRequest *request) const {
  if (request->method() != HTTP_GET)
    return false;
#ifdef USE_ESP32
  char buf[AsyncWebServerRequest::URL_BUF_SIZE];
  StringRef url = request->url_to(buf);
#else
  const auto &url = request->url();
#endif
#ifdef USE_NOQOPEN_PANEL
  // home screen shortcut: icon and web app manifest, on either network
  if (url == ESPHOME_F("/icon.png") || url == ESPHOME_F("/manifest.webmanifest"))
    return true;
#endif
  if (setup_open_())
    return !(url == ESPHOME_F("/config.json") || url == ESPHOME_F("/wifisave"));
#ifdef USE_NOQOPEN_PANEL
  return url == ESPHOME_F("/") || url == ESPHOME_F("/index.html");
#else
  return false;
#endif
}

#ifdef USE_NOQOPEN_PANEL
// Web app manifest for "Add to Home screen": the device's own name, standalone, the NOQopen icon.
static std::string manifest_json() {
  std::string name;
  StringRef src = App.get_friendly_name().empty() ? App.get_name() : App.get_friendly_name();
  for (size_t i = 0; i < src.size(); i++) {
    char c = src.c_str()[i];
    if (c == '"' || c == '\\')
      name += '\\';
    if (static_cast<unsigned char>(c) >= 0x20)
      name += c;
  }
  return "{\"name\":\"" + name + "\",\"short_name\":\"" + name +
         "\",\"start_url\":\"/\",\"scope\":\"/\",\"display\":\"standalone\","
         "\"background_color\":\"#f5f5f5\",\"theme_color\":\"#f5f5f5\","
         "\"icons\":[{\"src\":\"/icon.png\",\"sizes\":\"192x192\",\"type\":\"image/png\",\"purpose\":\"any\"}]}";
}
#endif

void NoqopenPortal::handleRequest(AsyncWebServerRequest *request) {
#ifdef USE_NOQOPEN_PANEL
#ifdef USE_ESP32
  char buf[AsyncWebServerRequest::URL_BUF_SIZE];
  StringRef url = request->url_to(buf);
#else
  const auto &url = request->url();
#endif
  if (url == ESPHOME_F("/icon.png")) {
#ifdef USE_ESP8266
    auto *icon = request->beginResponse_P(200, ESPHOME_F("image/png"), ICON_PNG, sizeof(ICON_PNG));
#else
    auto *icon = request->beginResponse(200, ESPHOME_F("image/png"), ICON_PNG, sizeof(ICON_PNG));
#endif
    icon->addHeader(ESPHOME_F("Cache-Control"), ESPHOME_F("max-age=604800"));
    request->send(icon);
    return;
  }
  if (url == ESPHOME_F("/manifest.webmanifest")) {
    std::string json = manifest_json();
    request->send(200, ESPHOME_F("application/manifest+json"), json.c_str());
    return;
  }
#endif
  const uint8_t *page = PAGE_GZ;
  size_t size = sizeof(PAGE_GZ);
#ifdef USE_NOQOPEN_PANEL
  if (!setup_open_()) {
    page = PANEL_GZ;
    size = sizeof(PANEL_GZ);
  }
#endif
#ifdef USE_ESP8266
  auto *response = request->beginResponse_P(200, ESPHOME_F("text/html"), page, size);
#else
  auto *response = request->beginResponse(200, ESPHOME_F("text/html"), page, size);
#endif
  response->addHeader(ESPHOME_F("Content-Encoding"), ESPHOME_F("gzip"));
  response->addHeader(ESPHOME_F("Cache-Control"), ESPHOME_F("no-store"));
  request->send(response);
}

}  // namespace esphome::noqopen_portal
