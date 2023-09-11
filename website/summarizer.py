#from gensim.summarization import summarize
from transformers import pipeline
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import math

    #todo -edit sentence position scoring//done , edit sentence lenght scoring//todo remove super short sentences,
    # change weights, add similarity check//to be changed together with sentence lenght scoring same functionality

def summarize(text, num_sentences, length_weight, position_weight, keyword_weight, keyword_number):


    # Preprocess
    sentences, raw_sentences = preprocess_text(text)
    
    # Calculate the frequency of each word // not used curr


    # Extract Keywords

    important_keywords, their_tfidf = calculate_keywords(sentences, keyword_number)

    # Calculate scores for each sentence

    sentence_scores, raw_sentences_scores = calculate_sentence_scores(sentences, raw_sentences, important_keywords, their_tfidf, length_weight, position_weight, keyword_weight)

    # Sort sentences #todo Calculate sentence similarity and remove them from summary if above threshold

    sentence_scores.sort(key=lambda x: x['score'], reverse=True)
    raw_sentences_scores.sort(key=lambda x: x['score'], reverse=True)

    # Select the top n sentences based on their scores

    summary_sentences = [sentence_scores[i]['sentence'] for i in range(num_sentences)]
    raw_summary_sentences = [raw_sentences_scores[i]['sentence'] for i in range(num_sentences)]

    # Combine the summary

    summary = ' '.join(raw_summary_sentences)
    # Test
    print("Summary scores:")
    for i in range(num_sentences):
        sent_score = raw_sentences_scores[i]['score']
        print(f" Sentence {i}: {sent_score}")
    print(summary)
    return summary


def preprocess_text(text):

    # Tokenize the text into sentences and words
    
    sentences = sent_tokenize(text)
    raw_sentences = sentences
    words = [word_tokenize(sentence.lower()) for sentence in sentences]

    # Remove punctuation and stopwords, and lemmatize the words
    stop_words = set(stopwords.words('english') + list(string.punctuation))
    lemmatizer = WordNetLemmatizer()
    # try without lemmatizer

    words = [[lemmatizer.lemmatize(word) for word in sentence if word not in stop_words] for sentence in words]

    # Convert the words back into sentences
    sentences = [' '.join(sentence) for sentence in words]

    return sentences, raw_sentences


def calculate_keywords(sentences, n):
    # Calculate tf-idf score of each word
    word_frequencies = {}
    tf_idf = {}
    for sentence in sentences:
        words = word_tokenize(sentence)
        for word in words:
            if word not in word_frequencies:
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
        for word in set(words):
            if word not in tf_idf:
                #  logarithm of the ratio between the total number of documents and the number of documents that contain the word.
                num_documents_containing_word = sum([1 for s in sentences if word in word_tokenize(s)])
                tf_idf[word] = math.log(len(sentences) / num_documents_containing_word) * word_frequencies[word] #tf * idf

    # Normalize the TF-IDF scores by dividing each score by the maximum score// score is between 0 and 1
    max_tf_idf = max(tf_idf.values())
    tf_idf = {word: score / max_tf_idf for word, score in tf_idf.items()}

    # Get the top N keywords based on their combined frequency and TF-IDF score
    sorted_word_scores = sorted(tf_idf.items(), key=lambda x: x[1], reverse=True)[:n]
    important_keywords = [word[0] for word in sorted_word_scores]
    tf_idf_scores = {word[0]: word[1] for word in sorted_word_scores}

    return important_keywords, tf_idf_scores



def calculate_sentence_scores(sentences, raw_sentences, important_keywords, their_tfidf, length_weight, position_weight, keyword_weight):
    # Calculate start
    sentence_scores = []
    raw_sentence_score =[]
    num_sentences = len(sentences)

    # Length score: short sentence more score

    longest_sentence_length = max([len(word_tokenize(sentence)) for sentence in sentences])
    length_scores = [1 - (len(word_tokenize(sentence)) / longest_sentence_length) for sentence in sentences]

    # Position score: sentences at the beginning are more important

    #position_scores = [1 - (i / num_sentences) for i in range(num_sentences)]
    position_scores = [abs(i - num_sentences/2)/(num_sentences/2) for i in range(num_sentences)]

    # Keyword score: sentences containing important keywords are more important
    keyword_scores = [0] * num_sentences
    if important_keywords is not None:
        for i, sentence in enumerate(sentences):
            for word in word_tokenize(sentence):
                if word in important_keywords:
                    keyword_scores[i] += their_tfidf[word]

    for i in range(num_sentences):
        sentence_scores.append({
            'sentence': sentences[i],
            'length': length_scores[i],
            'position': position_scores[i],
            'score': length_weight * length_scores[i] + position_weight * position_scores[i]
        })
        raw_sentence_score.append({
            'sentence': raw_sentences[i],
            'length': length_scores[i],
            'position': position_scores[i],
            'score': length_weight * length_scores[i] + position_weight * position_scores[i]
        })

        if important_keywords is not None:
            sentence_scores[i]['keyword'] = keyword_scores[i]
            sentence_scores[i]['score'] += keyword_weight * keyword_scores[i]

        if important_keywords is not None:
            raw_sentence_score[i]['keyword'] = keyword_scores[i]
            raw_sentence_score[i]['score'] += keyword_weight * keyword_scores[i]
        

    return sentence_scores, raw_sentence_score





def abstractiveSummarization(text, desired_word_count):

    # giving preprocessed text 

    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0)
    summary = summarizer(text, min_length=int(desired_word_count-30), max_length=int(desired_word_count+30))

    return summary[0]['summary_text']


def extract_keywords(text, n):
    # Preprocess
    sentences, _ = preprocess_text(text)
    
    # Calculate keywords and their TF-IDF scores
    important_keywords, their_tfidf = calculate_keywords(sentences, n)
    
    
    return important_keywords[:n]