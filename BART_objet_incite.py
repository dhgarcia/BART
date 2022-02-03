# "C:\Program Files (x86)\Python27\python" C:\Users\erohart\Desktop\BART\BART_objet_incite.py
from __future__ import division
import kivy                                                 # import from the kivy part
from random import randint
from kivy.app import *
from kivy.lang import *
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.core.window import WindowBase
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from functools import partial
import naoqi, sys, argparse,almath             # imports from the nao part
import motion
from naoqi import *
from optparse import OptionParser
import time, threading, thread
import os,inspect
from os.path import exists

absol = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))+"/data.txt"
f = open(absol,'r') # open the file where the IP adress of te robot is stock.
IP = f.readline() #IP adress of the robot
f.close()
PORT = 9559            # port to connect the robot
path = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))+"/results/results_"
# path where files will stocks

class RobotControllerModule(ALModule):
    def __init__(self, name):
        ALModule.__init__(self, name)
        self.tts = ALProxy("ALTextToSpeech") # initialize speech
        self.motionProxy = ALProxy("ALMotion") # help make the robot move
        self.animatedSpeechProxy = ALProxy("ALAnimatedSpeech") # initialize the body language
        self.tracker = ALProxy("ALTracker")   # initialize the track of different targets 
        self.autonomousLife = ALProxy("ALAutonomousLife") # initialize autonomous life
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
      #  self.run = True                             

        global memory
        memory = ALProxy("ALMemory")

    def track(self):
        while self.run:
            time.sleep(1)
            if self.tracker.isTargetLost():
                self.tracker.toggleSearch(True) # search a new target
            else:
                self.tracker.toggleSearch(False) # stop the search of the target

    def setVolume(self, value): # change the volume of Nao robot
        self.tts.setVolume( value )

    def say(self,sentence):
       # self.stopTracker()   
        threading.Thread(target = self.animatedSpeechProxy.say, args=(sentence,self.configuration)).start() # define fonctions to execute and start the tread
        self.tracker.track("Face")   # activate the human face track
        self.run = True           
     #   self.animatedSpeechProxy.say(sentence,self.configuration)

    def stopTracker(self):
        self.run = False
        self.tracker.stop() # stop to track human face


class BART_TestApp(App):

    def build(self):
        self.tts = ALProxy("ALTextToSpeech") # initialize the robot's peech
        self.motionProxy = ALProxy("ALMotion") # help make the robot move
        self.tabms = []    # table of ms between two click             
        self.tabal = [0]   # table of numbers of values in tabms for one balloon
        self.deb = time.time()
        self.sound_boom = SoundLoader.load('sounds/sound_boom.ogg')   # sounds for the game
        self.sound_pump = SoundLoader.load('sounds/sound_pump.ogg')
        self.sound_money = SoundLoader.load('sounds/sound_money.ogg')
        self.b = 0  # if the robot speaks
        self.s = 0  # numbers of robot intervention by balloon
        self.p = 0.00  # payment for the participant
        self.nb_pump = 0 # number of pumping
        self.nb_bal = 0 # number of used balloon
        self.t = 3 # time between two nao's sentences
        self.maxi = randint(9,127) # random fonction for the maximum pumping of the first balloon
        self.z = [0,0,0,0,0,0] # choose nao's interventions with a random function
        for i in range(0,6):
            self.z[i] = randint(1,29)
            j = 0
            while (j<i): # for all value completes on the table
                if (self.z[j] == self.z[i]) : # if two values are identical, change the last value
                    self.z[i] = randint(1,29) # choose a new balloon
                    j = 0 # comback at the first value of the table
                else :
                    j+=1
        self.files = open(self.ID,"a") # open the text file
        # write the text in the file
        self.files.write("balloon number,robot intervention [0/1],number of verbal interventions,number of pumps, explosion point, explosion [0:no/1:yes], payment \n")
        game = FloatLayout(padding=10, orientation = 'vertical')
        
        self.rules = Button(text="rules",size_hint=(None,None),size=(150,75),pos_hint={'center_x':0.1,'center_y':0.9})
        self.rules.bind(on_press=self.open_rules)
        game.add_widget(self.rules) # rules button
        
        self.quit = Button(text = 'quit',size_hint=(None,None),size=(150,75),pos_hint={'center_x':0.9,'center_y':0.9})
        self.quit.bind(on_press=self.quits)
        game.add_widget(self.quit) # quit button
        
        self.titles = Label(text = 'Blow up the balloon',size_hint=(None,None),size=(150,75),pos_hint={'center_x':0.5,'center_y':0.75},font_size='20sp')
        game.add_widget(self.titles) # title of the game
        
        self.blow = Button(text='pump balloon',size_hint=(None,None),size=(150,100),pos_hint={'center_x':0.35,'center_y':0.2})
        self.blow.bind(on_press=self.blow_up)
        game.add_widget(self.blow) # 'pump balloon' button

        self.reward = Button(text='collect reward',size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.75,'center_y':0.2})
        self.reward.bind(on_press=self.change_value)
        game.add_widget(self.reward) # button to colect the money

        self.im_pump = Image(source='images/pump.gif',size_hint=(None,None),size=(50,50),pos_hint={'center_x':0.15,'center_y':0.2})
        game.add_widget(self.im_pump) # the pump image

        self.pump = Label(text='0',font_size='20dp',pos_hint={'center_x':0.22,'center_y':0.2})
        game.add_widget(self.pump) # print the number of pump for one balloon

        self.im_bal = Image(source="images/deflated_balloon.jpg",size_hint_x=0.2,size_hint_y=0.2,pos_hint={'center_x':0.35,'center_y':0.55})
        game.add_widget(self.im_bal) # balloon deflated / inflated

        self.im_boom = Image(source = "images/boom-cloud.png",size_hint_x = 1,size_hint_y = 1, pos_hint={'center_x':0.35,'center_y':0.5})
        game.add_widget(self.im_boom) # image of explosion
        self.im_boom.opacity = 0  # the explosion image become invisible

        self.bar = ProgressBar(value=0,max=30,size_hint=(None,None),size=(200,400),pos_hint={'center_x':0.75,'center_y':0.3})
        game.add_widget(self.bar) # bar of avencment

        self.im_balloon = Image(source="images/balloon.jpg",size_hint=(None,None),size=(70,70),pos_hint={'center_x':0.93,'center_y':0.25})
        game.add_widget(self.im_balloon) # image of the small balloon

        self.balloon = Label(text='0',font_size='20dp',pos_hint={'center_x':0.93,'center_y':0.25})
        game.add_widget(self.balloon) # text on the small balloon

        self.safe = Image(source="images/empty.jpg",size_hint=(None,None),size=(100,100),pos_hint={'center_x':0.75,'center_y':0.5})
        game.add_widget(self.safe) # money and safe image

        self.pig = Image(source="images/wallet.jpg",size_hint=(None,None),size=(90,90),pos_hint={'center_x':0.93,'center_y':0.5})
        game.add_widget(self.pig) # pig wallet image

        self.money = Label(text='0.00', font_size='20dp',pos_hint={'center_x':0.94,'center_y':0.4})
        game.add_widget(self.money) # money win by the participant

        self.livre = Image(source="images/livre.jpg",size_hint=(None,None),size=(20,20),pos_hint={'center_x':0.9,'center_y':0.4})
        game.add_widget(self.livre) # the pound symbol
        return game

    def speak(self,sentence): # nao speech with no blockage of the rest of the application
        tts = ALProxy("ALTextToSpeech",IP,PORT) # intializations
        animated = ALProxy("ALAnimatedSpeech",IP,PORT)
        config = {"bodyLanguageMode":"contextual"}
        threading.Thread(target = animated.say,args=(sentence,config)).start() # nao's speech

    def change_value(self,btn):  # fonction called by the 'collect reward' button
        if (self.reward.opacity != 0):
            self.sound_money.play() # play the money sound
            r = 0
            if (self.nb_bal>=29): # if  30 balloons have been used
                self.bar.value+=self.nb_pump/self.maxi  # change the bar value
                self.speak("this is the end of the game \\pau=500\\ Thank you !")
                finalvalue = (self.bar.value*100)/30
                self.p = self.p+(0.01*self.nb_pump) # money earn by participant
                if (len(str(self.p)) <4):
                    self.money.text = str(self.p)+'0'
                else:
                    self.money.text = str(self.p)
                texts = 'you have finished this experience !! \n Thank you for your time \n your score is : '+str("%.2f" % finalvalue) +'% \n You earn '+str(self.p)+' pounds'
                self.box4 = FloatLayout(orientation='vertical')
                self.box4.add_widget(Label(text=texts,size_font='20sp',size_hint=(None,None),size=(100,70),pos_hint={'center_x':0.5,'center_y':0.75}))
                self.box4.add_widget(Button(text='close the BART test',size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.5,'center_y':0.25},on_press=self.close))
                popup = Popup(title='END',title_align ='center',title_size = '30sp', content=self.box4,size_hint = (0.7,0.7),auto_dismiss=False)
                popup.open() # open the end's window
                Clock.schedule_once(partial(self.sit),3)
                self.files.write("%d , %d , %d , %d , %d , 0 , %.2f \n" % (self.nb_bal+1,self.b,self.s,self.nb_pump,self.maxi,self.p))
                self.files.write("score : %.2f \n" % finalvalue)
                deb2 = time.time()      # take the time
                self.deb = (deb2 - self.deb)*1000  # pass in millisecond
                self.tabms += [int(self.deb)]      
                self.deb = deb2
                l = len(self.tabms)     
                self.tabal += [l]      
                i = 0
                self.files.write("\nballoon, t1 [ms], t2, ... until balloon pops or collect \n")
                while (i<len(self.tabal)-1):       # write all values ( in ms ) on the file 
                    self.files.write(str(self.tabms[self.tabal[i]:self.tabal[i+1]])+"\n")   
                    i+=1
                self.files.close() # close the text file
                tps2 = time.time()
                timer = round(tps2-self.tps1,2)
                with open(self.ID, "r+") as file: # complete the file
                    text = file.read()
                    i = text.index("XXXX") # end time
                    j = text.index("ZZZZ") # time pass on the game
                    k = text.index("PP.PP") # money win by the participant
                    file.seek(0) # comme back at the start of the file
                    file.write(text[:i] + str(time.strftime('%H:%M',time.localtime())) + text[i + 4: j] + str(timer) + text[j+ 5:k] + str(self.p)+text[k + 5: ])
            else : # if it's not the end of the game
                if (self.b == 0): # if nao hasn't speak
                    for i in range(0,6):
                        if (self.z[i] == self.nb_bal) : # if it is the moment for nao to becoming demanding
                            deb2 = time.time()      
                            self.deb = (deb2 - self.deb)*1000   
                            self.tabms += [int(self.deb)]   
                            self.deb = deb2
                            self.speak("Are you sure ? Why no try one more ?")
                            self.delivery = time.time() # note the first nao's intervention for this balloon
                            self.t = 3
                            self.b = 1
                            self.s = 1 
                            r = 1
                            if ((self.maxi<self.nb_pump+10) and ((self.nb_pump+10)<127)) : # posibility to increase the maximum value of number of pump
                                self.maxi = self.nb_pump+10
                            elif ((self.maxi<self.nb_pump+10) and ((self.nb_pump+10)>=127)) :
                                self.maxi = 127                   
                            break
                if (r == 0) : # if nao doesn't ask to continue
                    self.bar.value+=self.nb_pump/self.maxi  # change the bar value
                    self.im_bal.source = "images/deflated_balloon.jpg"
                    if (self.nb_pump<50): # if the participant stop before 50 pumps
                        alea = randint(1,13)
                        if (alea == 1):
                            self.speak("thank you but I wanted a big balloon ...")
                        elif (alea == 2):
                            self.speak("It's a baby balloon")
                        elif (alea == 3):
                            self.speak("why is it to small ?")
                        elif (alea == 4):
                            self.speak("it's not a real ballon")
                        elif (alea == 5):
                            self.speak("It's already the end ?")
                        elif (alea == 6):
                            self.speak(" can you do a bigest balloon for the next round ?")
                        elif (alea == 7):
                            self.speak("you haven't take lot of risk")
                        elif (alea == 8):
                            self.speak("you had all your time")
                        elif (alea == 9):
                            self.speak("Why have you stop to pump ?")
                        elif (alea == 10):
                            self.speak("you had not to cease now")
                        elif (alea == 11):
                            self.speak("you shouldn't doubt, you had the time")
                        elif (alea == 12):
                            self.speak("It will be more funny if you pumped more")
                        elif (alea == 13):
                            self.speak("You have been able to do a better score")
                    else : # if the participant has done more than 50 pump
                        alea = randint(1,13)
                        if (alea == 1):
                            self.speak("it's a beautiful balloon")
                        elif (alea == 2):
                            self.speak("I like it")
                        elif (alea == 3):
                            self.speak("good")
                        elif (alea == 4):
                            self.speak("thank you for this big balloon")
                        elif (alea == 5):
                            self.speak("you've earned"+str(self.p)+"pounds, good job")
                        elif (alea == 6):
                            self.speak("this balloon have respectable size")
                        elif (alea == 7):
                            self.speak("well done")
                        elif (alea == 8):
                            self.speak("amazing")
                        elif (alea == 9):
                            self.speak("I realy like this balloon")
                        elif (alea == 10):
                            self.speak("superb balloon")
                        elif (alea == 11):
                            self.speak("felicitation")
                        elif (alea == 12):
                            self.speak("great")
                        elif (alea == 13):
                            self.speak("good job")
                    deb2 = time.time()      
                    self.deb = (deb2 - self.deb)*1000 # pass to second in milisecond  
                    self.tabms += [int(self.deb)]     # add the value in the tab
                    self.deb = deb2
                    l = len(self.tabms)  
                    self.tabal += [l]
                    self.p = self.p+(0.01*self.nb_pump)  #  reward for the player
                    self.reward.opacity = 0 # the reward button become invisible
                    if (len(str(self.p)) <4):
                        self.money.text = str(self.p)+'0'
                    else:
                        self.money.text = str(self.p)
                    self.files.write("%d , %d , %d , %d , %d , 0 , %.2f \n" % (self.nb_bal+1,self.b,self.s,self.nb_pump,self.maxi,self.p))
                    self.nb_bal +=1
                    self.maxi = randint(1,127)
                    if (self.bar.value<0.3):       # change the picture in accordance with the value of the bar
                        self.safe.source = "images/safe_1.jpg" 
                    elif (self.bar.value<1.5):
                        self.safe.source = "images/safe_5.jpg"
                    elif (self.bar.value<15):
                        self.safe.source = "images/safe_25.jpg"
                    elif (self.bar.value<22.5) :
                        self.safe.source = "images/safe_75.jpg"
                    elif (self.bar.value<28.5) :
                        self.safe.source = "images/safe_90.jpg"
                    elif (self.bar.value<=30) :
                        self.safe.source = "images/safe_100.jpg"
                    self.im_bal.size_hint_y = 0.18 # update value of the game
                    self.im_bal.size_hint_x = 0.18
                    self.nb_pump = 0 
                    self.balloon.text=str(self.nb_bal)
                    self.pump.text = str(self.nb_pump)
                    self.b = 0
                    self.s = 0
                else :
                    r = 0

    def talk(self,v): # Nao movements and talking after an explosion
        JointNames = ["RShoulderPitch", "RShoulderRoll","LShoulderPitch", "LShoulderRoll"] # initialisation for right arm and left arm
        Arm1 = [60,  -20, 60, 20]  # position of right and left arms
        Arm1 = [ x * motion.TO_RAD for x in Arm1]
        pFractionMaxSpeed = 0.5 # speed of movement
        self.motionProxy.angleInterpolationWithSpeed(JointNames, Arm1, pFractionMaxSpeed) # movement
        self.speak("ho !")
        Arm1 = [80,  5, 80,5]  
        Arm1 = [ x * motion.TO_RAD for x in Arm1]
        pFractionMaxSpeed = 0.3
        self.motionProxy.angleInterpolationWithSpeed(JointNames, Arm1, pFractionMaxSpeed)
        alea = randint(1,11) # random integer between 1 and 12
        if (self.nb_bal > 29): # it's the end of the game
            self.speak("It doesn't matter \\pau=750\\this is the end of the game \\pau=500\\ Thank you !")
        elif (alea == 1): 
            self.speak("oups !")
        elif (alea == 2):
            self.speak("I did't think it will explose")
        elif (alea == 3):
            self.speak("It was't planned")
        elif (alea == 4):
            self.speak("oups, sorry")
        elif (alea == 5):
            self.speak("It wasn't to resistant")
        elif (alea == 6 ):
            self.speak("we will do better with the next balloon")
        elif (alea == 7):
             self.speak("It dosen't matter")
        elif (alea == 8):
            self.speak("no problem, we have other balloons")
        elif (alea == 9):
            self.speak("Don't worry !")
        elif (alea == 10):
            self.speak("It wasn't a good balloon")
        elif (alea == 11):
            self.speak("try with another balloon")

    def blow_up(self,btn) :   # fonction called by the 'blow up' button
        y = self.im_bal.size_hint_y # take the dimention of the balloon image
        x = self.im_bal.size_hint_x
        k = 0 # initialize k
        if (self.blow.text == "new balloon"): # if the balloon just come to explose
            self.im_bal.source = "images/deflated_balloon.jpg"
            self.im_bal.opacity = 1 # the balloon become visible
            self.im_boom.opacity = 0 # the explosion become invisible
            self.reward.opacity = 1 # the reward button become visible
            self.blow.text = "pump balloon" # change the text of the button
        else:
            if (self.nb_pump >= self.maxi): # if the balloon must explode
                self.files.write("%d , %d , %d , %d , %d , 1 , %.2f \n" % (self.nb_bal+1,self.b,self.s,self.nb_pump,self.maxi,self.p))
                self.im_bal.opacity = 0 # the balloon become invisible
                self.im_boom.opacity = 1 # the explosion become visible
                self.reward.opacity = 0 # the reward button become invisible
                self.blow.text = "new balloon"
                y = 0.18 # resize the balloon image
                x = 0.18
                self.nb_pump = 0
                self.nb_bal+=1
                self.sound_boom.play() # a boom sound
                Clock.schedule_once(partial(self.talk), 0)
                k = 1
            if ((self.nb_bal==29 and self.nb_pump>=self.maxi) or (self.nb_bal >=30)): # if 30 balloons have been used
                finalvalue = ((self.bar.value)*100)/30 # change value in percentage
                texts = 'you have finished this experience,thank you for your time \n your score is :'+str("%.2f" % finalvalue) +'% \n You earn '+str(self.p)+' pounds'
                self.files.write("score : %.2f \n" % finalvalue)
                self.box3 = FloatLayout(orientation='vertical')
                self.box3.add_widget(Label(text=texts,size_font='20sp',size_hint=(None,None),size=(100,70),pos_hint={'center_x':0.5,'center_y':0.75}))
                self.box3.add_widget(Button(text='close the BART test',size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.5,'center_y':0.25},on_press=self.close))
                self.popup = Popup(title='END',content=self.box3,size_hint = (0.7,0.7),auto_dismiss=False)
                Clock.schedule_once(partial(self.pop),1)
                self.nb_pump = 0
                deb2 = time.time()  # take the time 
                self.deb = (deb2 - self.deb)*1000
                self.tabms += [int(self.deb)]  
                self.deb = deb2
                l = len(self.tabms)  
                self.tabal += [l]   
                i = 0
                self.files.write("\nballoon, t1 [ms], t2, ... until balloon pops or collect \n")
                while (i<len(self.tabal)-1):        
                    self.files.write(str(self.tabms[self.tabal[i]:self.tabal[i+1]])+"\n")  
                    i+=1
                self.files.close()  # close the text file
                tps2 = time.time()
                timer = round(tps2-self.tps1,2)
                with open(self.ID, "r+") as file: # complete last informations in the file, open the file in read+
                    text = file.read() # read the file
                    i = text.index("XXXX")
                    j = text.index("ZZZZ")
                    k = text.index("PP.PP")
                    file.seek(0)
                    file.write(text[:i] + str(time.strftime('%H:%M',time.localtime())) + text[i + 4: j] + str(timer) + text[j+ 5:k] + str(self.p)+text[k + 5: ])
                Clock.schedule_once(partial(self.sit),7) # wait the end of the Nao's peach before turn off its motors
            elif ( k == 1 ): # if the balloon must explode
                self.maxi=randint(1,127) # give a new maximum value
                self.b = 0 # reboot 
                self.s = 0
                deb2 = time.time() # note when the button was click
                self.deb = (deb2 - self.deb)*1000  # seconde => ms
                self.tabms += [int(self.deb)]   # round and add in the table
                self.deb = deb2
                l = len(self.tabms) # note the changing of balloon
                self.tabal += [l] # add the changing on the table
            elif (k == 0) : # if the balloon doesn't explode, it blow up
                if (self.nb_pump == 0): # if i's the first pump for this balloon
                    self.im_boom.opacity = 0
                    self.im_bal.opacity = 1
                    self.reward.opacity = 1
                    self.tabms+=[self.nb_bal+1]
                self.nb_pump+=1
                self.im_bal.source = "images/balloon.png"
                self.sound_pump.play() # pump sound
                y = y+ 0.003 # change the size of balloon
                x = x + 0.002
                deb2 = time.time()       
                self.deb = (deb2 - self.deb)*1000  
                self.tabms += [int(self.deb)]    
                self.deb = deb2 
            self.im_bal.size_hint_y = y  # update values of the game
            self.im_bal.size_hint_x = x
            self.pump.text = str(self.nb_pump)
            self.balloon.text = str(self.nb_bal)
            self.delivery2 = time.time()
            if ((self.b == 1) and (self.delivery2-self.delivery >= self.t) ) : # if nao is demanding
                self.delivery = time.time()
                alea = randint(1,16)
                if (alea == 1):
                    self.speak("again") # nao speech
                    self.t = 1.5 # time to wait before an other sentence
                elif (alea == 2):
                    self.speak("I want a big balloon")
                    self.t = 2.5 
                elif (alea == 3):
                    self.speak("It will be the bigest balloon in the word")
                    self.t = 3
                elif (alea == 4):
                    self.speak("Why no try one more ?")
                    self.t = 2.5
                elif (alea == 5):
                    self.speak("pump again this balloon")
                    self.t = 2
                elif (alea == 6):
                    self.speak("try again")
                    self.t = 1.5
                elif (alea == 7):
                   self.speak("one more pump please ")
                   self.t = 1.5
                elif (alea == 8):
                    self.speak("continue to pump")
                    self.t = 2
                elif (alea == 9):
                    self.speak("I think you have time before an explosion")
                    self.t = 3.5
                elif (alea == 10):
                    self.speak("I want to win more money")
                    self.t = 2
                elif (alea == 11):
                    self.speak("I think it's a good idea to pump again")
                    self.t = 3
                elif (alea == 12):
                    self.speak("I don't think you risk something")
                    self.t = 2.5
                elif (alea == 13):
                    self.speak("even more please")
                    self.t = 2
                elif (alea == 14):
                    self.speak("once more")
                    self.t = 1
                elif (alea == 15):
                    self.speak("if you want to win money you should pump more")
                    self.t = 3.5
                elif (alea == 16):
                    self.speak("Come on you can do better")
                    self.t = 2
                self.s +=1 # nao's interventions

    def pop(self,btn): # open the end popup
        self.popup.open() 

    def sit(self,btn): # turn off motors of Nao
        self.motionProxy.rest()
    
    def open_rules(self,btn):  # fonction called by the 'rules' button
        popup = Popup(title='rules',title_align ='center',title_size = '30sp', content=Label(text='''
            You are going to see 30 air balloons, one after the other.

            Click on "pump balloon" to inflate them. You can pump at most 127 times.

            Be careful! Balloons can pop at anytime! Some might even pop after a
            single pump.

            Each pump is worth 0.01 pound: the more you pump, the more you earn!
            But if the balloon pops, you lose your gains for that balloon.

            At any time, you can click "Collect reward" to save your current gains,
            and start with a new balloon. Remember, you have 30 balloons in total.

            Attention: if you quit the test before the end, you will not earn anything. '''),size_hint = (None,None),size=(650,450)) # create the popup window
        popup.open() # open the rules window

    def quits(self,btn): # fonction called by the 'quit' button, asks a confirmation before quit the game
        self.tts = ALProxy("ALTextToSpeech")
        self.box = FloatLayout( orientation='vertical')
        testq = '''
        Are you sure you want to quit ?
        You will not receive any money'''
        self.speak("Are you sure you want to quit me ?") # nao speaks 
        self.box.add_widget(Label(text = testq,size_font = '20sp',size_hint=(None,None),size=(100,70),pos_hint={'center_x':0.5,'center_y':0.75}))
        self.box.add_widget(Button(text='yes',size_hint=(None,None),size=(120,100),pos_hint={'center_x':0.25,'center_y':0.3},on_press=self.yes))
        self.box.add_widget(Button(text='no',size_hint=(None,None),size=(120,100),pos_hint={'center_x':0.75,'center_y':0.3},on_press=self.no))
        self.popup = Popup(title='Exit', content= self.box, size_hint=(None, None), size=(400, 300),auto_dismiss = False)
        self.popup.open()  # open the popup

    def no(self,btn): # if the participant comes back on the game
        self.popup.dismiss()
        self.speak("cool !")

    def yes(self,btn):   # if the participant wants quit the game before the end
        self.speak("ok, good bye")
        finalvalue = ((self.bar.value)*100)/30
        texts = 'you have finished this experience,thank you for your time \n your score is :'+str("%.2f" % finalvalue) +'% \n '
        self.box2 = FloatLayout(orientation='vertical')
        self.box2.add_widget(Label(text=texts,size_font='20sp',size_hint=(None,None),size=(100,70),pos_hint={'center_x':0.5,'center_y':0.75}))
        self.box2.add_widget(Button(text='close the BART test',size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.5,'center_y':0.25},on_press=self.close))
        popup = Popup(title='END',content=self.box2,size_hint = (0.7,0.7),auto_dismiss=False) 
        popup.open() # open the popup window
        self.files.write("%d , %d , %d , %d , %d , 0,  %.2f \n" % (self.nb_bal+1,self.b,self.s,self.nb_pump,self.maxi,self.p))
        self.files.write("score : %.2f \n" % finalvalue)
        deb2 = time.time()              
        self.deb = (deb2 - self.deb)*1000     
        self.tabms += [int(self.deb)]         
        self.deb = deb2           
        x = len(self.tabms)           
        self.tabal += [x]      
        i = 0
        self.files.write("\nballoon, t1 [ms], t2, ... until balloon pops or collect \n")
        while (i<len(self.tabal)-1):   
            self.files.write(str(self.tabms[self.tabal[i]:self.tabal[i+1]])+"\n")  
            i+=1
        self.files.write("quit button used")
        self.files.close() # close the file
        tps2 = time.time()
        timer = round(tps2-self.tps1,2) # compt seconds passed on the test
        with open(self.ID, "r+") as file: # 'r+' to read and write on the file
            text = file.read() # read the file
            i = text.index("XXXX") # note the starting of the "XXXX" chain
            j = text.index("ZZZZ")
            k = text.index("PP.PP")
            file.seek(0) # comme back at the start of the file
            file.write(text[:i] + str(time.strftime('%H:%M',time.localtime())) + text[i + 4: j] + str(timer) + text[j+ 5:k] + str(00.00)+text[k + 5: ])
        self.motionProxy.rest() # Nao turns off its motors
    
    def close(self,btn):
        App.get_running_app().stop()


class StartApp(App):

    def build(self):
        layout = FloatLayout(padding=10, orientation='vertical')
        self.btn1 = Button(text="start",size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.5,'center_y':0.25})
        self.btn1.bind(on_press=self.buttonClicked)
        layout.add_widget(self.btn1) # 'start' button
        self.lbl1 = Label(text="Please, enter your participant ID",font_size='30sp', pos_hint={'center_x':0.5,'center_y':0.75})
        layout.add_widget(self.lbl1) # text on the window 
        self.txt1 = TextInput(text='', multiline=False,size_hint=(None,None),size=(200,35),pos_hint={'center_x':0.5,'center_y':0.5})
        layout.add_widget(self.txt1) # place to write the participant ID
        return layout

    def opac(self,x):
        x=1
        self.btn1.opacity=1

    def part_2(self,x): # differents paragraphs of rules
        self.lbl1.text='''
        Click on "pump balloon" to inflate them. You can pump at most
        127 times. '''

    def part_3(self,x):
        self.lbl1.text='''
        Be careful! Balloons can pop at anytime! Some might even
        pop after a single pump. '''

    def part_4(self,x):
        self.lbl1.text='''
        Each pump is worth 0.01 pound: the more you pump, the more
        you earn!
        But if the balloon pops, you lose your gains for that balloon. '''

    def part_5(self,x):
        self.lbl1.text='''
        At any time, you can click "Collect reward" to save your
        current gains, and start with a new balloon. Remember,
        you have 30 balloons in total. '''

    def part_6(self,x):
        self.lbl1.text='''
        Attention:
        if you quit the test before the end, you will not earn anything. '''

    def part_7(self,x):
        self.lbl1.text='''
        If you have questions, it is the right time to ask! Good luck! '''

    def buttonClicked(self,btn):
        if (self.btn1.text=="start"):
            bla = self.txt1.text
            fileID = path +str(bla)+".txt" # create file's name with the participant ID
            if (exists(fileID)):
                self.lbl1.text = "This ID already exist. Please choose an other ID"
            else :
                files = open( fileID,"a") # open the text file
                files.write( "Participant ID : %s \nRobot present : yes \nType : incite robot \n" %(bla)) # write in the text file
                times = "Date : "+ str(time.strftime('%d/%m/%y',time.localtime()))+"\nStart time : "+str(time.strftime('%H:%M',time.localtime()))+"\n"
                files.write(times)
                BART_TestApp.tps1 = time.time()
                files.write("End time : XXXX \nElapsed time : [s] ZZZZ \nTotal reward : PP.PP \n")
                files.close()  # close the text files
                self.lbl1.font_size='25sp'
                self.lbl1.pos_hint={'center_x':0.5,'center_y':0.65}
                self.lbl1.text='''
                You are going to see 30 air balloons, one after the other. '''    # change the text on the window
                try :
                    self.myBroker = ALBroker("myBroker", "0.0.0.0", 0, IP, PORT)  # robot part
                except RuntimeError :
                    self.myBroker = ALBroker("myBroker", "0.0.0.0", 0, IP, PORT)
                self.module = RobotControllerModule("module")
                self.postureProxy = ALProxy("ALRobotPosture")
                self.trackerThread = threading.Thread(target = self.module.track)
                self.trackerThread.start() # activate a thread
                # presentation of the game by nao \\pau\\ make pauses during its speech, \\rspd\\ is for the output of the Nao's speech
                self.module.say('''\\rspd=75\\You are going to see 30 air balloons, one after the other.\\pau=2000\\

                Click on "pump balloon" to inflate them. You can pump at most 127 times. \\pau=2000\\

                Be careful! \\pau=500\\ Balloons can pop at anytime! Some might even pop after a
                single pump. \\pau=2000\\

                Each pump is worth 0.01 pound: the more you pump, the more you earn! \\pau=500\\
                But if the balloon pops, you lose your gains for that balloon.\\pau=2000\\

                At any time, you can click "Collect reward" to save your current gains,
                and start with a new balloon. Remember, you have 30 balloons in total. \\pau=2000\\

                Attention:\\pau=500\\ if you quit the test before the end, you will not earn anything.\\pau=2000\\

                If you have questions, it is the right time to ask! Good luck! ''')
                self.btn1.opacity=0 # hidden the 'start' button
                self.btn1.text="start the test" # turn 'start' into 'start game'
                self.btn1.pos_hint={'center_x':0.5,'center_y':0.15}
                self.btn1.size=(250,125) # change the size of the button
                self.txt1.size=(0,0) # reduce the TextInput
                self.txt1.opacity=0  # hidden the TextInput
                Clock.schedule_once(partial(self.part_2),13) # post rules paragraph per paragraph
                Clock.schedule_once(partial(self.part_3),24)
                Clock.schedule_once(partial(self.part_4),32)
                Clock.schedule_once(partial(self.part_5),47)
                Clock.schedule_once(partial(self.part_6),61)
                Clock.schedule_once(partial(self.part_7),69.5)
                Clock.schedule_once(partial(self.opac),73) # reapper the 'start game' button
        elif (self.btn1.opacity == 0):
            return
        elif (self.btn1.text=="start the test"):
            App.get_running_app().stop() # close the starting window
            BART_TestApp.ID = path +str(self.txt1.text)+".txt" # to change on an other computer
            BART_TestApp().run()   # call the game

Window.fullscreen = True
StartApp().run()

