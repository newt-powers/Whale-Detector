//sourced from https://arduinogetstarted.com/faq/how-to-control-speed-of-servo-motor

#include <Servo.h>

Servo myServo;

//unsigned long MOVING_TIME = 20000; //moving time is 20 seconds
//unsigned long moveStartTime;
//int startAngle = 1; // 0 degrees
//int stopAngle = 359; // 359 degrees (almost a full rotation)

const int SERVO_PIN = 9;
const int trigPin = 7;
const int echoPin = 10;

bool stopped = false;
int currentAngle = 90;

void setup() {
  Serial.begin(9600);
  myServo.attach(SERVO_PIN);
  myServo.write(currentAngle);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);


}

//how to keep looping the servo motor to be continuous???
void loop() {
  // unsigned long progress = millis() - moveStartTime;
  //check for commands from Python
  if(Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if(command == "STOP") {
      stopped = true;
      myServo.write(currentAngle);

      //Serial.println("SERVO STOPPED");
    }
    if(command == "START") {
      stopped = false;

      //Serial.println("SERVO STARTED");
    }
  }

  if(!stopped) {
    //move servo normally
    myServo.write(0);
    delay(1000);

    if (stopped) return;
    
    myServo.write(90);
    delay(1000);

    if (stopped) return;
  
    myServo.write(180);
    delay(1000);
  }

    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
  
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
  
    long duration = pulseIn(echoPin, HIGH);
    float distance = duration * 0.0343 / 2;
  
//    Serial.print("Distance: ");
    Serial.println(distance);
//    Serial.println(" cm");
  
}
