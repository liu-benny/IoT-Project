#include <ESP8266WiFi.h>
#include <PubSubClient.h>


//changed to class wifi
const char* ssid = "TP-Link_2AD8";
const char* password = "14730078";
const char* mqtt_server = "192.168.0.153";

const int pResistor = A0;

WiFiClient vanieriot;
PubSubClient client(vanieriot);

void setup_wifi() {
  delay(10);
  
  //connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.print("WiFi connected - ESP-8266 IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messagein;

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messagein += (char)message[i];
  }
}

void reconnect() {
  while (!client.connected()) {
      Serial.print("Attempting MQTT connection...");
      if (client.connect("vanieriot")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 3 seconds");
      // Wait 3 seconds before retrying
      delay(3000);
    }
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  // setup photoresistor
  pinMode(pResistor,INPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
  if (!client.connected()) {
      reconnect();
    }
   
  if(!client.loop())
    client.connect("vanieriot");

  //check temperature and turn into string
//  String temp = String(dht.getTemperature(), 1) + "Â°C";
//  Serial.println(temp);
  int intens = analogRead(pResistor);
  String intensity = String(intens) + "";

  
  client.publish("Smarthome/ESP/light", intensity.c_str());
  
  //wait 5 seconds
  delay(5000);
}
