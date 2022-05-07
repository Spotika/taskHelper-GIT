from constants import *
import parseExel
import datetime
import math
import os


def num_of_days(x):
    return (28 + (x + math.floor(x/8)) % 2 + 2 % x + 2 * math.floor(1/x))