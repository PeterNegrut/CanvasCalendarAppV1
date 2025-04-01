import RPi.GPIO as GPIO
import time


speedA = int(input("Input a speed value for motor A (0-100)"))
speedB = int(input("Input a speed value for motor B (0-100)"))

#for motor state, 1 is forward, 0 is backwards
motor_state = 1

#Pin Definitions
INA = 17
INB = 22
PWMA = 27
INC = 23
IND = 24
PWMB = 25

Rasberry_List = [INA, INB, PWMA, INC, IND, PWMB]

MotorApower = GPIO.PWM(PWMA, 1000)
MotorBpower = GPIO.PWM(PWMB, 1000)

MotorApower.start(0)
MotorBpower.start(0)

def StartMotors():
    global motor_state
    if motor_state == 1:
        return("motors are already forward")

    #Hbridge control for motor A
    GPIO.output(INA, GPIO.HIGH)
    GPIO.output(INB, GPIO.LOW)
    MotorApower.ChangeDutyCycle(speedA)

    #Hbridge control for motor B
    GPIO.output(INC, GPIO.HIGH)
    GPIO.output(IND, GPIO.LOW)
    MotorBpower.ChangeDutyCycle(speedB)

    motor_state = 1
    print("Motors are running forward")


def ReverseMotors():
    global motor_state
    if motor_state == 0:
        return("motors are already reversed")
    #Hbridge control for motor A
    GPIO.output(INA, GPIO.LOW)
    GPIO.output(INB, GPIO.HIGH)
    MotorApower.ChangeDutyCycle(speedA)

    #Hbridge control for motor B
    GPIO.output(INC, GPIO.LOW)
    GPIO.output(IND, GPIO.HIGH)
    MotorBpower.ChangeDutyCycle(speedB)

    motor_state = 0
    print("Motors reversing")

def checkStatus():
    global motor_state
    if motor_state == 1:
        print("Motors are running forward")
    else:
        print("Motors are reversing")


def StopMotors():

    MotorApower.ChangeDutyCycle(0)
    MotorBpower.ChangeDutyCYcle(0)
    for pin in Rasberry_List:
        GPIO.output(pin, GPIO.LOW)
    print("Motors stopped")


def Sensor():
    pass


def main():
    while True:
        command = input("Enter 'f' for forward, 'r' for reverse, 's' to stop, 'q' to quit: ").lower()
        if command == 'f':
            StartMotors()
        elif command == 'r':
            ReverseMotors()
        elif command == 's':
            StopMotors()
        elif command == 'q':
            print("Exiting program...")
            StopMotors()
            GPIO.cleanup()
            break

main()