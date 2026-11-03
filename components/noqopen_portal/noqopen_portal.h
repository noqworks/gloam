#pragma once

#include "esphome/core/component.h"
#include "esphome/components/web_server_base/web_server_base.h"

namespace esphome::noqopen_portal {

// Registers ahead of the stock captive portal and the stock web server.
// Setup network open: answers every GET with the NOQopen setup page, except the two data endpoints the page itself
// calls (/config.json, /wifisave).
// Home network (USE_NOQOPEN_PANEL): answers GET / with the NOQopen control page; everything else (/events and the
// entity endpoints the page calls) stays with the stock web server.
class NoqopenPortal final : public AsyncWebHandler, public Component {
 public:
  explicit NoqopenPortal(web_server_base::WebServerBase *base) : base_(base) {}
  void setup() override;
  void dump_config() override;
  // Before WiFi, the captive portal and the web server, so this handler is first in line.
  float get_setup_priority() const override { return setup_priority::WIFI + 2.0f; }

  bool canHandle(AsyncWebServerRequest *request) const override;
  void handleRequest(AsyncWebServerRequest *request) override;

 protected:
  static bool setup_open_();
  web_server_base::WebServerBase *base_;
};

}  // namespace esphome::noqopen_portal
