#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <MQUnifiedsensor.h>

// Konstan untuk WiFi credentials
const char *WIFI_SSID = "Redmi Note 12 Pro";
const char *WIFI_PASS = "66666666";

// API server address
const char *serverName = "http://192.168.75.25:3001/api/data"; // Ganti <alamat_ip_komputer> dengan alamat IP lokal komputer Anda

// Pin assignments
int sensor_input = 34;
#define DHTPIN 4  // DHT22 sensor pin
#define DHTTYPE DHT11  // DHT sensor type
const int ledPin = 32;  // LED pin

// Global objects
DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2); // Sesuaikan dengan alamat I2C LCD Anda

#define Board "ESP-32"
#define Voltage_Resolution 3.3
#define ADC_Bit_Resolution 12
#define RatioMQ135CleanAir 3.6 // berdasarkan data sheet MQ-135

MQUnifiedsensor MQ135(Board, Voltage_Resolution, ADC_Bit_Resolution, sensor_input, "MQ-135");

// Fungsi untuk mendapatkan data suhu
float get_temperature_data() {
  float t = dht.readTemperature();
  if (isnan(t)) {
    Serial.println(F("Error reading temperature!"));
    return 0.0;  // Return default value on error
  } else {
    Serial.print(F("Temperature: "));
    Serial.print(t);
    Serial.println(F("°C"));
    return t;
  }
}

// Fungsi untuk mendapatkan data kelembaban
float get_humidity_data() {
  float h = dht.readHumidity();
  if (isnan(h)) {
    Serial.println(F("Error reading humidity!"));
    return 0.0;  // Return default value on error
  } else {
    Serial.print(F("Humidity: "));
    Serial.print(h);
    Serial.println(F("%"));
    return h;
  }
}

// Fungsi untuk membaca data dari sensor MQ-135
float get_CO_data() {
  MQ135.setRegressionMethod(1); // Set regression method untuk CO
  MQ135.setA(605.18); MQ135.setB(-3.937); // Rumus dari datasheet MQ-135 untuk CO
  MQ135.update(); // membaca sensor MQ-135
  return MQ135.readSensor(); // membaca konsentrasi CO
}

float get_CO2_data() {
  MQ135.setRegressionMethod(1); // Set regression method untuk CO2
  MQ135.setA(110.47); MQ135.setB(-2.862); // Rumus dari datasheet MQ-135 untuk CO2
  MQ135.update(); // membaca sensor MQ-135
  return MQ135.readSensor(); // membaca konsentrasi CO2
}


void send_data_to_server(float temperature, float humidity, float air_quality, float CO, float CO2) {
  if (WiFi.status() == WL_CONNECTED) { 
    HTTPClient http;

    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{\"temperature\":" + String(temperature) + 
                      ",\"humidity\":" + String(humidity) + 
                      ",\"air_quality\":" + String(air_quality) +
                      ",\"CO\":" + String(CO) + // Pastikan ini ada
                      ",\"CO2\":" + String(CO2) + "}"; // Pastikan ini ada

    int httpResponseCode = http.POST(jsonData);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("Error in WiFi connection");
  }
}


// Fungsi untuk mengontrol lampu berdasarkan kondisi lingkungan
void control_lamp(float temperature, float humidity, float CO, float CO2) {
  bool is_hot = temperature > 32.0; // Kondisi suhu terlalu panas
  bool is_dry = humidity < 32.0; // Kondisi kelembapan terlalu kering
  bool is_wet = humidity > 80; // Kondisi kelembapan terlalu lembap
  bool is_high_CO = CO > 50; // Kondisi CO lebih dari 50 ppm
  bool is_high_CO2 = CO2 > 1000; // Kondisi CO2 lebih dari 1000 ppm

  if (is_hot || is_dry || is_wet || is_high_CO || is_high_CO2) {
    digitalWrite(ledPin, HIGH); // Nyalakan lampu
  } else {
    digitalWrite(ledPin, LOW); // Matikan lampu
  }
}


// Fungsi untuk menampilkan kualitas udara pada LCD berdasarkan CO dan CO2
void display_status(float temperature, float humidity, float CO, float CO2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("CO: ");
  lcd.print(CO);
  lcd.print(" ppm");
   
  lcd.setCursor(0, 1);
  lcd.print("CO2: ");
  lcd.print(CO2);
  lcd.print(" ppm");
  
  delay(2000); // Tampilkan nilai CO dan CO2 selama 2 detik

  lcd.clear();
  lcd.setCursor(0, 0);
  if (CO <= 9) {
    lcd.print("CO: Normal");
  } else if (CO <= 35) {
    lcd.print("CO: Warning");
  } else if (CO <= 200) {
    lcd.print("CO: Danger");
  } else {
    lcd.print("CO: Critical");
  }

  lcd.setCursor(0, 1);
  if (CO2 <= 600) {
    lcd.print("CO2: Normal");
  } else if (CO2 <= 1000) {
    lcd.print("CO2: Warning");
  } else if (CO2 <= 2000) {
    lcd.print("CO2: Danger");
  } else {
    lcd.print("CO2: Critical");
  }
  
  delay(2000); // Tampilkan status CO dan CO2 selama 2 detik

  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Suhu: ");
  lcd.print(temperature);
  
  lcd.setCursor(0, 1);
  lcd.print("Humid: ");
  lcd.print(humidity);
  
  delay(2000);


   lcd.clear();
  lcd.setCursor(0, 0);
  if (temperature <= 32) {
    lcd.print("Suhu: Normal");
  } else if (temperature <= 35) {
    lcd.print("Suhu: Warning");
  } else if (temperature <= 40) {
    lcd.print("Suhu: Danger");
  } else {
    lcd.print("Suhu: Critical");
  }

  lcd.setCursor(0, 1);
  if (humidity >= 30 && humidity <= 65) {
    lcd.print("Humid: Normal");
  } else if (humidity < 30) {
    lcd.print("Humid: Warning");
  } else if (humidity <= 80) {
    lcd.print("Humid: Danger");
  } else {
    lcd.print("Humid: Critical");
  }

  delay(1000); // Tampilkan status suhu dan kelembapan selama 2 detik
}


// Fungsi untuk menampilkan data CO dan CO2 pada Serial Monitor
void display_serial(float CO, float CO2) {
  Serial.print("CO Concentration: ");
  Serial.print(CO);
  Serial.println(" ppm");

  Serial.print("CO2 Concentration: ");
  Serial.print(CO2);
  Serial.println(" ppm");
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  
  dht.begin();
  lcd.init(); // Ganti dengan lcd.begin() untuk beberapa library
  lcd.backlight();
  pinMode(ledPin, OUTPUT); // Set LED pin as output
  
  MQ135.setRegressionMethod(1); // Set method 1 untuk regresi linear
  MQ135.init();

  Serial.print("Calibrating...\n");
  float calcR0 = 0;
  for(int i = 1; i <= 10; i++) {
    MQ135.update(); // membaca sensor MQ-135
    calcR0 += MQ135.calibrate(RatioMQ135CleanAir);
    Serial.print(".");
  }
  MQ135.setR0(calcR0 / 10);
  Serial.println(" Calibration is done!\n");

  if (isinf(calcR0)) {
    Serial.println("Warning: Connection issue detected, R0 is infinite (Open circuit detected) please check your wiring and supply");
    while (1);
  }
  if (calcR0 == 0) {
    Serial.println("Warning: Connection issue detected, R0 is zero (Analog pin with short circuit to ground) please check your wiring and supply");
    while (1);
  }

  Serial.print("R0: ");
  Serial.print(MQ135.getR0());
  Serial.println(" kohm");
}

void loop() {
  delay(20000);
  float temperature = get_temperature_data();
  float humidity = get_humidity_data();
  float CO = get_CO_data();
  float CO2 = get_CO2_data();
  float air_quality = (CO + CO2) / 2; // Menggabungkan data CO dan CO2 sebagai kualitas udara

  send_data_to_server(temperature, humidity, air_quality, CO, CO2);
  control_lamp(temperature, humidity, CO, CO2);
  display_status(temperature, humidity, CO, CO2); // Memanggil fungsi baru
  display_serial(CO, CO2);
}


