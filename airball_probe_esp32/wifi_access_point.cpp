#include <esp_wifi.h>

#include "wifi_access_point.h"

#define WIFI_SSID "airball0011"
#define WIFI_PASS "relativewind"
#define WIFI_UDP_PORT 30123

#define STARTUP_DELAY_MS 1000

IPAddress local_ip(192, 168, 4, 10);
IPAddress gateway_ip(192, 168, 4, 254);
IPAddress subnet_ip_mask(255, 255, 255, 0);

WifiAccessPoint::WifiAccessPoint() {}

void WifiAccessPoint::begin() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(WIFI_SSID, WIFI_PASS);
  Serial.println(WiFi.softAPIP());
  WiFi.softAPConfig(local_ip, gateway_ip, subnet_ip_mask);
  Serial.println(WiFi.softAPIP());
  broadcast_ip = WiFi.broadcastIP();
  esp_wifi_set_ps(WIFI_PS_NONE);
}

void WifiAccessPoint::send(const char* sentence) {
  wifi_udp.beginPacket(broadcast_ip, WIFI_UDP_PORT);
  wifi_udp.write((const uint8_t*) sentence, strlen(sentence));
  wifi_udp.endPacket();
  wifi_udp.flush();
}
