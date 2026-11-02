#pragma once

#include "esphome/core/component.h"
#include "esphome/components/web_server_base/web_server_base.h"

namespace esphome::noqopen_portal {

// Registers ahead of the stock captive portal and answers every GET it would answer with the
// NOQopen page, except the two data endpoints the page itself calls (/config.json, /wifisave).
class NoqopenPortal final : public AsyncWebHandler, public Component {
 public:
  explicit NoqopenPortal(web_server_base::WebServerBase *base) : base_(base) {}
  void setup() override;
  void dump_config() override;
  // Before WiFi and before the captive portal, so this handler is first in line.
  float get_setup_priority() const override { return setup_priority::WIFI + 2.0f; }

  bool canHandle(AsyncWebServerRequest *request) const override;
  void handleRequest(AsyncWebServerRequest *request) override;

 protected:
  web_server_base::WebServerBase *base_;
};

}  // namespace esphome::noqopen_portal
