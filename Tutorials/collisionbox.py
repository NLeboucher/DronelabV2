# import required libraries
import pygame
import random

# initialize pygame objects
pygame.init()

# define the colours
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)

# set the Dimensions
width = 650
height = 700

# size of a block
pixel = 64

# set Screen
screen = pygame.display.set_mode((width, 
								height))

# set caption
pygame.display.set_caption("CORONA SCARPER")

# load the image
gameIcon = pygame.image.load("rectangleBlock.png")

# set icon
pygame.display.set_icon(gameIcon)

# load the image
backgroundImg = pygame.image.load("wallBackground.jpg")
