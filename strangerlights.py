#!/usr/bin/python

# Stranger Things Christmas Lights
# Author: Paul Larson (djhazee@gmail.com)
#
# -Port of the Arduino NeoPixel library strandtest example (Adafruit).
# -Uses the WS2811 to animate RGB light strings (I am using a 5V, 50x RGB LED strand)
# -This will blink a designated light for each letter of the alphabet


# Import libs used
import time
import random
from neopixel import *
from twitter import setupStream

#Start up random seed
random.seed()
tweets = []
people = set([
  'andrew',
  'elizabeth',
  'everyone'
])

# LED strip configuration:
LED_COUNT      = 50      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

#Predefined Colors and Masks
OFF = Color(0,0,0)
WHITE = Color(255,255,255)
RED = Color(255,0,0)
GREEN = Color(0,255,0)
BLUE = Color(0,0,255)
PURPLE = Color(128,0,128)
YELLOW = Color(255,255,0)
ORANGE = Color(255,50,0)
TURQUOISE = Color(64,224,208)
RANDOM = Color(random.randint(0,255),random.randint(0,255),random.randint(0,255))

#list of colors, tried to match the show as close as possible
COLORS = [YELLOW,GREEN,RED,BLUE,ORANGE,TURQUOISE,GREEN,
          YELLOW,PURPLE,RED,GREEN,BLUE,YELLOW,RED,TURQUOISE,GREEN,RED,BLUE,GREEN,ORANGE,
          YELLOW,GREEN,RED,BLUE,ORANGE,TURQUOISE,RED,BLUE, 
          ORANGE,RED,YELLOW,GREEN,PURPLE,BLUE,YELLOW,ORANGE,TURQUOISE,RED,GREEN,YELLOW,PURPLE,
          YELLOW,GREEN,RED,BLUE,ORANGE,TURQUOISE,GREEN,BLUE,ORANGE] 

#bitmasks used in scaling RGB values
REDMASK = 0b111111110000000000000000
GREENMASK = 0b000000001111111100000000
BLUEMASK = 0b000000000000000011111111

# Other vars
ALPHABET = '*********nopqrstuvwxyz*******m*l*k*jihgf*edcb*a***'#'*******abcdefghijklm********zyxwvutsrqpon*********'  #alphabet that will be used
LIGHTSHIFT = 0  #shift the lights down the strand to the other end 
FLICKERLOOP = 3  #number of loops to flicker

def initLights(strip):
  """
  initializes the light strand colors 

  inputs: 
    strip = color strip instance to action against

  outputs:
    <none>
  """
  colorLen = len(COLORS)
  #Initialize all LEDs
  for i in range(len(ALPHABET)):
    strip.setPixelColor(i+LIGHTSHIFT, COLORS[i%colorLen])
  strip.show()

def blinkWords(strip, word):
  """
  blinks a string of letters

  inputs: 
    strip = color strip instance to action against
    word = word to blink

  outputs:
    <none>
  """
  #create a list of jumbled ints
  s = list(range(len(ALPHABET)))
  random.shuffle(s)

  #first, kill all lights in a semi-random fashion
  for led in range(len(ALPHABET)):
    strip.setPixelColor(s[led] + LIGHTSHIFT, OFF)
    strip.show()
    time.sleep(random.randint(2,15)/1000.0)

  #quick delay
  time.sleep(1.6)

  #if letter in alphabet, turn on 
  #otherwise, stall
  for character in word:
    if character in ALPHABET:
      strip.setPixelColor(ALPHABET.index(character) + LIGHTSHIFT, RED)
      strip.show()
      time.sleep(0.9)
      strip.setPixelColor(ALPHABET.index(character) + LIGHTSHIFT, OFF)
      strip.show()
      time.sleep(.3)
      print character
    else:
      print ' '
      time.sleep(.75)
  print ' '

def flicker(strip, ledNo):
  """
  creates a flickering effect on a bulb

  inputs: 
    strip = color strip instance to action against
    ledNo = LED position on strand, as integer.

  outputs:
    <none>
  """
  #get origin LED color
  origColor = strip.getPixelColor(ledNo)

  #do FLICKERLOOP-1 loops of flickering  
  for i in range(0,FLICKERLOOP-1):

    #get current LED color, break out to individuals
    currColor = strip.getPixelColor(ledNo)
    currRed = (currColor & REDMASK) >> 16
    currGreen = (currColor & GREENMASK) >> 8
    currBlue = (currColor & BLUEMASK)

    #turn off for a random short period of time
    strip.setPixelColor(ledNo, OFF)
    strip.show()
    time.sleep(random.randint(10,50)/1000.0)

    #turn back on at random scaled color brightness
    #modifier = random.randint(30,120)/100
    modifier = 1
    #TODO: fix modifier so each RGB value is scaled. 
    #      Doesn't work that well so modifier is set to 1. 
    newBlue = int(currBlue * modifier)
    if newBlue > 255:
      newBlue = 255
    newRed = int(currRed * modifier)
    if newRed > 255:
      newRed = 255
    newGreen = int(currGreen * modifier) 
    if newGreen > 255:
      newGreen = 255
    strip.setPixelColor(ledNo, Color(newRed,newGreen,newBlue))
    strip.show()
    #leave on for random short period of time
    time.sleep(random.randint(10,80)/1000.0)

  #restore original LED color
  strip.setPixelColor(ledNo, origColor)

def sleep(duration, check):
  while duration >= 1:
    if check():
      return
    time.sleep(1)
    duration -= 1
  if check():
    return
  if duration:
    time.sleep(duration)

keywords = set([
  'hi', 'welcome', 'hello', 'greetings', 'hey', 'yo',
  'bye', 'goodbye', 'good bye', 'adios',
  'drink'
])

def addPerson(strip, text):
  if ' ' not in text and text not in keywords:
    people.add(text)
    print(str(people))

def removePerson(strip, text):
  if ' ' not in text:
    print('REMOVING', text)
    people.remove(text)

def parseSpecial(strip, text):
  triggers = ['hi', 'welcome', 'hello', 'greetings', 'hey', 'yo']
  for hi in triggers:
    greet = hi + ' '
    if text.startswith(greet):
      text = text[len(greet):]
      addPerson(strip, text)
      return False

  triggers = ['bye', 'goodbye', 'good bye', 'adios']
  for bye in triggers:
    greet = bye + ' '
    if text.startswith(greet):
      text = text[len(greet):]
      removePerson(strip, text)
      return False

  if text.startswith('drink'):
    tweets.pop(0)
    makeDrink(strip)
    return True

  return False

def showTweet(strip, text=None):
  override = False
  if text:
    tweets.insert(0, text)
    override = True

  print('SHOW', text)
  print(tweets)

  if not len(tweets):
    return
  text = tweets[0]

  if parseSpecial(strip, text):
    return

  if not override:
    #flicker each light, no delay between each
    for i in range(20):
      flicker(strip,random.randint(LIGHTSHIFT, len(ALPHABET) + LIGHTSHIFT))
      time.sleep(random.randint(4, 34)/1000.0)

    time.sleep(1.6)

  #flash lights to word
  blinkWords(strip, text)
  time.sleep(1)

  #create a list of jumbled ints
  s = list(range(len(ALPHABET)))
  random.shuffle(s)

  #turn on each light in a semi-random fasion
  colorLen = len(COLORS)

  #Initialize all LEDs
  for i in range(len(ALPHABET)):
    strip.setPixelColor(s[i] + LIGHTSHIFT, COLORS[s[i] % colorLen])
    strip.show()
    time.sleep(random.randint(10, 70) / 1000.0)

  initLights(strip)
  time.sleep(3.3)
  tweets.pop(0)

  if len(tweets):
    showTweet(strip)

def flashWord(strip, word, color):
  print('FLASH', word)
  timeDelta = 0.4
  offDelta = 0.2

  seen = set()
  for c in word:
    index = ALPHABET.index(c) + LIGHTSHIFT
    if index in seen:
      strip.setPixelColor(index, OFF)
      strip.show()
      time.sleep(offDelta)
    else:
      seen.add(index)
    strip.setPixelColor(index, color)
    strip.show()
    time.sleep(timeDelta)

  time.sleep(timeDelta)
  for index in seen:
    strip.setPixelColor(index, OFF)
  strip.show()

def makeDrink(strip):
  colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
  name = random.sample(people, 1)[0]
  for i in xrange(3 * len(colors)):
    for j in xrange(LED_COUNT):
      strip.setPixelColor(j, colors[(i + j) % len(colors)])
    strip.show()
    time.sleep(0.15)

  for c in [RED, YELLOW, GREEN]:
    flashWord(strip, 'drink', c)

  initLights(strip)
  time.sleep(0.2)

  showTweet(strip, name)

def onTweet(strip, text):
  print('Queued:', text)
  tweets.append(text)
  if len(tweets) == 1:
    showTweet(strip)

def testLights(strip):
  num = 0
  for i in xrange(LED_COUNT):
    strip.setPixelColor(num, GREEN)
  strip.show()
  while True:
    print num
    strip.setPixelColor(num, RED)
    strip.show()
    time.sleep(1)
    strip.setPixelColor(num, OFF)
    strip.show()
    time.sleep(0.5)
    num = (num + 1) % LED_COUNT

# Main program logic follows:
if __name__ == '__main__':
  # Create NeoPixel object with appropriate configuration.
  strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
  # Intialize the library (must be called once before other functions).
  strip.begin()

  print ('Press Ctrl-C to quit.')

  setupStream(strip, onTweet)
      