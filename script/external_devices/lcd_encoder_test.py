from lcd_display import *
from rotary_encoder import *

def modeChoice(mode):
    if(mode == "Mode 1"):
        #faire action 1
        pass
    #faire de meme pour tous les autres modes


def main():
    ListMode = ["Mode 1","Mode 2","Mode 3","Mode 4"]
    indexList = 0

    encoder = Encoder()
    

    while True:
        if(encoder.updateCount()):
            indexList = encoder.getCount()

            if(indexList <= len(ListMode)):
                if(encoder.isPair()):
                    lcd_string(ListMode[indexList],LCD_LINE_1)
                    lcd_string(ListMode[indexList + 1],LCD_LINE_2)
                else:
                    lcd_string(ListMode[indexList - 1],LCD_LINE_1)
                    lcd_string(ListMode[indexList],LCD_LINE_2)
        
        else:
            lcd_string(ListMode[indexList],LCD_LINE_1)
            lcd_string(ListMode[indexList + 1],LCD_LINE_2)
        
        if (encoder.isClicked()):
            modeChoice(ListMode[indexList])
            



if __name__ == '__main__':
    try:
        main()
    except:
        pass