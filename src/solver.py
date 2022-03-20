"""
- 色々なゲームのsolver
"""

import os
import re
import random
from typing import Tuple

from collections import defaultdict

import numpy as np

class woldle_solver:

    wordlist_path = "/usr/share/dict/words" #/usr/share/dict/words にスペルチェック用のワードリストがあるらしい
    possiblewordslist_path = "data/wordlist"

    wordle_pat = "^[A-Za-z]{5}$"
    check_str_pat = "^[0-2]{5}$"

    state_str = "⬜🟨🟩"

    first_word = "SALET"

    def __init__(self) -> None:
        if not os.path.exists(self.possiblewordslist_path):
            self.make_wordlistfile()

        self.ng_char = set()
        self.must_char = set()
        with open(self.possiblewordslist_path) as fp:
            self.word_list = [s.strip() for s in fp.readlines()]

        self.word_list_hist = [self.word_list]

    def make_wordlistfile(self):
        input_fp = open(self.wordlist_path)
        output_fp = open(self.possiblewordslist_path, mode='w')

        for word in input_fp:
            if self.check_inputword(word):
                output_fp.write(word.upper())

        input_fp.close()
        output_fp.close()

    def answer(self):
        if self.word_list == []:
            return None
        
        cand_word = self.choose_ans_by_entropy()
        self.word_list.remove(cand_word)
        return cand_word

    #乱択
    def choose_ans(self):
        return random.choice(self.word_list)

    # 残りの候補数が最小になるように選択（ans_wordが一様分布に従うと仮定した場合の情報量最大化）
    # 時間計算量はO(n^2)
    def choose_ans_by_entropy(self):
        
        # 初手の最善は前計算できるので...
        if len(self.word_list) > 6000 and self.first_word in self.word_list:
            return self.first_word

        ent_word_list = []

        for cand_word in self.word_list:
            d = defaultdict(int)
            for ans_word in self.word_list:
                d[self.check_state(cand_word, ans_word)] += 1
            entropy = np.sum(np.vectorize(lambda x:x * np.log2(x))(list(d.values())))
            ent_word_list.append((entropy, cand_word))

        return sorted(ent_word_list)[0][1]

    def validate_checkstr(self, check_str):
        return re.match(self.check_str_pat, check_str)

    def validate_inputword(self, word):
        return re.match(self.wordle_pat, word)
    
    def update_list(self, cand_word: str, check_str: str, list_: list=None) -> list:
        # 0 -> nope
        # 1 -> hit
        # 2 -> brow

        req_pat = []

        for i in range(5):
            if check_str[i] == '2':
                req_pat.append(f'({cand_word[i]})')
                self.must_char.add(cand_word[i])
                continue
            else:
                req_pat.append(f'([^{cand_word[i]}])')
                found_answer = False
            
            if check_str[i] == '0':
                self.ng_char.add(cand_word[i])
            else:
                self.must_char.add(cand_word[i])

        if len(self.ng_char) == 0:
            self.ng_char = set("9") #dummy

        ng_pat = "[" + "".join(list(self.ng_char)) + "]"
        req_pat = ''.join(req_pat)

        if list_:
            list_ = [w for w in list_ if re.match(req_pat, w) and  
                not re.search(ng_pat, w) and all([ch in w for ch in self.must_char])]
            
            return list_
       
        else:
            self.word_list = [w for w in self.word_list if re.match(req_pat, w) and  
                not re.search(ng_pat, w) and all([ch in w for ch in self.must_char])]
            
            self.word_list_hist.append(self.word_list)
       
            return self.word_list
    
    def back_word_list(self):
        if len(self.word_list_hist) == 1:
            return -1
        else:
            self.word_list = self.word_list_hist.pop()
            return 0

    def check_state(self, word, ans):
        res = []
        for i in range(len(ans)):
            res.append(self.state_str[2 if word[i] == ans[i] else 1 if word[i] in ans else 0])
        return "".join(res)


if __name__ == "__main__":
    solver = woldle_solver()
    print(solver.better_choose_ans())