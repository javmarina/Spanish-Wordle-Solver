from typing import Dict

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


def decode(word: str) -> str:
    return (word.replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("ü", "u"))


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
