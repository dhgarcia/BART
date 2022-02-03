# "C:\Program Files (x86)\Python27\python" C:\Users\erohart\Desktop\BART\BART_3_balloon.py
from __future__ import division
import kivy                                                 # import for the kivy part
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
from optparse import OptionParser
import time
import os,sys, inspect
from os.path import exists

path = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))+"/results/results_"
# path where files will stocks

class BART_TestApp(App):

    def build(self):
        self.tabms = []    # table of ms between two click             
        self.tabal = [0]   # table of numbers of values in tabms for one balloon
        self.deb = time.time()
        self.sound_boom = SoundLoader.load('sounds/sound_boom.ogg')   # sounds for the game
        self.sound_pump = SoundLoader.load('sounds/sound_pump.ogg')
        self.sound_money = SoundLoader.load('sounds/sound_money.ogg')
        self.p = 0.00  # payment for the participant
        self.nb_pump = 0 # number of pumping
        self.nb_bal = 0 # number of used balloon
        self.color = 3 # start the game with a blue balloon
        self.maxi = randint(80,127) # random function for the blue balloon
        game = FloatLayout(padding=10, orientation = 'vertical')
        
        self.rules = Button(text="rules",size_hint=(None,None),size=(150,75),pos_hint={'center_x':0.1,'center_y':0.9})
        self.rules.bind(on_press=self.open_rules)
        game.add_widget(self.rules)  # rules button
        
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
        
        self.im_bal=Image(source="images/deflated_balloon.jpg",size_hint_x=0.2,size_hint_y=0.2,pos_hint={'center_x':0.35,'center_y':0.55})
        game.add_widget(self.im_bal) # balloon deflated / inflated

        self.im_boom = Image(source = "images/boom-cloud.png",size_hint_x = 1,size_hint_y = 1, pos_hint={'center_x':0.35,'center_y':0.5})
        game.add_widget(self.im_boom) # image of explosion
        self.im_boom.opacity = 0 # the explosion image become invisible

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
        
        self.files = open(self.ID,"a") # open the file
        self.files.write("balloon number,color[1:red(1,40)/2:green(35,84)/3:blue(80,127)],robot intervention [0/1],number of verbal interventions,number of pumps, explosion point, explosion [0:no/1:yes], payment \n")
        return game

    def change_value(self,btn):  # fonction called by the 'new balloon' button
        if (self.reward.opacity != 0):
            self.bar.value+=self.nb_pump/self.maxi # change the bar value
            self.sound_money.play() # play the money sound
            r = 0
            self.p = self.p + (0.01*self.nb_pump) # money earn by participant
            deb2 = time.time()   # take the time
            self.deb = (deb2 - self.deb)*1000  # pass in millisecond
            self.tabms += [int(self.deb)]    # add the time between two clicks in the table  
            self.deb = deb2 
            l = len(self.tabms)  # note numbers of  space  comleted for the current balloon   
            self.tabal += [l]
            if (len(str(self.p)) <4):
                self.money.text = str(self.p)+'0'
            else:
                self.money.text = str(self.p)
            if (self.nb_bal>=29): # if  30 balloons have been used
                finalvalue = (self.bar.value*100)/30                
                texts = 'you have finished this experience !! \n Thank you for your time \n your score is :'+str("%.2f" % finalvalue) +'% \n You win '+str(self.p)+' pounds'
                self.box4 = FloatLayout(orientation='vertical')
                self.box4.add_widget(Label(text=texts,size_font='20sp',size_hint=(None,None),size=(100,70),pos_hint={'center_x':0.5,'center_y':0.75}))
                self.box4.add_widget(Button(text='close the BART test',size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.5,'center_y':0.25},on_press=self.close))
                popup = Popup(title='END', content=self.box4,size_hint = (0.7,0.7),auto_dismiss=False)
                popup.open() # open the end's window
                self.files.write("%d , %d , 0 , 0 , %d , %d , 0 , %.2f \n" % (self.nb_bal+1,self.color,self.nb_pump,self.maxi,self.p))    
                self.files.write("score : %.2f \n" % finalvalue)
                i = 0
                self.files.write("\nballoon, t1 [ms], t2, ... until balloon pops or collect \n")
                while (i<len(self.tabal)-1):  # write all values ( in ms ) on the file
                    self.files.write(str(self.tabms[self.tabal[i]:self.tabal[i+1]])+"\n")   
                    i+=1     
                self.files.close() # close the text file
                tps2 = time.time() # take the time at the end of the game
                timer = round(tps2-self.tps1,2) # number of second pass on this game
                with open(self.ID, "r+") as file:  # complete the file
                    text = file.read() # read all the file
                    i = text.index("XXXX") # end time
                    j = text.index("ZZZZ") # time pass on the game
                    k = text.index("PP.PP") # money win by the participant
                    file.seek(0) # comme back at the start of the file
                    file.write(text[:i] + str(time.strftime('%H:%M',time.localtime())) + text[i + 4: j] + str(timer) + text[j+ 5:k] + str(self.p)+text[k + 5: ])
            else : # if it's not the end of the game   
                self.files.write("%d , %d , 0 , 0 , %d , %d , 0 , %.2f \n" % (self.nb_bal+1, self.color,self.nb_pump,self.maxi,self.p))
                self.nb_bal +=1  # an other balloon has been used
                self.balloon.text=str(self.nb_bal) # change the posting
                self.color = randint(1,3) # init the balloon's color
                if (self.color == 1): # change the maximum value in function of the balloon's color
                    self.im_bal.source = "images/deflated_red.png" # red balloon
                    self.maxi = randint(1,40)
                elif(self.color == 2): # green balloon
                    self.im_bal.source = "images/deflated_green.jpg" 
                    self.maxi = randint(35,84)
                else:  # blue balloon
                    self.im_bal.source = "images/deflated_balloon.jpg"
                    self.maxi = randint(80,127)
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
                self.im_bal.size_hint_y = 0.18  # update values of the game
                self.im_bal.size_hint_x = 0.18
                self.nb_pump = 0
                self.pump.text=str(self.nb_pump)
                self.reward.opacity = 0 # the reward button become invisible

    def blow_up(self,btn) :   # fonction called by the 'blow up' button
        y = self.im_bal.size_hint_y  # take the dimention of the balloon image
        x = self.im_bal.size_hint_x
        if (self.blow.text == "new balloon"): # if the balloon just come to explose
            if (self.color == 1):
                self.im_bal.source = "images/deflated_red.png"
                self.maxi = randint(1,40)
            elif (self.color == 2):
                self.im_bal.source = "images/deflated_green.jpg"
                self.maxi = randint(35,84)
            elif (self.color == 3):
                self.im_bal.source = "images/deflated_balloon.jpg"
                self.maxi = randint(80,127)
            self.im_bal.opacity = 1 # the balloon become visible
            self.im_boom.opacity = 0 # the explosion become invisible
            self.reward.opacity = 1 # the reward button become visible
            self.blow.text = "pump balloon" # change the text of the button
        else :
            if ((self.nb_bal==29 and self.nb_pump>=self.maxi) or (self.nb_bal>=30)): # if 30 balloons have been used
                self.im_bal.opacity = 0
                self.im_boom.opacity = 1
                self.sound_boom.play()
                finalvalue = ((self.bar.value)*100)/30
                texts = 'you have finished this experience,thank you for your time \n your score is :'+str("%.2f" % finalvalue) +'% \n You win '+str(self.p)+' pounds'
                self.box3 = FloatLayout(orientation='vertical')
                self.box3.add_widget(Label(text=texts,size_font = '20sp',size_hint=(None,None),size=(100,100),pos_hint={'center_x':0.5,'center_y':0.75}))
                self.box3.add_widget(Button(text='close the BART test',size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.5,'center_y':0.25},on_press=self.close))                
                popup = Popup(title='END',content=self.box3,size_hint = (0.7,0.7),auto_dismiss=False) 
                popup.open() # open the opup               
                self.files.write("%d , %d , 0 , 0 , %d , %d , 1,  %.2f \n" % (self.nb_bal+1,self.color,self.nb_pump,self.maxi,self.p))
                self.files.write("score : %.2f \n" % finalvalue)
                deb2 = time.time() # note when the button was click
                self.deb = (deb2 - self.deb)*1000 # seconde => ms
                self.tabms += [int(self.deb)] # round and add in the table
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
                with open(self.ID, "r+") as file: # complete last informations in the file
                    text = file.read()
                    i = text.index("XXXX")
                    j = text.index("ZZZZ")
                    k = text.index("PP.PP")
                    file.seek(0)
                    file.write(text[:i] + str(time.strftime('%H:%M',time.localtime())) + text[i + 4: j] + str(timer) + text[j+ 5:k] + str(self.p)+text[k + 5: ])
            elif (self.nb_pump>=self.maxi): # if the balloon must explode
                self.files.write("%d , %d , 0 , 0 , %d , %d , 1 , %.2f \n" % (self.nb_bal+1,self.color,self.nb_pump,self.maxi,self.p))
                self.blow.text = "new balloon"
                y = 0.18
                x = 0.18
                self.im_bal.opacity = 0 # the balloon become invisible
                self.im_boom.opacity = 1 # the explosion become visible
                self.reward.opacity = 0 # the reward button become invisible
                self.sound_boom.play() # a boom noise
                self.nb_pump=0 # a boom noise
                self.nb_bal+=1
                deb2 = time.time() # note when the button was click
                self.deb = (deb2 - self.deb)*1000 # seconde => ms
                self.tabms += [int(self.deb)] # round and add in the table
                self.deb = deb2
                l = len(self.tabms) # note the changing of balloon
                self.tabal += [l] # add the changing on the table
                self.color = randint(1,3)
            else : # if the balloon doesn't explode, it blow up
                if (self.nb_pump == 0):  # if i's the first pump for this balloon
                    self.im_bal.opacity = 1
                    self.im_boom.opacity = 0
                    self.reward.opacity = 1
                    self.im_bal.pos_hint = {'center_x':0.35,'center_y':0.55}
                    self.tabms+=[self.nb_bal+1]
                    if (self.color == 1): # choose the balloon color
                        self.im_bal.source = "images/red.png"
                    elif(self.color == 2):
                        self.im_bal.source =  "images/Green_balloon.png"
                    else:
                        self.im_bal.source = "images/balloon.png"
                y = y + 0.006 # change the size of the balloon's image
                x = x + 0.006
                self.nb_pump+=1
                self.sound_pump.play()
                deb2 = time.time() # note when the button was click
                self.deb = (deb2 - self.deb)*1000 # seconde => ms
                self.tabms += [int(self.deb)] # round and add in the table
                self.deb = deb2
            self.im_bal.size_hint_y = y # change the size of the balloon
            self.im_bal.size_hint_x = x
            self.pump.text = str(self.nb_pump)
            self.balloon.text = str(self.nb_bal)

    def open_rules(self,btn):  # fonction called by the 'rules' button
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
        self.popup.open()

    def quits(self,btn):  # fonction called by the 'quit' button, asks a confirmation before quit the game
        self.box = FloatLayout( orientation='vertical')
        testq = '''
        Are you sure you want to quit ?
        You will not receive any money'''
        self.box.add_widget(Label(text = testq,size_font = '20sp',size_hint=(None,None),size=(100,70),pos_hint={'center_x':0.5,'center_y':0.75}))
        self.box.add_widget(Button(text='yes',size_hint=(None,None),size=(120,100),pos_hint={'center_x':0.25,'center_y':0.3},on_press=self.yes))
        self.box.add_widget(Button(text='no',size_hint=(None,None),size=(120,100),pos_hint={'center_x':0.75,'center_y':0.3},on_press=self.no))
        self.popup = Popup(title='Test popup', content= self.box, size_hint=(None, None), size=(400, 300),auto_dismiss = False)
        self.popup.open() # open the popup

    def no(self,btn): # if the participant comes back on the game
        self.popup.dismiss() # close the popup

    def yes(self,btn): # if the participant decide to quit the game
        finalvalue = round((self.bar.value*100)/30,2)# create a round number        
        texts = 'you have finished this experience,thank you for your time \n your score is :'+ str(finalvalue) +'% \n'
        self.box2 = FloatLayout(orientation='vertical')
        self.box2.add_widget(Label(text=texts,size_font='20sp',size_hint=(None,None),size=(100,70),pos_hint={'center_x':0.5,'center_y':0.75}))
        self.box2.add_widget(Button(text='close the BART test',size_hint=(None,None),size=(200,100),pos_hint={'center_x':0.5,'center_y':0.25},on_press=self.close))
        self.popup2 = Popup(title='END',content=self.box2,size_hint = (0.7,0.7),auto_dismiss=False) 
        self.popup2.open()      
        self.files.write("%d , %d , 0 , 0 , %d , %d , 0,  %.2f \n" % (self.nb_bal+1,self.color,self.nb_pump,self.maxi,self.p))
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
        with open(self.ID, "r+") as file: # 'r+' to read and write on the file
            text = file.read() # read the file
            i = text.index("XXXX") # note the starting of the "XXXX" chain
            j = text.index("ZZZZ")
            k = text.index("PP.PP")
            file.seek(0) # comme back at the start of the file
            file.write(text[:i] + str(time.strftime('%H:%M',time.localtime())) + text[i + 4: j] + str(timer) + text[j+ 5:k] + str(00.00)+text[k + 5: ])

    def close(self,btn):
        App.get_running_app().stop()

class StartApp(App):

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

    def buttonClicked(self,btn):
        if (self.btn1.text=="start"):
            bla = self.txt1.text
            fileID = path +str(bla)+".txt" # create file's name with the participant ID
            if (exists(fileID)):
                self.lbl1.text = "This ID already exist.Please choose an other ID"
            else :
                files = open( fileID,"a")  # open the text file 
                files.write( "Participant ID : %s \nRobot present : no \n" %(bla)) # write in the text file
                times = "Date : "+ str(time.strftime('%d/%m/%y',time.localtime()))+"\nStart time : "+str(time.strftime('%H:%M',time.localtime()))+"\n"
                files.write(times)
                BART_TestApp.tps1 = time.time()
                files.write("End time : XXXX \nElapsed time : [s] ZZZZ \nTotal reward : PP.PP \n")
                files.close()  # close the text files
                self.lbl1.font_size='17sp' # change the size of the font
                self.lbl1.pos_hint={'center_x':0.5,'center_y':0.65}
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

                If you have questions, it is the right time to ask! Good luck!'''      
                self.btn1.text="start the test" # change the text of the button
                self.btn1.pos_hint={'center_x':0.5,'center_y':0.15} # change the position
                self.btn1.size=(250,125) # change the size
                self.txt1.size=(0,0) # change the size for the TextInput zone
                self.txt1.opacity=0 # hidden the TextInput
        elif(self.btn1.text=="start the test"):
            App.get_running_app().stop() # close the starting window
            BART_TestApp.ID = path +str(self.txt1.text)+".txt" # to change on an other computer
            BART_TestApp().run()   # call the game

Window.fullscreen = False
StartApp().run() # call the first window
