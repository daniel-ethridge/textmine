import csv
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

def create_word_cloud(filename, directory_passed=False):

    file_list = []
    if directory_passed:
        for file in os.listdir(filename):
            file_list.append(os.path.join(filename, file))
    else:
        file_list.append(filename)

    for file in file_list:
        comments = []
        with open(file, "r") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                comments.append(row)

        rem_words = ["just", "dont", "song", "im", "like", "having", "things", "going"]

        comments = [comment for sublist in comments for comment in sublist]
        red_comments = []

        for comment in comments:
            word_list = comment.split(" ")
            word_list_ = [word for word in word_list if word not in rem_words]
            red_comments.append(" ".join(word_list_))

        count_v = CountVectorizer(input="content", stop_words="english", ngram_range=(2, 3))

        comment_arr = count_v.fit_transform(red_comments).toarray()
        word_frame = pd.DataFrame(comment_arr, columns = count_v.get_feature_names_out())
        summed_frame = word_frame.sum(axis=0, numeric_only=True)

        wordcloud = WordCloud().generate_from_frequencies(summed_frame)
        plt.title(file)
        plt.imshow(wordcloud)
        plt.show()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--filename')
    parser.add_argument('-d', '--dirname')

    args = parser.parse_args()
    if args.filename and args.dirname:
        args.dirname = None
        print("Both directory and filename passed. Defaulting to file only.")

    if args.filename:
        create_word_cloud(args.filename)
    elif args.dirname:
        create_word_cloud(args.dirname, True)
    else:
        print("Nothing passed. Exiting.")
