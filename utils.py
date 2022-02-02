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

wordle_past_words = ["coche", "nieve", "hueso", "titan", "flujo", "disco", "razon", "mural", "abril",
                     "vejez", "falso", "cañon", "obeso", "metal", "avena", "rubia", "pieza", "cuero",
                     "noche", "bingo", "corto", "multa", "nieto", "dieta", "mosca", "nadal", "líder",
                     "cerco"]


def decode(word: str) -> str:
    return (word.replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("ü", "u"))


def is_vowel(c: str) -> bool:
    assert len(c) == 1
    c = decode(c)
    vowels = ["a", "e", "i", "o", "u"]
    return c in vowels


def number_vowels(word: str, unique: bool = True) -> int:
    vowels_found = []
    word = decode(word)
    for c in word:
        if is_vowel(c):
            vowels_found.append(c)
    if unique:
        return len(set(vowels_found))
    else:
        return len(vowels_found)


def word_scoring(word: str, weights: Dict[str, float], allow_duplicates: bool = False) -> float:
    chars = list(decode(word))
    if not allow_duplicates:
        chars = list(set(chars))
    score = 0
    for c in chars:
        if c in weights:
            score += weights[c]
    return score
