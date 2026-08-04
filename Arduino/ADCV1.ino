#include <Wire.h>
uint8_t byte1, byte2;
uint16_t byte0;
uint16_t byte_r;
double data2vol_t;
double vol_t;
double vol;
int sensorValue;
double sensorVol;
double resist;

void setup() {
  Wire.begin();  
  Serial.begin(115200);
  writei2c(0b1001000, 0b01010000, 0b11100011);
  delay(1);
  data2vol_t = ( (pow(2,15)-1) / pow(2,15) * 6.144 ) / 32767;
  delay(10);
}

void loop() {
  writei2c(0b1001000, 0b01010000, 0b11100011);
  delayMicroseconds(10);
  byte_r = readi2c(0b1001000);
  delayMicroseconds(10);
  sensorVol = data2vol(byte_r);
  resist = sensorVol/(5.0-sensorVol) * 33000; // Reference resistance
  
  Serial.print(sensorVol);
  Serial.print(", ");
  Serial.println(resist); 
  delay(10);
}

void writei2c(uint8_t address, uint8_t byte_m, uint8_t byte_l){
  Wire.beginTransmission(address);
  Wire.write(0b00000001);
  Wire.write(byte_m);
  Wire.write(byte_l);
  Wire.endTransmission();
}

uint16_t readi2c(uint8_t address){
  Wire.beginTransmission(address);
  Wire.write(0b00000000);
  Wire.endTransmission();
  Wire.requestFrom(address,2);
  byte1 = Wire.read();
  byte2 = Wire.read();
  byte0 = byte1<<8 | byte2;
  return byte0;
}

double data2vol(uint16_t byte_){
  if (byte_ >= 32768) {
    byte_ = ~byte_ + 1;
    vol_t = - data2vol_t * double(byte_);
  }
  else {
    vol_t = data2vol_t * double(byte_);
  }
  return vol_t;
}
