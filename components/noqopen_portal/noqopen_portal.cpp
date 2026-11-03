#include "noqopen_portal.h"
#include "portal_page.h"
#ifdef USE_NOQOPEN_PANEL
#include "panel_page.h"
#endif

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
  if (setup_open_())
    return !(url == ESPHOME_F("/config.json") || url == ESPHOME_F("/wifisave"));
#ifdef USE_NOQOPEN_PANEL
  return url == ESPHOME_F("/") || url == ESPHOME_F("/index.html");
#else
  return false;
#endif
}

void NoqopenPortal::handleRequest(AsyncWebServerRequest *request) {
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
