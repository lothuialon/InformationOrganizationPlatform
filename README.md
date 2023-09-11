# InformationOrganizationPlatform

A text summarization platform. Users can create an account and CRUD folders, notes, keyword extraction and text summarizations. Platform is capable of both extractive and abstractive summarization.

Extractive summarization is implemented with TF-IDF and other parameters such as sentence length, sentence position and keywords included in it. It may be fine tuned further with parameters in the main extractive summarization function.
Abstractive summarization is implemented with a huggingface model.
Flask framework is used to implement the web platform.
