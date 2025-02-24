import os
from argparse import ArgumentParser
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker
import re

import textmine.utils.constants as constants
import textmine.utils.custom_list_utils as list_utils
from unidecode import unidecode
from nltk.corpus import stopwords as sw


def load_yt_comments(filename):
    comments = list_utils.read(filename)
    return list_utils.flatten(comments)


def clean_comments(input_filename=None,
                   input_directory=None,
                   save_loc="./",
                   convert_to_ascii=False,
                   remove_line_breaks=False,
                   remove_punctuation=False,
                   lower=False,
                   remove_numbers=False,
                   spell_check=False,
                   remove_stopwords=False,
                   stem=False,
                   lemmatize=False,
                   custom_stopwords_=None):


    if not input_filename and not input_directory:
        raise ValueError("Either input_filename or input_directory must be provided.")

    if input_filename:
        files = [input_filename]
    else:
        all_files = os.listdir(input_directory)
        files = [os.path.join(input_directory, file) for file in all_files]

    for file in files:
        process_string = ""
        yt_comments = load_yt_comments(file)

        # Convert all characters to ASCII
        if convert_to_ascii:
            process_string += "a"
            yt_comments = [unidecode(comment) for comment in yt_comments]

        # Remove line breaks
        if remove_line_breaks:
            process_string += "b"
            yt_comments = [comment
                              .replace("\n", " ")
                              .replace("\r", " ")
                              .replace("\r\n", " ")
                              for comment in yt_comments]

        # Remove punctuation
        if remove_punctuation:
            print("Removing punctuation")
            process_string += "p"
            for i, comment in enumerate(yt_comments):
                yt_comments[i] = "".join(str(ch) for ch in comment if ch not in constants.PUNCTUATION)

        # Convert to lowercase
        if lower:
            print("Lower")
            process_string += "l"
            yt_comments = [comment.lower() for comment in yt_comments]

        # Remove numbers
        if remove_numbers:
            print("Removing numbers")

            process_string += "n"
            yt_comments = [re.sub(r"[0-9]", "", comment) for comment in yt_comments]

        # Spell check
        if spell_check:
            print("Spell check")

            process_string += "s"
            spell = SpellChecker()
            for i, comment in enumerate(yt_comments):
                comment = comment.split(" ")
                new_comment = [spell.correction(word) for word in comment]
                comment = [orig if corr is None else corr for (corr, orig) in zip(new_comment, comment)]
                yt_comments[i] = " ".join(comment)

        # Remove stopwords, either custom or according to nltk toolkit stopwords
        if remove_stopwords:
            print("Removing stop words")
            process_string += "w"
            if not custom_stopwords_:
                custom_stopwords_ = sw.words("english")
            for i, comment in enumerate(yt_comments):
                comment = comment.split(" ")
                comment = [word for word in comment if word.lower() not in custom_stopwords_]
                yt_comments[i] = " ".join(comment)

        # Stem words
        if stem:
            print("Stemming")
            process_string += "S"
            stemmer = PorterStemmer()
            for i, comment in enumerate(yt_comments):
                comment = comment.split(" ")
                comment = [stemmer.stem(word) for word in comment]
                yt_comments[i] = " ".join(comment)

        # Lemmatize words
        if lemmatize:
            print("lemming")
            process_string += "L"
            lemmer = WordNetLemmatizer()
            for i, comment in enumerate(yt_comments):
                comment = comment.split(" ")
                comment = [lemmer.lemmatize(word) for word in comment]
                yt_comments[i] = " ".join(comment)

        if len(process_string) > 0:
            process_string += "_"
            full_file_path = os.path.join(save_loc, process_string + os.path.split(file)[1])
            yt_comments = list_utils.single_to_multi(yt_comments)
            list_utils.write(yt_comments, full_file_path)
        else:
            print("none")
            continue


if __name__ == "__main__":
    parser = ArgumentParser(prog="Clean Text",
                            description="Clean a set of text comments. The comments should be in a CSV file format."
                                        "")

    parser.add_argument("--input_file", "-i",
                        help="The CSV file containing the comments to clean. If this is not passed, then --input_dir "
                             "(-d) must be passed.")
    parser.add_argument("--input_dir", "-I",
                        help="A directory containing multiple csv files to clean. There can be no other files in the "
                             "directory besides CSV files to clean. If this is not passed, then --input_file (-i) must "
                             "be passed.")
    parser.add_argument("--save_dir", "-D",
                        default="./",
                        help="The directory where the file will be saved. The filename will match the input file name "
                             "with a string of letters prepended to it. The letter code is described in the description"
                             "of this CLI function. Defaults to current directory")
    parser.add_argument("--convert_to_ascii", "-a",
                        action="store_true",
                        help="Convert all characters to ASCII. Add the letter 'a' to the prepended filename string.")
    parser.add_argument("--remove_line_breaks", "-b",
                        action="store_true",
                        help="Remove all line breaks. Add the letter 'b' to the prepended filename string.")
    parser.add_argument("--remove_punctuation", "-p",
                        action="store_true",
                        help="Remove all punctuation. Add the letter 'p' to the prepended filename string.")
    parser.add_argument("--lowercase", "-l",
                        action="store_true",
                        help="Make all letters lowercase. Add the lowercase letter 'l' to the prepended filename "
                             "string. Not to be confused with 'L' for lemmatize.")
    parser.add_argument("--remove_numbers", "-n",
                        action="store_true",
                        help="Remove all numbers from the text. Add the letter 'n' to the prepended filename string.")
    parser.add_argument("--spell_check", "-s",
                        action="store_true",
                        help="Spell check. Add the lowercase letter 's' to the prepended filename string. Not to be "
                             "confused with 'S' for stemmer.")
    parser.add_argument("--remove_stopwords", "-w",
                        action="store_true",
                        help="Remove stopwords from the text. Add the letter 'w' to the prepended filename string. A "
                             "text file containing a comma separated list of stop words can be passed via the "
                             "--custom_stopwords (-c) argument. If nothing is passed, the stopwords from the python "
                             "nltk toolkit will be utilized.")
    parser.add_argument("--stem", "-S",
                        action="store_true",
                        help="Stem all words using the nltk toolkit PorterStemmer. Add the capital letter 'S' to the "
                             "prepended filename string. Not to be confused with 's' for spell check.")
    parser.add_argument("--lemmatize", "-L",
                        action="store_true",
                        help="Lemmatize all words using the nltk tookit WordNetLemmatizer. Add the capital letter 'L' "
                             "to the prepended filename string. Not to be confused with 'l' for lowercase.")
    parser.add_argument("--custom_stop_words", "-W",
                        help="A string of comma-separated stop words. If --stop_words_file_path (-f) is passed, "
                             "a file path may be passed to this argument.")
    parser.add_argument("--stop_words_file_path", "-f",
                        action="store_true",
                        help="A file was passed to --custom_stop_words (-W). Ignored in --custom_stop_words (-W) is "
                             "omitted.")

    # Parse and perform checks
    args = parser.parse_args()
    if not args.input_file and not args.input_dir:
        parser.error("Either --input_file (-I) or --input_dir (-D) must be provided.")

    custom_stopwords = args.custom_stop_words
    if custom_stopwords is not None:
        if args.stop_words_file_path:
            with open(custom_stopwords, "r") as f:
                custom_stopwords = f.read()

    clean_comments(args.input_file,
                   args.input_dir,
                   args.save_dir,
                   args.convert_to_ascii,
                   args.remove_line_breaks,
                   args.remove_punctuation,
                   args.lowercase,
                   args.remove_numbers,
                   args.spell_check,
                   args.remove_stopwords,
                   args.stem,
                   args.lemmatize,
                   custom_stopwords)
