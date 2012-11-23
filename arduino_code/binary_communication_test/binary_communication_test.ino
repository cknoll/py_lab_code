/*
Test binary communication
 */


// bytewise interface to 4-byte variables

// convert float <-> 4 bytes for serial communication
union u_floatbytes {
  byte b[4];
  float fval;
} 
floatbytes;

union u_ulongbytes {
  byte b[4];
  unsigned long ulval;
} 
ulongbytes;


// global variables needed for timing

unsigned long const stepsize = 10000; // 10 ms
unsigned long mi = 0;
unsigned long nextStep = stepsize;


// ###############################################################

void setup() {
  
  Serial.begin(115200);
}

// ###############################################################

void loop() {

  // This loop is run once every 10 milli seconds
  
  // Send some data

  
  Serial.print("AA");

  send_float(1.1);
  send_float(2.2);
  send_float(3.3);
  send_float(54.321);  
  send_float(0.12345678);
  send_float(0.0);
  send_int(721);
  send_long(mi); // time passed since controller started
  send_long((stepsize<<1) - nextStep + mi); // computation time

 
  
  mi = micros();
  
  // wait until the next step
  delayMicroseconds(nextStep-mi);
  // !! hint: if waiting time > 16000us then waitMicroseconds is not exact anymore
  nextStep += stepsize;
  
}


void send_float(float f)
{
  floatbytes.fval = f;
  Serial.write(floatbytes.b[0]);
  Serial.write(floatbytes.b[1]);
  Serial.write(floatbytes.b[2]);
  Serial.write(floatbytes.b[3]);
}

void send_int(int i)
{
  Serial.write(i & 0xFF);
  Serial.write(i >>8); 
}

void send_long(unsigned long l)
{
  Serial.write(l & 0xFF);
  Serial.write(l >>8);
  Serial.write(l >>16);
  Serial.write(l >>24);
}

