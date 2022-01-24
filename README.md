# Spanish Wordle Solver

This repository contains a simple algorithm to automate the Spanish Wordle puzzle. The algorithm is as follows:

1. Download a corpus of Spanish words with usage frequency, and select valid words with 5 letters.
2. Find the word with highest number of unique vowels (currently, it's "audio", with 4 unique vowels).
3. Use the resultof the first attempt to filter list of potential candidates.
4. Try until Wordle is solved, but now prioritizing words with frequent usage instead of focusing on vowels.

The goal of the code is to be as extensible as possible. Thus, it's easy to use other word corpora, and a **simulator** is provided so that any word can be tested, regardless of the word of the day.

## Acknowledgements

Thanks to [__amarqz__](https://github.com/amarqz) and [__RPS98__](https://github.com/RPS98) for the idea and suggestions.