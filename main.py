import io
import os.path
import pickle
import shutil
import time
import zipfile
from tkinter import Tk
from typing import List, Type, Optional, Dict, Any

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager


def decode(word: str) -> str:
    return (word.replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("ü", "u"))


class WordProvider:
    def __init__(self, cache_filename: str):
        self._cache_filename = cache_filename

    def get_words(self) -> List[str]:
        if os.path.exists(self._cache_filename):
            with open(self._cache_filename, "rb") as f:
                return pickle.load(f)

        words = self._get_words_internal()
        with open(self._cache_filename, "wb") as f:
            pickle.dump(words, f)
        return words

    def _get_words_internal(self) -> List[str]:
        pass

    @staticmethod
    def _is_valid(word: str) -> bool:
        return len(word) == 5 and word.isalpha() and number_vowels(word) > 0


class RaeCorpusProvider(WordProvider):
    def __init__(self):
        super(RaeCorpusProvider, self).__init__(cache_filename="words_RAE.p")

    def _get_words_internal(self) -> List[str]:
        url = "https://corpus.rae.es/frec/CREA_total.zip"

        print("Downloading...")
        r = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        print("Download complete")
        z.extractall("unzipped")
        print("Extraction complete")

        words = []
        with open("unzipped/CREA_total.TXT", "r") as f:
            for line in tqdm(f.readlines()):
                elements = line.split()
                if len(elements) != 4:
                    continue

                word = elements[1].lower()
                if self._is_valid(word):
                    words.append(word)
        shutil.rmtree("unzipped")
        return words


class CorpusDataProvider(WordProvider):
    def __init__(self):
        super(CorpusDataProvider, self).__init__(cache_filename="words_corpus.p")

    def _get_words_internal(self) -> List[str]:
        url = "https://www.corpusdata.org/span/samples/wordLemPoS.zip"

        print("Downloading...")
        r = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        print("Download complete")
        z.extractall("unzipped")
        print("Extraction complete")

        words = []
        with open("unzipped/wordLemPoS.txt", "r") as f:
            for line in tqdm(f.readlines()):
                elements = line.split()
                if len(elements) != 5:
                    continue

                word = elements[3].lower()
                if self._is_valid(word):
                    words.append(word)
        shutil.rmtree("unzipped")
        return words


class ListaPalabrasProvider(WordProvider):
    def __init__(self):
        super(ListaPalabrasProvider, self).__init__(cache_filename="words_listapalabras.p")

    @staticmethod
    def _get_clean_string(element) -> str:
        return str(element.text).rstrip("\n").strip()

    def _get_words_internal(self) -> List[str]:
        url = "https://www.listapalabras.com/"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/97.0.4692.99 Safari/537.36"}
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, features="html.parser")

        words = []

        div = soup.find("div", {"class": "abecedario"})
        for a in tqdm(div.find_all("a")):
            href = a["href"]
            subpage = requests.get(url + href + "&total=s", headers=headers)
            sub_soup = BeautifulSoup(subpage.content, features="html.parser")

            column = sub_soup.find("div", {"id": "columna_resultados_generales"})
            for sub_a in column.find_all("a", {"id": "palabra_resultado"}):
                word = self._get_clean_string(sub_a).lower()

                if self._is_valid(word):
                    words.append(word)
        return words


def number_vowels(word: str) -> int:
    vowels = ["a", "e", "i", "o", "u"]
    word = decode(word)
    count = 0
    for vowel in vowels:
        if vowel in word:
            count += 1
    return count


def word_scoring(word: str, weights: Dict[str, float], allow_duplicates: bool = False) -> float:
    chars = list(decode(word))
    if not allow_duplicates:
        chars = list(set(chars))
    score = 0
    for c in chars:
        if c in weights:
            score += weights[c]
    return score


class Game:
    def __init__(self):
        self.green = {}
        self.yellow = {}
        self.black = set()
        self.num_attempts = 0
        self.finished = False

    def play(self):
        pass

    def new_attempt(self, word: str):
        pass

    def is_finished(self) -> bool:
        return self.finished

    def is_successful(self) -> bool:
        return sum(len(val) for val in self.green.values()) == 5

    def _finish(self):
        self.finished = True

    def _green(self, letter: str, idx: int):
        if letter not in self.green:
            self.green[letter] = set()
        self.green[letter].add(idx)

    def _yellow(self, letter: str, idx: int):
        if letter not in self.yellow:
            self.yellow[letter] = set()
        self.yellow[letter].add(idx)

    def _black(self, letter: str):
        self.black.add(letter)

    def close(self) -> str:
        return ""


class SimulatedGame(Game):
    def __init__(self, word: str):
        super(SimulatedGame, self).__init__()
        self._word = word
        self._dictionary = ListaPalabrasProvider().get_words()
        self._rows_results = []

    def new_attempt(self, word: str) -> bool:
        if word not in self._dictionary:
            return False

        word = decode(word)
        solution = decode(self._word)

        row_result = ""
        for i, c in enumerate(word):
            if c in solution:
                if solution[i] == c:
                    self._green(c, i)
                    row_result += "🟩"
                else:
                    self._yellow(c, i)
                    row_result += "🟨"
            else:
                self._black(c)
                row_result += "⬜"
        print("{:s}: {:s}".format(word.upper(), row_result))
        self._rows_results.append(row_result)

        correct = word == solution
        self.num_attempts += 1
        if correct or self.num_attempts >= 6:
            self._finish()
        return True

    def close(self) -> str:
        result = "Wordle (ES) #0 {:d}/6".format(self.num_attempts) + os.linesep
        for row_result in self._rows_results:
            result += row_result + os.linesep
        result += os.linesep + "wordle.danielfrg.com"
        return result


class WebGame(Game):
    def __init__(self):
        super(WebGame, self).__init__()
        self._browser = None

    def play(self):
        s = Service(ChromeDriverManager().install())
        # noinspection PyArgumentList
        self._browser = webdriver.Chrome(service=s)
        self._browser.maximize_window()
        self._browser.get("https://wordle.danielfrg.com/")

        time.sleep(1)

        self._browser.find_element(By.XPATH, "//button[contains(., 'Jugar!')]").click()

        time.sleep(0.5)

    def _update_result(self, row_idx: int) -> bool:
        main = self._browser.find_element(By.TAG_NAME, "main")
        rows = main.find_elements(By.XPATH, "div/div")
        row = rows[row_idx]
        flips = row.find_elements(By.CLASS_NAME, "react-card-flip")
        green_count = 0
        for column, flip in enumerate(flips):
            back = flip.find_element(By.CLASS_NAME, "react-card-back")
            letter_div = back.find_element(By.TAG_NAME, "div")
            letter_class = letter_div.get_attribute("class")
            letter = letter_div.text.lower()
            if "bg-present" in letter_class:
                # yellow
                self._yellow(letter, column)
            elif "bg-correct" in letter_class:
                # green
                self._green(letter, column)
                green_count += 1
            elif "bg-absent" in letter_class:
                # black
                self._black(letter)
            else:
                raise ValueError("Unknown class: " + letter_class)
        return green_count == 5

    def new_attempt(self, word: str) -> bool:
        word = decode(word)
        for c in word:
            self._browser.find_element(By.XPATH, '//button[@aria-label="{:s}"]'.format(c)).click()
        self._browser.find_element(By.XPATH, '//button[@aria-label="procesar palabra"]').click()

        time.sleep(0.5)

        try:
            self._browser.find_element(By.XPATH, '//div[@class="Toastify__toast-container '
                                                 'Toastify__toast-container--top-center"]')
            ret_button = self._browser.find_element(By.XPATH, '//button[@aria-label="borrar letra"]')
            for _ in range(5):
                ret_button.click()
            # toast doesn't disappear if window not focused
            self._browser.switch_to.window(self._browser.window_handles[0])
            time.sleep(5)  # wait for toast to disappear
            return False
        except NoSuchElementException:
            correct = self._update_result(self.num_attempts)
            self.num_attempts += 1
            if correct or self.num_attempts >= 6:
                self._finish()
            return True

    def close(self) -> str:
        time.sleep(2)
        self._browser.find_element(By.XPATH, "//button[contains(., 'Compartir')]").click()
        self._browser.close()
        return Tk().clipboard_get()


# https://es.wikipedia.org/wiki/Frecuencia_de_aparici%C3%B3n_de_letras
weights = {
    "a": 0.1253,
    "b": 0.0142,
    "c": 0.0468,
    "d": 0.0586,
    "e": 0.1368,
    "f": 0.0069,
    "g": 0.0101,
    "h": 0.0070,
    "i": 0.0625,
    "j": 0.0044,
    "k": 0.0002,
    "l": 0.0497,
    "m": 0.0315,
    "n": 0.0671,
    "ñ": 0.0031,
    "o": 0.0868,
    "p": 0.0251,
    "q": 0.0088,
    "r": 0.0687,
    "s": 0.0798,
    "t": 0.0463,
    "u": 0.0393,
    "v": 0.0090,
    "w": 0.0001,
    "x": 0.0022,
    "y": 0.0090,
    "z": 0.0052,
}


def play_game(first_guesses: List[str], candidates: List[str], game_cls: Type,
              args: Optional[List[Any]] = None, kwargs: Optional[Dict[str, Any]] = None):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    game = game_cls(*args, **kwargs)
    game.play()

    while True:
        first = game.num_attempts == 0
        accepted = game.new_attempt(first_guesses[0] if first else candidates[0])
        if not accepted:
            if first:
                del first_guesses[0]
            else:
                del candidates[0]
            continue

        if game.is_finished():
            if game.is_successful():
                print("YES!!")
            else:
                print("NOOOOOOOOOOOOOOOOO")
            break

        # Game goes on, update candidates
        for letter, must_indices in game.green.items():
            def filter_condition(word: str):
                word = decode(word)
                for idx in must_indices:
                    if word[idx] != letter:
                        return False
                return True

            candidates = [word for word in candidates if filter_condition(word)]

        for letter in game.black:
            candidates = [word for word in candidates if letter not in decode(word)]

        for letter, prohibited_indices in game.yellow.items():
            def filter_condition(word: str):
                word = decode(word)
                if letter not in word:
                    return False
                for idx in prohibited_indices:
                    if word[idx] == letter:
                        return False
                return True

            candidates = [word for word in candidates if filter_condition(word)]

    # Finished
    result = game.close()
    return result


def test_words():
    words_to_test = ["avena", "pieza", "cañón", "rubia", "razón", "robot", "fiera", "crack", "épico"]

    word_list = RaeCorpusProvider().get_words()
    word_unique = list(dict.fromkeys(word_list))

    words_sorted_by_vowels = sorted(word_list, key=lambda w: number_vowels(w), reverse=True)
    candidates = list(word_unique)

    for word in words_to_test:
        print("Solución:", word)
        result = play_game(words_sorted_by_vowels, candidates, SimulatedGame, kwargs={"word": word})
        print(result)
        print()


def run_bot():
    word_list = RaeCorpusProvider().get_words()
    word_unique = list(dict.fromkeys(word_list))
    words_sorted_by_vowels = sorted(word_list, key=lambda w: number_vowels(w), reverse=True)
    candidates = list(word_unique)

    result = play_game(words_sorted_by_vowels, candidates, WebGame)
    print(result)


if __name__ == '__main__':
    test_words()
    run_bot()
