import board
import neopixel
import time

pixel_pin = board.D21

# The number of NeoPixels
num_pixels = 58

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

#walk2
my_color = (194,100,185)
dim_by = 25
sop = 0

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, auto_write=True, pixel_order=ORDER
)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle():
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        print(pixels[i], pixel_index)

def gui():
    print('-----------------------------------        _____            _____   ')
    print('1    : blinking green             |       |     \-\        /     |\ ')
    print('2    : blinking blue              |       |      \-\      /      |-|')
    print('3    : blinking red               |       |       \-\    /       |-|')
    print('4    : white                      |       |        \-\  /        |-|')
    print('5    : red                        |       |   |\    \-\/    /|   |-|')
    print('6    : green                      |       |   |-\    \/    /-|   |-|')
    print('7    : blue                       |       |   |-|\        /--|   |-|')
    print('8    : rainbow                    |       |   |-| \      /--/|   |-|')
    print('9    : walk1                      |       |   |-|  \____/--/ |   |-|')
    print('11   : walk2                      |       |   |-|   \____\/  |   |-|')
    print('12   : fade                       |       |___|-|            |___|-|')
    print('0    : turn off led               |        \___\|             \___\|arkiso')
    print('q    : quit                       |')
    print('-----------------------------------')       



while True:

    gui()
    a = input('give command:')
    
    if a == str('1'):
        print('blinking green')
        for i in range(5,0,-1):
            if (i % 2) == 0:
                pixels.fill((0,255,0))
            else:
                pixels.fill((0,0,0))
            time.sleep(0.1)
    elif a == str('2'):
        print('blinking blue')
        for i in range(5,0,-1):
            if (i % 2) == 0:
                pixels.fill((0,0,255))
            else:
                pixels.fill((0,0,0))
            time.sleep(0.1)
    elif a == str('3'):
        print('blinking red')
        for i in range(5,0,-1):
            if (i % 2) == 0:
                pixels.fill((255,0,0))
            else:
                pixels.fill((0,0,0))
            time.sleep(0.1)
    elif a == str('7'):
        print('blue')
        pixels.fill((0,0,255))
    elif a == str('6'):
        print('green')
        pixels.fill((0,255,0))
    elif a == str('5'):
        print('red')
        pixels.fill((255,0,0))
    elif a == str('8'):
        print('rainbow')
        rainbow_cycle()
    elif a == '4' :
        print('white')
        pixels.fill((100,100,100))
    elif a == '9':
        print('walk1')
        tambah = 0
        putaran = 10
        
        while tambah != 10:
            for x in range(57, -1, -1):
                pixels[x] = (0, 100, 0)
                time.sleep(0.01)
                if x == 0:
                    tambah += 0.5
                    print (tambah)
                    for y in range (0,58,1):
                        pixels[y] = (0,0,100)
                        time.sleep(0.01)
                        if y == 57:
                            tambah += 0.5
                            print(tambah)


    elif a == '11':
        print('walk2')
        tambah = 0
        putaran = 5
        
        while True:
            pixels[sop] = my_color
            pixels[0:] = [[max(i-dim_by,0) for i in l] for l in pixels]
            sop = (sop+1) % num_pixels
            pixels.show()
            time.sleep(0.05)#speed
            #print(tambah)
            '''if sop == 57:
                tambah += 1
            elif tambah == putaran:
                break'''
    
    elif a == '12':
        color = [0,0,0]
        increment = 10
        print('fade')

        tambah = 0
        num_of_breath = 10

        while True:

            color[2] += increment
            #color[1] += increment
            #color[0] += increment

            if color[2] >= 255:
                color[2] = 255
                #color[0] = 255
                increment = -10
                #time.sleep(1)
                tambah += 0.5

            elif color[2] <= 0:
                color[2] = 0
                #color[0] = 0
                increment = 10
                #time.sleep(1)
                tambah +=0.5

            elif tambah == num_of_breath:
                break

            pixels.fill(color)
            pixels.write()
            #print(tambah)





                
#--------------------OFF-----------------%
    elif a == '0':
        print('LED OFF')
        pixels.fill((0,0,0))

    elif a == str('q'):
        print('exit from program')
        pixels.fill((0,0,0))
        exit()
        
    else:
        print('wrong command')
