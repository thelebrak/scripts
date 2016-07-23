#!/usr/bin/env python3

import sys
import random

def get_chinese_words(line):
    word_list = []
    if line.startswith('*'):
        line = line.replace('*', '')
        for sentence in line.split(':'):
            word = sentence.strip().rstrip()
            word_list.append(word)
    return word_list

def pick_a_word(chinese_words):
    word = random.choice(chinese_words)
    wtype = random.randint(0, 1)

    # We suppose wtype == 0
    target = " - ".join(word[:-1])
    solution = word[2]

    if wtype == 1:
        target, solution = solution, target
    
    return target, solution

if __name__ == '__main__':
    filename = sys.argv[1]
    chinese_words = []
    
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            word_list = get_chinese_words(line)
            if word_list:
                chinese_words.append(word_list)

    nb = input("combien de fois veux-tu faire l'exercice ? ")

    for i in range(0, int(nb)):
        print("****************************")
        print("Exercice n°", i+1)
        target, solution = pick_a_word(chinese_words)
        input("Que veut-dire ce mot ? '"+ target +"'\n")
    
        print("La solution est : ", solution)

        input("J'espère que tu as réussi ! Presse 'entrez' pour passer à la suite ")
