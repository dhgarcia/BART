import time
import threading

# import naoqi
# from naoqi import *
from naoqi import ALBroker
from naoqi import ALModule
from naoqi import ALProxy
import motion

class naoqiController(ALModule):

    def __init__(self, name, ip="127.0.0.1", port=9559):
        self.broker = ALBroker("naoqiController", "0.0.0.0", 0, ip, port)
        ALModule.__init__(self, name)

        self.tts = ALProxy("ALTextToSpeech", ip, port) # initialize speech
        self.motionProxy = ALProxy("ALMotion", ip, port) # help make the robot move
        self.animatedSpeechProxy = ALProxy("ALAnimatedSpeech", ip, port) # initialize the body language
        self.tracker = ALProxy("ALTracker", ip, port)   # initialize the track of different targets
        self.autonomousLife = ALProxy("ALAutonomousLife", ip, port) # initialize autonomous life
        autoState = self.autonomousLife.getState() # to know the state of autonomous life
        if autoState != "disabled": # disabled the autonomous life
            self.autonomousLife.setState("disabled")
        self.motionProxy.wakeUp()    # turn on robot's motors
        self.motionProxy.setBreathConfig([["Bpm", 6], ["Amplitude", 0.9]]) # configuration of the breathing
        self.motionProxy.setBreathEnabled("Body", True) # turn on the breathing
        self.motionProxy.setStiffnesses('Head', 1.0) # define the stiffness of the robot's head
        targetName = "Face" # trace humans faces
        faceWidth = 0.1
        self.tracker.registerTarget(targetName, faceWidth)   # register predefined target
        self.tracker.track(targetName)  # start traking process
        self.tts.setVolume(0.8) # adjust the sound
        self.configuration = {"bodyLanguageMode":"contextual"} # start the autonomous life

        self.run = True

        # global memory
        # memory = ALProxy("ALMemory", ip, port)

    def say(self,sentence):
       # self.stopTracker()
        threading.Thread(target = self.animatedSpeechProxy.say, args=(sentence,self.configuration)).start() # define fonctions to execute and start the tread
        self.tracker.track("Face")   # activate the human face track
        self.run = True
     #   self.animatedSpeechProxy.say(sentence,self.configuration)

    def setVolume(self, value): # change the volume of Nao robot
        self.tts.setVolume( value )

    def stopTracker(self):
        self.run = False
        self.tracker.stopTracker() # stop to track human face


    def track(self):
        while self.run:
            time.sleep(1)
            try:
                if self.tracker.isTargetLost():
                    self.tracker.toggleSearch(True) # search a new target
                else:
                    self.tracker.toggleSearch(False) # stop the search of the target
            except RuntimeError :
                print("Naoqi RuntimeError")


    def armMovement(self):
        JointNames = ["RShoulderPitch", "RShoulderRoll","LShoulderPitch", "LShoulderRoll"] # initialisation for right arm and left arm
        Arm1 = [60, -20, 60, 20]  # position of right and left arms
        Arm1 = [ x * motion.TO_RAD for x in Arm1]
        pFractionMaxSpeed = 0.5 # speed of movement
        self.motionProxy.angleInterpolationWithSpeed(JointNames, Arm1, pFractionMaxSpeed) # movement
        Arm1 = [80, 5, 80, 5]
        Arm1 = [ x * motion.TO_RAD for x in Arm1]
        pFractionMaxSpeed = 0.3
        self.motionProxy.angleInterpolationWithSpeed(JointNames, Arm1, pFractionMaxSpeed)