#!/usr/bin/python
# -*- coding: utf-8 -*-

_author__ = 'dbroqua'

from MyAppli import MyAppli
from time import sleep

if __name__ == '__main__':
    # Initialisation du LCD
    lcd = MyAppli()
    lcd.InitMenu()
    lcd.isStarted = True

    # Initialisation du backlight
    lcd.initBacklight()

    # Ecran d'accueil
    lcd.clear()
    sleep(0.5)
    lcd.message("Adafruit i2c\nDarKou")
    sleep(1)

    # Affichage du menu
    lcd.clear()
    lcd.getItems( -1 )

    # Tant que l'appli est lancée on fait quelque chose
    while lcd.isStarted == True:
        for b in lcd.btn: # Parcours le tableau des boutons en continue
            if lcd.buttonPressed(b[0]): # Le pointeur sur btn est égal au bouton pressé
                lcd.clear() # On efface l'écran avant d'afficher un nouveau message
                curBtn = b[0] # Id du bouton
                lcd.getItems(curBtn) # Affiche d'un message sur l'écran
                curBtn = -1
                sleep(0.5) # Pause de 0.5 secondes pour éviter que les boutons ne buguent

    # Arrêt propre de l'appli
    sleep(1)
    lcd.clear()
    lcd.backlight( 'OFF' )