"""
Copyright (c) 2024 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Joel Jose <joeljos@cisco.com>"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

from getquestions import getquestions
from dochat import dochat
import json
from rank_bm25 import BM25Okapi
import re
from pprint import pprint

with open("data/doc_qa.json","r") as f:
    data = json.load(f)
# Example corpus questions (replace with your actual list)
corpus_questions = getquestions()
# Tokenize the corpus questions for BM25
tokenized_corpus = [re.findall(r'\b\w+\b', question.lower()) for question in corpus_questions]
# Initialize BM25
bm25 = BM25Okapi(tokenized_corpus)

# Function to get adjacent questions based on BM25 similarity score threshold
def find_adjacent_questions_bm25(qlist, bm25, base_question, base_index, threshold=0.3):
    qlist2 = [base_question]  # Include the base question in qlist2
    base_query = base_question.split()  # Tokenize the base question

    # Compute scores for the base question against all questions
    base_scores = bm25.get_scores(base_query)

    # Check the next questions in the corpus
    for i in range(base_index + 1, len(qlist)):
        next_query = qlist[i].split()  # Tokenize the next question
        next_score = bm25.get_scores(next_query)[base_index]  # BM25 score for the next question
        similarity = next_score / max(base_scores[base_index], 1e-6)  # Normalize by base score

        if similarity > threshold:
            qlist2.append(qlist[i])
            # print(f"Similarity between '{base_question}' and '{qlist[i]}': {similarity:.4f}")
        else:
            qlist2.append(qlist[i])  # Add the first question that goes below threshold
            break  # Stop after adding this question

    return qlist2

def dosearch(query_question):
    # Tokenize the query for BM25
    tokenized_query = re.findall(r'\b\w+\b', query_question.lower())

    # Get BM25 scores for the query against the corpus
    scores = bm25.get_scores(tokenized_query)

    # Get indices of top 5 most similar questions
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]

    # Retrieve the most similar questions
    bm25_similar_questions = [corpus_questions[i] for i in top_indices]

    qlist = []
    for q, s in zip(bm25_similar_questions, [scores[i] for i in top_indices]):
        if s > 0:
            #print(f"{q} (BM25 Score: {s:.4f})")
            qlist.append(q)

    print("len of BM25 qlist:", len(qlist))
    print(f"Query: {query_question}, Selected Question List : {qlist}")

    prompt = f"re-order the questions in Qlist based on the similarity of the Query to the questions in the Qlist. Output only the re-ordered list of Qlist in json format. Do not output anything else other than the re-ordered Qlist. Query : {query_question}. Qlist : {qlist}"

    answer = dochat(prompt, json=True)
    qlist = json.loads(answer)["Qlist"]
    print("len of re-ordered qlist:", len(qlist))
    pprint(qlist)
    qlist = qlist[:2] # Limit the number of questions to top 2
    pprint(qlist)

    print("Finding adjacent questions based on similarity...")
    final_qlist = []
    for question in qlist:
        # Find the index of the current question in the corpus
        base_index = corpus_questions.index(question)
        
        qlist2 = find_adjacent_questions_bm25(corpus_questions, bm25, question, base_index)
        
        # Merge qlist2 with final_qlist
        final_qlist = list(set(final_qlist + qlist2))  # Use set to avoid duplicates

    alist=[]
    for item in data:
        if item["question"] in final_qlist:
            alist.append(item["content"])
        if len(alist)==len(final_qlist):
            break
            
    print(f"Query: {query_question}, Selected Question List : {final_qlist}, Context: {str(alist)}, Question + Answer List length : {len(final_qlist) + len(alist)}")

    prompt = f"Answer the query using the provided context. Only use the provided context to answer the query. Try to derive an answer (even if partial) from the given context. Only if you do have an answer at all from the given context, then mention that you do not have the information. Query: {query_question} Context: {str(alist)}"
    print("Prompt:", prompt)
    answer = dochat(prompt)
    return answer


if __name__ == "__main__":

    while True:
        # New sentence (query) you want similar questions for
        query_question = input("Enter your question: ")
        if query_question == "exit":
            break
        answer = dosearch(query_question)
        print("Query:", query_question)
        print("Answer:", answer)

        