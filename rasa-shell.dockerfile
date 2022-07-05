FROM rasa/rasa:3.0.2-full
USER root
RUN python -m spacy download pt_core_news_lg
USER 1001