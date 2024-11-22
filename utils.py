import random
import string
from constants import *

def generate_random_message():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def get_random_question():
    return random.choice(RANDOM_QUESTIONS)