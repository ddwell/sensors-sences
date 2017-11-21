import decimal
import drivers.grove_rgb_lcd as grove_rgb_lcd  #import *
import drivers.grove_oled as grove_oled #import *

class LCD:                
    def __init__(self):
        self.dpR, self.dpG, self.dpB = 100, 100, 100
        self.dpText = ''
        self.busy = False
        self.pendingMessages = []
        
    class Message:
        def __init__(self, text, colour):
            self.text = text
            self.colour = colour
    
    def reset(self):
        self.deletePendingMessages()
        grove_rgb_lcd.setRGB(0,0,0)
        grove_rgb_lcd.setText('')        
        
    def updateColour(self):
        if not self.busy:
            grove_rgb_lcd.setRGB(self.dpR, self.dpG, self.dpB)     
        
    def updateColourVar(self,r,g,b):
        self.dpR, self.dpG, self.dpB = r, g, b
        self.updateColour()
        
    def defaultColour(self):
        self.dpR, self.dpG, self.dpB = 100,100,100  
        self.updateColour()
    
    def updateText(self,):
        if not self.busy:
            grove_rgb_lcd.setText(self.dpText)
        
    def updateTextVar(self, text=''):
        self.dpText = text
        self.updateText()
        
    def newMessage(self, text, colour=[10,10,10]):
        self.pendingMessages.append(self.Message(text,colour))
        
    def popMessage(self, message):
        grove_rgb_lcd.setText(message.text)
        grove_rgb_lcd.setRGB(message.colour[0], message.colour[1], message.colour[2])        
        try:
            self.pendingMessages.pop(0)
        except:
            print('Error: Message: List is already empty')
#         time.sleep(message.duration)
    
    def displayMessage(self):
        self.busy = True
        if len(self.pendingMessages) > 0:
            self.popMessage(self.pendingMessages[0])                
                
    def endDisplayMessage(self):
        self.busy = False
        self.updateColour()
        self.updateText()
        
    def deletePendingMessages(self):
        for i,x in enumerate(self.pendingMessages):
            self.pendingMessages.pop(i)