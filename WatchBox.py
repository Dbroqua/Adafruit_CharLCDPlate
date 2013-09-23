#!/usr/bin/python
# -*- coding: utf-8 -*-

author__ = 'dbroqua'

from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from time import sleep
import ConfigParser


class WatchBox():

    # Begin Extended from Adafruit_CharLCDPlate -------------------------------
    # Port expander input pin definitions
    SELECT = 0
    RIGHT = 1
    DOWN = 2
    UP = 3
    LEFT = 4

    btn = (
        (SELECT, 'Select'),
        (LEFT, 'Gauche'),
        (UP, 'Haut'),
        (DOWN, 'Bas'),
        (RIGHT, 'Droite')
    )

    # LED colors
    COLORS = {}
    COLORS['OFF'] = 0x00
    COLORS['RED'] = 0x01
    COLORS['GREEN'] = 0x02
    COLORS['BLUE'] = 0x04
    COLORS['YELLOW'] = 0x01 + 0x02
    COLORS['TEAL'] = 0x02 + 0x04
    COLORS['VIOLET'] = 0x01 + 0x04
    COLORS['WHITE'] = 0x01 + 0x02 + 0x04
    COLORS['ON'] = 0x01 + 0x02 + 0x04
    # END Extended from Adafruit_CharLCDPlate ---------------------------------

    curMenuIndex = 'MAIN' # Level
    previousMenuIndex = ''
    curMenuPosition = 0 # Position dans le menu actuel
    cursorStyle = "=> "
    menuSize = 0

    menuSequence = {} # Contient l'arborescence complète parcouru
    curIndexMenuSequence = 0
    menu = {} # Contient la liste des éléments permettant de générer le menu
    menu['MAIN'] = (
        ( 'Run' , 'START' ),
        ( 'Settings' , 'SETTINGS' ),
        ( 'About' , 'ABOUT' ),
        ( 'Quit' , 'QUIT' )
    )
    menu['SETTINGS'] = (
        ( 'Color' , 'COLORS' ),
        ( 'Back' , 'BACK' )
    )
    menu['COLORS'] = (
        ( 'Red' , 'RED' ),
        ( 'Green' , 'GREEN' ),
        ( 'Blue' , 'BLUE' ),
        ( 'Yellow' , 'YELLOW' ),
        ( 'Teal' , 'TEAL' ),
        ( 'Violet' , 'VIOLET' ),
        ( 'White' , 'WHITE' ),
        ( 'Back' , 'BACK' )
    )

    isStarted = False

    lcd = ''
    config = ''

    ''' Redéfinition des méthodes de la classe Adafruit pour gagner du temps dans l'écriture '''
    def backlight(self , backlight):
        _backlight = self.COLORS[backlight]
        self.lcd.backlight( _backlight )
    def clear(self):
        self.lcd.clear()
    def message(self,msg):
        self.lcd.message(msg)
    def buttonPressed(self,btn):
        return self.lcd.buttonPressed(btn)
    def scrollDisplayLeft(self):
        self.lcd.scrollDisplayLeft()
    def numlines(self):
        return self.lcd.numlines

    '''
        Fonctions servant pour la gestion du Menu
    '''

    ''' Fonction permettant d'initialiser la gestion du menu '''
    def InitMenu(self):
        self.lcd = Adafruit_CharLCDPlate()
        self.lcd.begin(16, 2)
        self.isStarted = True
        # Initialisation du Menu
        self.menuSequence[self.curIndexMenuSequence] = 'MAIN'
        self.initMenuSize()
        self.readConfigFile()

    ''' Fonction permettant d'initialiser le rétro éclairage de l'écran'''
    def initBacklight(self):
        backlight = self.config.get('Main','backlight')
        self.backlight( backlight )

    ''' Fonction permettant d'initialiser le nombre d'éléments dans le menu courant '''
    def initMenuSize(self):
        self.menuSize = len(self.menu[self.menuSequence[self.curIndexMenuSequence]])

    ''' Fonction permettant d'afficher les éléments du menu / de gérer les actions '''
    def getItems( self , btn ):
        curIndex = self.curMenuPosition # On récupère la position actuelle dans le menu

        # Gestion du bouton
        if btn == self.lcd.SELECT: # Le bouton "select" est appuyé
            curMenuIndex = self.menuSequence[self.curIndexMenuSequence]

            # Il faut effectuer l'action demandée associée au menu courant
            if self.menu[curMenuIndex][curIndex][1] == 'QUIT' :
                self.ActionQuit()
                return True
            if self.menu[curMenuIndex][curIndex][1] == 'ABOUT' :
                self.ActionAbout()
                return True
            if self.menu[curMenuIndex][curIndex][1] == 'BACK' :
                if self.menuSequence[self.curIndexMenuSequence] != 'MAIN':
                    self.curIndexMenuSequence-=1
                    self.initMenuSize()
                    self.getItems( -1 )
                return True
            if curMenuIndex == 'COLORS' : # Demande de changement de couleur du rétro éclairage
                color = self.menu[curMenuIndex][curIndex][1]
                self.writeConfigFile('Main','backlight',color)
                self.backlight( color )
                self.getItems( -1 )
                return True
            if self.menu[self.menu[curMenuIndex][curIndex][1]] : # On regarde si l'action est associée à un sous menu
                CurrentmenuNameIndexed = self.menuSequence[self.curIndexMenuSequence]
                NextmenuNameIndexed = self.menu[curMenuIndex][curIndex][1]
                print("Current Index :"+CurrentmenuNameIndexed)
                print("Next Index : "+NextmenuNameIndexed)
                self.menuSequence[self.curIndexMenuSequence] = CurrentmenuNameIndexed # On stocke l'id du menu actuel
                self.curIndexMenuSequence+=1 # On déplace le pointer vers la droite
                self.menuSequence[self.curIndexMenuSequence] = NextmenuNameIndexed # On stocke l'id du nouveau menu
                self.initMenuSize() # On recalcule le nombre d'éléments dans le menu
                self.curMenuPosition = 0 # On se place au premier élément du nouveau menu
                self.getItems( -1 ) # On affiche le menu
                return True

        else:
            self.lcd.clear()
            if btn == self.lcd.DOWN:
                curIndex+=1
            if btn == self.lcd.UP:
                curIndex-=1

            # Cas des sortie du menu (haut / bas)
            if curIndex < 0:
                curIndex = self.menuSize-1
            if curIndex >= self.menuSize:
                curIndex = 0

            # Génération du texte à afficher
            print(self.menu[self.menuSequence[self.curIndexMenuSequence]][curIndex][0])
            msg = self.cursorStyle + self.menu[self.menuSequence[self.curIndexMenuSequence]][curIndex][0]+"\n"
            if (curIndex+1) != self.menuSize:
                msg+= self.menu[self.menuSequence[self.curIndexMenuSequence]][(curIndex+1)][0]

            # Mise à jours de la position courante du curseur dans menu
            self.curMenuPosition = curIndex

            # On affiche le texte sur l'afficheur
            print(msg)
            self.clear()
            self.message(msg)



    ''' Action permettant de quitter l'application '''
    def ActionQuit(self):
        self.isStarted = False
        self.message("Bye...")
        print("Ending application...")

    ''' Action permettant d'afficher le About '''
    def ActionAbout(self):
        msg = ( 'Test Application Adafruit' , 'Damien Broqua < damien.broqua@gmail.com>' )
        stringSize = len(msg[0])
        if len(msg[1]) > stringSize:
            stringSize = len(msg[1])

        loop = True
        maxloop = stringSize - self.numlines() + 1
        counterScroll = 0
        self.lcd.clear()
        wait = True
        while loop == True:
            self.message( msg[0]+"\n"+msg[1])
            if stringSize > self.numlines():
                sleep(0.5)
                self.scrollDisplayLeft()
                counterScroll+=1
            else:
                sleep(4)
                loop = False

            if counterScroll > maxloop:
                loop = False

            if self.buttonPressed(self.lcd.LEFT): # L'utilisateur appuie sur le bouton de gauche pour revenir au menu précédent
                wait = False
                loop = False

        if wait == True: # L'utilisateur n'a pas appuyé sur le bouton de gauche, on lui ré affiche pendant 2 secondes le message initial
            sleep(2) # Petite pause pour revoir le message initial

        self.curMenuIndex = 'MAIN' # On se repositionne sur le menu principal
        self.getItems(-1) # On affiche le menu principal


    def readConfigFile(self):
        try:
            with open('config.cfg'):
                self.config = ConfigParser.RawConfigParser()
                self.config.read('config.cfg')
        except IOError:
            self.createConfigFile()

    def createConfigFile(self):
        # Initialisation des variables sauvegardées
        self.config = ConfigParser.RawConfigParser()
        self.config.add_section('Main')
        self.config.set('Main', 'backlight', 'RED')

        # Writing our configuration file to 'example.cfg'
        with open('config.cfg', 'wb') as configfile:
            self.config.write(configfile)

    def writeConfigFile(self , section , col , value ):
        self.config.set(section,col,value)
        with open('config.cfg', 'wb') as configfile:
            self.config.write(configfile)
