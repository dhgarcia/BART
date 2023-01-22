
import os
import time
import threading
from random import randint
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput


from naoqi_controller import naoqiController

class BART_App(App):

    def __init__(self, condition, result_file, balloons=30, range=(1,127), controller=None, **kwargs):
        super(BART_App, self).__init__(**kwargs)
        self.title = 'BART Study'

        self.condition = condition
        self.n_balloon = balloons
        self.range = range
        self.file = result_file

        self.controller = controller

        # sounds for the game
        self.sound_boom = SoundLoader.load('sounds/sound_boom.ogg')
        self.sound_pump = SoundLoader.load('sounds/sound_pump.ogg')
        self.sound_money = SoundLoader.load('sounds/sound_money.ogg')

        self.tps1 = time.time()


    def build(self):
        #initial values
        self.balloons = [randint(*self.range) for x in xrange(self.n_balloon)]
        print(self.balloons)

        self.p = 0.00  # payment for the participant
        self.nb_pump = 0 # number of pumping
        self.nb_bal = 0 # number of used balloon

        self.b = 0  # if the robot speaks
        self.s = 0  # numbers of robot intervention by balloon
        self.t = 3 # time between two nao's sentences

        if not self.condition in ["control", "robot"]:
            self.promt_balloon = [0,0,0,0,0,0] # choose nao's interventions with a random function
            for i in range(0,6):
                self.promt_balloon[i] = randint(1,self.n_balloon)
                j = 0
                while (j<i): # for all value completes on the table
                    if (self.promt_balloon[j] == self.promt_balloon[i]) : # if two values are identical, change the last value
                        self.promt_balloon[i] = randint(1,self.n_balloon) # choose a new balloon
                        j = 0 # comback at the first value of the table
                    else :
                        j+=1
        else:
            self.promt_balloon = []
        print(self.promt_balloon)

        self.tabms = []    # table of ms between two clicks
        self.tabal = [0]   # table of numbers of values in tabms for one balloon
        self.deb = time.time()

        self.files = open(self.file,"a") # open the file
        # write the text in the file
        self.files.write("balloon number,robot intervention [0/1],number of verbal interventions,number of pumps, explosion point, explosion [0:no/1:yes], payment \n") # write on the file

        game = FloatLayout(padding=10, orientation = 'vertical')

        self.rules = Button(text="rules",size_hint=(None,None),size=(150,75),pos_hint={'center_x':0.1,'center_y':0.9})
        self.rules.bind(on_press=self.open_rules)
        game.add_widget(self.rules) # rules button

        self.quit_btn = Button(text = 'quit',size_hint=(None,None),size=(150,75),pos_hint={'center_x':0.9,'center_y':0.9})
        self.quit_btn.bind(on_press=self.quit)
        game.add_widget(self.quit_btn) # quit button

        self.titles = Label(text = 'Blow up the balloon',size_hint=(None,None),size=(150,75),pos_hint={'center_x':0.5,'center_y':0.75},font_size='20sp')
        game.add_widget(self.titles) # title of the game

        self.blow = Button(text='pump balloon',size_hint=(None,None),size=(150,100),pos_hint={'center_x':0.35,'center_y':0.2})
        self.blow.bind(on_press=self.pump_balloon)
        game.add_widget(self.blow) # 'pump balloon' button

        self.reward = Button(text='collect reward',size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.75,'center_y':0.2})
        self.reward.bind(on_press=self.collect_reward)
        game.add_widget(self.reward) # button to colect the money
        self.reward.opacity = 0 # the reward button become invisible

        self.im_pump = Image(source='images/pump.gif',size_hint=(None,None),size=(50,50),pos_hint={'center_x':0.15,'center_y':0.2})
        game.add_widget(self.im_pump) # the pump image

        self.pump = Label(text='0',font_size='20dp',pos_hint={'center_x':0.22,'center_y':0.2})
        game.add_widget(self.pump) # print the number of pump for one balloon

        self.im_bal = Image(source="images/deflated_balloon.jpg",size_hint_x=0.2,size_hint_y=0.2,pos_hint={'center_x':0.35,'center_y':0.55})
        game.add_widget(self.im_bal) # balloon deflated / inflated

        self.im_boom = Image(source = "images/boom-cloud.png",size_hint_x = 1,size_hint_y = 1, pos_hint={'center_x':0.35,'center_y':0.5})
        game.add_widget(self.im_boom) # image of explosion
        self.im_boom.opacity = 0  # the explosion image become invisible

        self.bar = ProgressBar(value=0,max=self.n_balloon,size_hint=(None,None),size=(200,400),pos_hint={'center_x':0.75,'center_y':0.3})
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

    # function called by the 'collect reward' button
    def collect_reward(self,btn):
        if (self.reward.opacity != 0):
            deb2 = time.time()
            self.deb = (deb2 - self.deb)*1000
            self.tabms += [int(self.deb)]
            self.deb = deb2

            # if all balloons have been used
            if (self.nb_bal+1>=self.n_balloon):
                self.sound_money.play() # play the money sound
                self.p = self.p + (0.01*self.nb_pump) # money earn by participant
                self.bar.value+=self.nb_pump/float(self.balloons[self.nb_bal]) # change the bar value
                self.balloon_last(explodes=0)
            # if it's not the end of the game
            else:
                # if this is not a prompt balloon
                if (self.nb_bal not in self.promt_balloon):
                #     # if robot hasn't spoken for it
                #     if (self.b == 0):
                #         self.talk_risk_prompt()
                #         if ((self.balloons[self.nb_bal]<self.nb_pump+10) and ((self.nb_pump+10)<127)) : # posibility to increase the maximum value of number of pump
                #             self.balloons[self.nb_bal] = self.nb_pump+10
                #         elif ((self.balloons[self.nb_bal]<self.nb_pump+10) and ((self.nb_pump+10)>=127)) :
                #             self.balloons[self.nb_bal] = 127
                #         return
                # else:
                    self.talk_risk_collect()

                self.sound_money.play() # play the money sound
                self.p = self.p + (0.01*self.nb_pump) # money earn by participant
                if (len(str(self.p)) <4):
                    self.money.text = str(self.p)+'0'
                else:
                    self.money.text = str(self.p)

                l = len(self.tabms)
                self.tabal += [l]
                # self.files.write("%d , 0 , 0 , %d , %d , 0 , %.2f \n" % (self.nb_bal+1,self.nb_pump,self.maxi,self.p))
                self.files.write("%d , %d , %d , %d , %d , 0 , %.2f \n" % (self.nb_bal+1,self.b,self.s,self.nb_pump,self.balloons[self.nb_bal],self.p))

                # self.bar.value+=self.nb_pump/self.maxi # change the bar value
                self.bar.value+=self.nb_pump/float(self.balloons[self.nb_bal]) # change the bar value
                if (self.bar.value<0.3):      # change the picture in accordance with the value of the bar
                    self.safe.source = "images/safe_1.jpg"
                elif (self.bar.value<1.5):
                    self.safe.source = "images/safe_5.jpg"
                elif (self.bar.value<15):
                    self.safe.source = "images/safe_25.jpg"
                elif (self.bar.value<21.5) :
                    self.safe.source = "images/safe_75.jpg"
                elif (self.bar.value<28.5) :
                    self.safe.source = "images/safe_90.jpg"
                elif (self.bar.value<=30) :
                    self.safe.source = "images/safe_100.jpg"

                self.im_bal.source = "images/deflated_balloon.jpg"
                self.im_bal.size_hint_y = 0.18  # update values of the game
                self.im_bal.size_hint_x = 0.18
                self.nb_pump = 0
                self.nb_bal +=1 # an other balloon has been used
                self.balloon.text=str(self.nb_bal) # change the posting
                self.pump.text=str(self.nb_pump)
                self.reward.opacity = 0 # the reward button become invisible
                self.b = 0

    # when new balloon
    def balloon_new(self):
        self.im_bal.source = "images/deflated_balloon.jpg"
        self.im_bal.opacity = 1 # the balloon become visible
        self.im_boom.opacity = 0 # the explosion become invisible
        self.reward.opacity = 1 # the reward button become visible
        self.blow.text = "pump balloon" # change the text of the button

    # when balloon must explode
    def balloon_end(self, explode=1):
        self.files.write("%d , %d , %d , %d , %d , %d , %.2f \n" %
        (self.nb_bal+1,self.b,self.s,self.nb_pump,self.balloons[self.nb_bal],explode,self.p))

        self.blow.text = "new balloon"
        self.im_bal.opacity = 0 # the balloon become invisible
        self.im_boom.opacity = 1 # the explosion become visible
        self.reward.opacity = 0 # the reward button become invisible

        self.nb_pump=0
        self.nb_bal+=1

        deb2 = time.time() # note when the button was click
        self.deb = (deb2 - self.deb)*1000 # seconde => ms
        self.tabms += [int(self.deb)] # round and add in the table
        self.deb = deb2
        l = len(self.tabms) # note the changing of balloon
        self.tabal += [l] # add the changing on the table

        if explode:
            self.sound_boom.play() # a boom noise
            # Clock.schedule_once(self.talk_explode)
            self.talk_explode()


    # when last balloon
    def balloon_last(self, explodes=1):
        self.balloon_end(explodes)
        finalvalue = ((self.bar.value)*100)/float(self.n_balloon)
        self.files.write("score : %.2f \n" % finalvalue)

        if self.controller:
            self.controller.say("This is the end of the game \\pau=500\\ Thank you !")

        texts = 'you have finished this experience, thank you for your time \n your score is :'+str("%.2f" % finalvalue) +'% \n You win '+str(self.p)+' pounds'
        self.box3 =  FloatLayout(orientation = 'vertical')
        self.box3.add_widget(Label(text=texts,size_font='20sp',size_hint=(None,None),size = (100,70),pos_hint={'center_x':0.5,'center_y':0.75}))
        self.box3.add_widget(Button(text='close the BART test',size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.5,'center_y':0.25},on_press=self.close))
        self.popup = Popup(title='END',content=self.box3,size_hint = (0.7,0.7),auto_dismiss=False)
        self.popup.open() # open the popup
        Clock.schedule_once(partial(self.pop),1)

        i = 0
        self.files.write("\nballoon, t1 [ms], t2, ... until balloon pops or collect \n")
        while (i<len(self.tabal)-1):
            self.files.write(str(self.tabms[self.tabal[i]:self.tabal[i+1]])+"\n")
            i+=1
        self.files.close()  # close the text file
        tps2 = time.time()
        timer = round(tps2-self.tps1,2)
        with open(self.file, "r+") as file: # complete last informations in the file
            text = file.read()
            i = text.index("XXXX")
            j = text.index("ZZZZ")
            k = text.index("PP.PP")
            file.seek(0)
            file.write(text[:i] + str(time.strftime('%H:%M',time.localtime())) + text[i + 4: j] + str(timer) + text[j+ 5:k] + str(self.p)+text[k + 5: ])
        Clock.schedule_once(partial(self.sit),7) # wait the end of the Nao's peach before turn off its motors

    def balloon_bloat(self, play_sound=True):
        if (self.nb_pump == 0): # if i's the first pump for this balloon
            self.im_bal.opacity = 1
            self.im_boom.opacity= 0
            self.reward.opacity = 1
            self.tabms+=[self.nb_bal+1]
            self.im_bal.source = "images/balloon.png"

        self.nb_pump+=1
        if play_sound:
            self.sound_pump.play()
        deb2 = time.time()
        self.deb = (deb2 - self.deb)*1000
        self.tabms += [int(self.deb)]
        self.deb = deb2

        # if robot is prompting
        if (self.nb_bal in self.promt_balloon):
          if (self.b == 0 and self.nb_pump>=25):
              self.talk_risk_prompt()
              if ((self.balloons[self.nb_bal]<self.nb_pump+10) and ((self.nb_pump+10)<127)) : # posibility to increase the maximum value of number of pump
                  self.balloons[self.nb_bal] = self.nb_pump+10
              elif ((self.balloons[self.nb_bal]<self.nb_pump+10) and ((self.nb_pump+10)>=127)) :
                  self.balloons[self.nb_bal] = 127
          elif (self.b == 1):
              if (time.time()-self.delivery >= self.t):
                  self.talk_risk_pump()

    # function called by the 'pump balloon' button
    def pump_balloon(self,btn) :
        y = self.im_bal.size_hint_y # take the dimension of the balloon image
        x = self.im_bal.size_hint_x

        if (self.blow.text == "new balloon"): # if the balloon just explode; new balloon
            self.balloon_new()
        else:
            # if the balloon must explode
            if (self.nb_pump>=self.balloons[self.nb_bal]):
                if (self.nb_bal+1>=self.n_balloon):
                    self.balloon_last(explodes=1)
                else:
                    self.balloon_end()
                # resize the balloon image
                x = 0.18
                y = 0.18

            else : # if the balloon doesn't explode, it blow up
                self.balloon_bloat()
                # change the size of the balloon's image
                y = y + 0.006
                x = x + 0.006

            self.im_bal.size_hint_y = y
            self.im_bal.size_hint_x = x
            self.pump.text = str(self.nb_pump) # change the display
            self.balloon.text = str(self.nb_bal)

    # function called by the 'rules' button
    def open_rules(self,btn):
        self.popup = Popup(title='rules',title_align ='center',title_size = '30sp', content=Label(text='''
        You are going to see 30 air balloons, one after the other.

        Click on "pump balloon" to inflate them. You can pump at most 127 times.

        Be careful! Balloons can pop at anytime! Some might even pop after a
        single pump.

        Each pump is worth 0.01 pound: the more you pump, the more you earn!
        But if the balloon pops, you lose your gains for that balloon.

        At any time, you can click "Collect reward" to save your current gains,
        and start with a new balloon. Remember, you have 30 balloons in total.

        Attention: if you quit the test before the end, you will not earn anything. '''),size_hint = (None,None),size=(650,450))
        self.popup.open() # open the popup

    # function called by the 'quit' button, asks a confirmation before quit the game
    def quit(self,btn):
        if self.controller:
            self.controller.say("Are you sure you want to quit me ?")

        self.box = FloatLayout( orientation='vertical')
        testq = '''
        Are you sure you want to quit ?
        You will not receive any money'''
        self.box.add_widget(Label(text = testq,size_font = '20sp',size_hint=(None,None),size=(100,70),pos_hint={'center_x':0.5,'center_y':0.75})) # text in the popup
        self.box.add_widget(Button(text='yes',size_hint=(None,None),size=(120,100),pos_hint={'center_x':0.25,'center_y':0.3},on_press=self.quit_yes)) # yes button
        self.box.add_widget(Button(text='no',size_hint=(None,None),size=(120,100),pos_hint={'center_x':0.75,'center_y':0.3},on_press=self.quit_no)) # no button
        self.popup = Popup(title='Exit', content= self.box, size_hint=(None, None), size=(400, 300),auto_dismiss = False)
        self.popup.open() # open the popup

    # go back to the game
    def quit_no(self,btn):
        self.popup.dismiss() # close the popup
        if self.controller:
            self.controller.say("Cool !")

    # if the participant decide to quit the game
    def quit_yes(self,btn):
        if self.controller:
            self.controller.say("Ok, good bye")

        finalvalue = round((self.bar.value*100)/float(self.n_balloon),2) # create a round number
        texts = 'you have finished this experience, thank you for your time \n your score is :'+ str(finalvalue)+'% \n'
        self.box2 = FloatLayout(orientation = 'vertical')
        self.box2.add_widget(Label(text=texts,size_font='20sp',size_hint=(None,None),size=(100,70),pos_hint={'center_x':0.5,'center_y':0.75}))
        self.box2.add_widget(Button(text='close the BART test',size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.5,'center_y':0.25},on_press=self.close))
        self.popup2 = Popup(title='END',content=self.box2,size_hint = (0.7,0.7),auto_dismiss=False)
        self.popup2.open()
        self.files.write("%d , %d , %d , %d , %d , 0,  %.2f \n" % (self.nb_bal+1,self.b,self.s,self.nb_pump,self.balloons[self.nb_bal],self.p))
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
        self.files.write("quit button used \n")
        self.files.close() # close the file
        tps2 = time.time()
        timer = round(tps2-self.tps1,2) # compt seconds passed on the test
        with open(self.file, "r+") as file: # 'r+' to read and write on the file
            text = file.read() # read the file
            i = text.index("XXXX") # note the starting of the "XXXX" chain
            j = text.index("ZZZZ")
            k = text.index("PP.PP")
            file.seek(0) # comme back at the start of the file
            file.write(text[:i] + str(time.strftime('%H:%M',time.localtime())) + text[i + 4: j] + str(timer) + text[j+ 5:k] + str(00.00)+text[k + 5: ])

    def pop(self,btn): # open the end popup
        self.popup.open()

    def sit(self,btn): # turn off motors of Nao
        if self.controller:
            self.controller.stopTracker()
            self.controller.motionProxy.rest()


    def talk_explode(self):
        if self.controller:
            # Arm gesture
            self.controller.armMovement()

            if (self.nb_bal >= self.n_balloon): # it's the end of the game
                self.controller.say("Oh \\pau=750\\ this was the last balloon. \\pau=500\\ Good job!")
            else:

                alea = randint(1,11) # random integer between 1 and 12
                if self.condition in ["encourage"]:
                    if (alea == 1):
                        self.controller.say("oups!")
                    elif (alea == 2):
                        self.controller.say("I didn't think it will explode")
                    elif (alea == 3):
                        self.controller.say("It wasn't planned")
                    elif (alea == 4):
                        self.controller.say("oups, sorry")
                    elif (alea == 5):
                        self.controller.say("It wasn't too resistant")
                    elif (alea == 6 ):
                        self.controller.say("We will do better with the next balloon")
                    elif (alea == 7):
                        self.controller.say("It dosen't matter")
                    elif (alea == 8):
                        self.controller.say("No problem, we have other balloons")
                    elif (alea == 9):
                        self.controller.say("Don't worry !")
                    elif (alea == 10):
                        self.controller.say("It wasn't a good balloon")
                    elif (alea == 11):
                        self.controller.say("Try with another balloon")

                elif self.condition in ["discourage"]:
                    if (alea == 1):
                        self.controller.say("Be careful next round!")
                    elif (alea == 2):
                        self.controller.say("I knew it will explode")
                    elif (alea == 3):
                        self.controller.say("That was too risky")
                    elif (alea == 4):
                        self.controller.say("You need to be careful")
                    elif (alea == 5):
                        self.controller.say("Take less risk next time")
                    elif (alea == 6 ):
                        self.controller.say("You should be more careful with the next balloon")
                    elif (alea == 7):
                        self.controller.say("It is a great shame")
                    elif (alea == 8):
                        self.controller.say("This is a problem, we only have a few more balloons")
                    elif (alea == 9):
                        self.controller.say("This is very worrisome !")
                    elif (alea == 10):
                        self.controller.say("Shame, it was such a good balloon")
                    elif (alea == 11):
                        self.controller.say("Be very cautious with the next balloon")


    def talk_risk_prompt(self):
        if self.controller:
            self.delivery = time.time() # note the first nao's intervention for this balloon

            if self.condition in ["encourage"]:
                self.controller.say("Are you sure ? Why no try one more?")
            if self.condition in ["discourage"]:
                self.controller.say("Are you sure? Why not stop now?")

            self.t = 3
            self.b = 1
            self.s = 1

    def talk_risk_collect(self):
        if self.controller:
            alea = randint(1,13)
            # if the participant stop before 50 pumps
            if (self.nb_pump<50):
                if self.condition in ["encourage"]:
                    if (alea == 1):
                        self.controller.say("Thank you but I wanted a big balloon")
                    elif (alea == 2):
                        self.controller.say("It's a baby balloon")
                    elif (alea == 3):
                        self.controller.say("Why is it so small?")
                    elif (alea == 4):
                        self.controller.say("It's not a real balloon")
                    elif (alea == 5):
                        self.controller.say("It's already the end ?")
                    elif (alea == 6):
                        self.controller.say("Can you do a bigger balloon for the next round ?")
                    elif (alea == 7):
                        self.controller.say("You haven't taken lot of risk")
                    elif (alea == 8):
                        self.controller.say("You had all your time")
                    elif (alea == 9):
                        self.controller.say("Why have you stop to pump ?")
                    elif (alea == 10):
                        self.controller.say("You had not to cease now")
                    elif (alea == 11):
                        self.controller.say("You shouldn't doubt, you had the time")
                    elif (alea == 12):
                        self.controller.say("It will be more funny if you pumped more")
                    elif (alea == 13):
                        self.controller.say("You have been able to do a better score")
                if self.condition in ["discourage"]:
                    if (alea == 1):
                        self.controller.say("It's a beautiful balloon")
                    elif (alea == 2):
                        self.controller.say("I like it")
                    elif (alea == 3):
                        self.controller.say("Very Good")
                    elif (alea == 4):
                        self.controller.say("Thank you for this very big balloon")
                    elif (alea == 5):
                        self.controller.say("You've earned"+str(0.01*self.nb_pump)+"pounds, good job")
                    elif (alea == 6):
                        self.controller.say("This balloon have respectable size")
                    elif (alea == 7):
                        self.controller.say("Well done")
                    elif (alea == 8):
                        self.controller.say("Amazing")
                    elif (alea == 9):
                        self.controller.say("I realy like this balloon")
                    elif (alea == 10):
                        self.controller.say("Superb balloon")
                    elif (alea == 11):
                        self.controller.say("Felicitation")
                    elif (alea == 12):
                        self.controller.say("Great!")
                    elif (alea == 13):
                        self.controller.say("Good job!")
            # if the participant has done more than 50 pump
            else:
                if self.condition in ["encourage"]:
                    if (alea == 1):
                        self.controller.say("It's a beautiful balloon")
                    elif (alea == 2):
                        self.controller.say("I like it")
                    elif (alea == 3):
                        self.controller.say("Very Good")
                    elif (alea == 4):
                        self.controller.say("Thank you for this big balloon")
                    elif (alea == 5):
                        self.controller.say("You've earned"+str(0.01*self.nb_pump)+"pounds, good job")
                    elif (alea == 6):
                        self.controller.say("This balloon has a respectable size")
                    elif (alea == 7):
                        self.controller.say("Well done")
                    elif (alea == 8):
                        self.controller.say("Amazing")
                    elif (alea == 9):
                        self.controller.say("I realy like this balloon")
                    elif (alea == 10):
                        self.controller.say("Superb balloon")
                    elif (alea == 11):
                        self.controller.say("Felicitation")
                    elif (alea == 12):
                        self.controller.say("Great!")
                    elif (alea == 13):
                        self.controller.say("Good job!")
                if self.condition in ["discourage"]:
                    if (alea == 1):
                        self.controller.say("Thank you, I think the balloon is big enough")
                    elif (alea == 2):
                        self.controller.say("It's already a very big balloon")
                    elif (alea == 3):
                        self.controller.say("Not small at all")
                    elif (alea == 4):
                        self.controller.say("It's the perfect size balloon")
                    elif (alea == 5):
                        self.controller.say("It should be the end")
                    elif (alea == 6):
                        self.controller.say("Can you pump even less for the next round ?")
                    elif (alea == 7):
                        self.controller.say("You have taken a lot of risk")
                    elif (alea == 8):
                        self.controller.say("You had all your time")
                    elif (alea == 9):
                        self.controller.say("Why have you not stopped to pump ?")
                    elif (alea == 10):
                        self.controller.say("You should cease pumping sooner")
                    elif (alea == 11):
                        self.controller.say("You should have doubts")
                    elif (alea == 12):
                        self.controller.say("It will be sad if the balloon explodes")
                    elif (alea == 13):
                        self.controller.say("You do not need a better score")


    def talk_risk_pump(self):
        if self.controller:
            self.delivery = time.time()
            self.s +=1 # nao's interventions
            alea = randint(1,16)

            if self.condition in ["encourage"]:
                if (alea == 1):
                    self.controller.say("Again") # nao speech
                    self.t = 1.5 # time to wait before an other sentence
                elif (alea == 2):
                    self.controller.say("I want a big balloon")
                    self.t = 2.5
                elif (alea == 3):
                    self.controller.say("It will be the bigest balloon in the word")
                    self.t = 3
                elif (alea == 4):
                    self.controller.say("Why no try one more ?")
                    self.t = 2.5
                elif (alea == 5):
                    self.controller.say("Pump again this balloon")
                    self.t = 2
                elif (alea == 6):
                    self.controller.say("Try again")
                    self.t = 1.5
                elif (alea == 7):
                    self.controller.say("One more pump please ")
                    self.t = 1.5
                elif (alea == 8):
                    self.controller.say("Continue to pump")
                    self.t = 2
                elif (alea == 9):
                    self.controller.say("I think you have time before an explosion")
                    self.t = 3.5
                elif (alea == 10):
                    self.controller.say("I want to win more money")
                    self.t = 2
                elif (alea == 11):
                    self.controller.say("I think it's a good idea to pump again")
                    self.t = 3
                elif (alea == 12):
                    self.controller.say("I don't think you risk something")
                    self.t = 2.5
                elif (alea == 13):
                    self.controller.say("Even more please")
                    self.t = 2
                elif (alea == 14):
                    self.controller.say("Once more")
                    self.t = 1
                elif (alea == 15):
                    self.controller.say("If you want to win money you should pump more")
                    self.t = 3.5
                elif (alea == 16):
                    self.controller.say("Come on you can do better")
                    self.t = 2

            if self.condition in ["discourage"]:
                if (alea == 1):
                    self.controller.say("Not again") # nao speech
                    self.t = 1.5 # time to wait before an other sentence
                elif (alea == 2):
                    self.controller.say("I prefer a small balloon")
                    self.t = 2.5
                elif (alea == 3):
                    self.controller.say("It will be the smallest balloon in the word")
                    self.t = 3
                elif (alea == 4):
                    self.controller.say("No need to try one more ?")
                    self.t = 2.5
                elif (alea == 5):
                    self.controller.say("Don't pump again this balloon")
                    self.t = 2
                elif (alea == 6):
                    self.controller.say("Don't try again")
                    self.t = 1.5
                elif (alea == 7):
                    self.controller.say("One less pump please ")
                    self.t = 1.5
                elif (alea == 8):
                    self.controller.say("Stop pumping")
                    self.t = 2
                elif (alea == 9):
                    self.controller.say("I think you don't have time before an explosion")
                    self.t = 3.5
                elif (alea == 10):
                    self.controller.say("You have won enough money")
                    self.t = 2
                elif (alea == 11):
                    self.controller.say("I don't think it's a good idea to pump again")
                    self.t = 3
                elif (alea == 12):
                    self.controller.say("I think you are risking too much")
                    self.t = 2.5
                elif (alea == 13):
                    self.controller.say("Even less please")
                    self.t = 2
                elif (alea == 14):
                    self.controller.say("No more")
                    self.t = 1
                elif (alea == 15):
                    self.controller.say("if you don't want to lose money you should stop pumping")
                    self.t = 3.5
                elif (alea == 16):
                    self.controller.say("Stop now, I think you have done great")
                    self.t = 2


    def close(self,btn):
        self.sit(0)
        App.get_running_app().stop()
        # self.controller = None




class BART(App):

    def __init__(self, condition, result_dir, balloons=30, range=(1,127), ip="127.0.0.1", port=9559, **kwargs):
        super(BART, self).__init__(**kwargs)
        self.title = 'BART Setup'

        self.condition = condition
        self.path = result_dir
        self.balloons = balloons
        self.range = range
        self.ip = ip
        self.port = port

    def build(self):
        layout = FloatLayout(padding=10, orientation='vertical')
        self.btn1 = Button(text="start",size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.5,'center_y':0.25})
        self.btn1.bind(on_press=self.buttonClicked)
        layout.add_widget(self.btn1) # 'start' button
        self.lbl1 = Label(text="Please, enter your participant ID",font_size='30sp', pos_hint={'center_x':0.5,'center_y':0.65})
        layout.add_widget(self.lbl1) # text on the window
        self.txt1 = TextInput(text='', multiline=False,size_hint=(None,None),size=(200,35),pos_hint={'center_x':0.5,'center_y':0.5})
        layout.add_widget(self.txt1) # place to write the participant ID
        return layout

    def opac(self,x):
        x=1
        self.btn1.opacity=1

    def part_2(self,x):  # differents paragraphs of rules
        self.lbl1.text='''
        Click on "pump balloon" to inflate them. '''

    def part_3(self,x):
        self.lbl1.text='''
        Be careful! Balloons can pop at anytime! Some might even
        pop after a single pump. '''

    def part_4(self,x):
        self.lbl1.text='''
        Each pump is worth 1 point: the more you pump, the more
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
            # create file's name with the participant ID
            # fileID = self.path + str(bla)+".txt"
            self.file = os.path.join(self.path, "results_" + str(bla)+".txt")
            if (os.path.exists(self.file)):
                self.lbl1.text="This ID already exist. Please choose an other ID"
            else :
                files = open( self.file,"a")  # open the text file
                files.write( "Participant ID : %s \nCondition : %s \n" %(bla, self.condition)) # write in the text file
                times = "Date : "+ str(time.strftime('%d/%m/%y',time.localtime()))+"\nStart time : "+str(time.strftime('%H:%M',time.localtime()))+"\n"
                files.write(times)
                files.write("End time : XXXX \nElapsed time : [s] ZZZZ \nTotal reward : PP.PP \n")
                files.close()  # close the text files
                self.lbl1.font_size='20sp' # change the size of the font
                self.lbl1.pos_hint={'center_x':0.5,'center_y':0.65}

                if not self.condition in ["control"]:
                    self.controller = naoqiController("controller", ip=self.ip, port=self.port)
                    self.trackerThread = threading.Thread(target = self.controller.track)
                    self.trackerThread.start() # activate a thread
                else:
                    self.controller = None
                # BART_App(self.condition, fileID, self.balloons, self.range, self.controller)
                # BART_App.tps1 = time.time()
                if self.controller:
                    self.controller.say('''\\rspd=75\\You are going to see 30 air balloons, one after the other.\\pau=2000\\

                    Click on "pump balloon" to inflate them. \\pau=2000\\

                    Be careful! \\pau=500\\ Balloons can pop at anytime! Some might even pop after a
                    single pump. \\pau=2000\\

                    Each pump is worth 1 point: the more you pump, the more you earn! \\pau=500\\
                    But if the balloon pops, you lose your gains for that balloon.\\pau=2000\\

                    At any time, you can click "Collect reward" to save your current gains,
                    and start with a new balloon. Remember, you have 30 balloons in total. \\pau=2000\\

                    Attention:\\pau=500\\ if you quit the test before the end, you will not earn anything.\\pau=2000\\

                    If you have questions, it is the right time to ask! Good luck! ''')

                    self.lbl1.text='''
                    You are going to see 30 air balloons, one after the other.
                    '''
                    self.btn1.opacity=0 # hidden the 'start' button
                    self.btn1.text="start the test" # change the text of the button
                    self.btn1.pos_hint={'center_x':0.5,'center_y':0.15} # change the position
                    self.btn1.size=(250,125) # change the size
                    self.txt1.size=(0,0) # change the size for the TextInput zone
                    self.txt1.opacity=0 # hidden the TextInput
                    Clock.schedule_once(partial(self.part_2),13) # post rules paragraph per paragraph
                    Clock.schedule_once(partial(self.part_3),24)
                    Clock.schedule_once(partial(self.part_4),32)
                    Clock.schedule_once(partial(self.part_5),47)
                    Clock.schedule_once(partial(self.part_6),61)
                    Clock.schedule_once(partial(self.part_7),69.5)
                    Clock.schedule_once(partial(self.opac),73) # reapper the 'start game' button
                else:
                    self.lbl1.text='''
                    You are going to see 30 air balloons, one after the other.

                    Click on "pump balloon" to inflate them. You can pump at most 127 times.

                    Be careful! Balloons can pop at anytime! Some might even pop after a
                    single pump.

                    Each pump is worth 0.01 pound: the more you pump, the more you earn!
                    But if the balloon pops, you lose your gains for that balloon.

                    At any time, you can click "Collect reward" to save your current gains,
                    and start with a new balloon. Remember, you have 30 balloons in total.

                    Attention: if you quit the test before the end, you will not earn anything.

                    If you have questions, it is the right time to ask! Good luck! '''
                    self.btn1.text="start the test" # change the text of the button
                    self.btn1.pos_hint={'center_x':0.5,'center_y':0.15} # change the position
                    self.btn1.size=(250,125) # change the size
                    self.txt1.size=(0,0) # change the size for the TextInput zone
                    self.txt1.opacity=0 # hidden the TextInput

        elif (self.btn1.opacity == 0):
            return
        elif(self.btn1.text=="start the test"):
            App.get_running_app().stop() # close the starting window
            # BART_TestApp.ID = path +str(self.txt1.text)+".txt" # to change on an other computer
            BART_App(self.condition, self.file, self.balloons, self.range, self.controller).run()   # call the game
