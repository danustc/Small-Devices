# this is the main program of functional animation
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

def init(line):
    line.set_data([], [])

def animate(pattern_mode):
    '''
    load a selected pattern mode
    '''


def main():
    fig=plt.figure(figsize = (5,3))
    anim = animation.FuncAnimation(fig, animate, init_func = init, frames = 200, interval = 20, blit = True)
