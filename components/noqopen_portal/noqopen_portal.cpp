#include "noqopen_portal.h"
#include "portal_page.h"

#include "esphome/core/log.h"
#include "esphome/components/captive_portal/captive_portal.h"

namespace esphome::noqopen_portal {

static const char *const TAG = "noqopen_portal";

void NoqopenPortal::setup() { this->base_->add_handler_without_auth(this); }

void NoqopenPortal::dump_config() {
  ESP_LOGCONFIG(TAG, "NOQopen setup page: %u bytes", static_cast<unsigned>(sizeof(PAGE_GZ)));
}

bool NoqopenPortal::canHandle(AsyncWebServerRequest *request) const {
  auto *portal = captive_portal::global_captive_portal;
  if (portal == nullptr || !portal->is_active() || request->method() != HTTP_GET)
    return false;
#ifdef USE_ESP32
  char buf[AsyncWebServerRequest::URL_BUF_SIZE];
  StringRef url = request->url_to(buf);
#else
  const auto &url = request->url();
#endif
  return !(url == ESPHOME_F("/config.json") || url == ESPHOME_F("/wifisave"));
}

void NoqopenPortal::handleRequest(AsyncWebServerRequest *request) {
#ifdef USE_ESP8266
  auto *response = request->beginResponse_P(200, ESPHOME_F("text/html"), PAGE_GZ, sizeof(PAGE_GZ));
#else
  auto *response = request->beginResponse(200, ESPHOME_F("text/html"), PAGE_GZ, sizeof(PAGE_GZ));
#endif
  response->addHeader(ESPHOME_F("Content-Encoding"), ESPHOME_F("gzip"));
  response->addHeader(ESPHOME_F("Cache-Control"), ESPHOME_F("no-store"));
  request->send(response);
}

}  // namespace esphome::noqopen_portal
