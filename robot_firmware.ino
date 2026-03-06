#include <Servo.h>

Servo servoX;
Servo servoY;

// Pin Definitions
const int fsrPin = A0;    // Force Sensitive Resistor on analog pin 0
const int servoXPin = 9;  // Base rotation (X-axis)
const int servoYPin = 10; // Arm extension/elevation (Y-axis)

// Communications
String inputString = "";
bool stringComplete = false;

void setup() {
  Serial.begin(115200);
  inputString.reserve(64);

  servoX.attach(servoXPin);
  servoY.attach(servoYPin);

  // Initialize to safe medical default positions
  servoX.write(90);
  servoY.write(90);
}

void loop() {
  // 1. Process received surgical movement commands
  if (stringComplete) {
    parseCommand(inputString);
    inputString = "";
    stringComplete = false;
  }

  // 2. Read haptic feedback (Force Applied at Surgical Site)
  int fsrValue = analogRead(fsrPin);

  // 3. Send haptic data back to Surgeon Console
  // Format is easily parsed by Python: FSR:<value>
  Serial.print("FSR:");
  Serial.println(fsrValue);

  // Low latency 10ms loop
  delay(10);
}

void parseCommand(String cmd) {
  // Command format expected: "X:120,Y:45\n"
  int xIdx = cmd.indexOf("X:");
  int yIdx = cmd.indexOf("Y:");

  if (xIdx != -1 && yIdx != -1) {
    int commaIdx = cmd.indexOf(',', xIdx);

    String xStr = cmd.substring(xIdx + 2, commaIdx);
    String yStr = cmd.substring(yIdx + 2); // Assumes Y is trailing

    int xVal = xStr.toInt();
    int yVal = yStr.toInt();

    // Safety constraints to avoid mechanical boundaries
    xVal = constrain(xVal, 0, 180);
    yVal = constrain(yVal, 0, 180);

    servoX.write(xVal);
    servoY.write(yVal);
  }
}

// Interruption-driven Serial Read for lowest latency
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else if (inChar != '\r') {
      inputString += inChar;
    }
  }
}