import os
import nltk
import math


DOC_BASE = "./Backend/Collection/"
STOP_WORDS = None
REG_EXPRESSION = None
INVERSED_FILE = None
INVERSED_FILE_OF_PONDERATON = None

def InitEngine():
    global STOP_WORDS
    global REG_EXPRESSION
    global INVERSED_FILE
    global INVERSED_FILE_OF_PONDERATON
    nltk.download('stopwords')
    STOP_WORDS = nltk.corpus.stopwords.words('english')
    REG_EXPRESSION = nltk.RegexpTokenizer("(?:A-Za-z]\.)+|\d+(?:\.\d+)?%?|\w+(?:\-\w+)*")
    INVERSED_FILE = CreateInversedFile()
    INVERSED_FILE_OF_PONDERATON = CreateCustomInversedFile("ponderation")
    return 

def CreateWordList(document):
    global STOP_WORDS
    global REG_EXPRESSION

    if (STOP_WORDS == None or REG_EXPRESSION == None):
        InitEngine()

    words_list = REG_EXPRESSION.tokenize(document)
    ##Stremming
    words_list = [nltk.PorterStemmer().stem(word) for word in words_list]
    ##remove stopwords
    words_list = [word for word in words_list if word.lower() not in STOP_WORDS]

    return words_list

def DocumentDictionary(Docname):
    file = open(f"{DOC_BASE}/{Docname}","r")
    document = file.read()
    words_list = CreateWordList(document)
    doc_dictionary = {}
    for word in words_list:
        if(word in doc_dictionary.keys()):
            doc_dictionary[word] += 1
        else:
            doc_dictionary[word] = 1
    
    return doc_dictionary

def CreateInversedFile():
    Documents = os.listdir(DOC_BASE)
    documents_dictionaries = {}
    for document in Documents:
        documents_dictionaries[document] = DocumentDictionary(document)
    return documents_dictionaries

def Calculate_Ponderation(word_results_in_documents,index):
    if (word_results_in_documents["NB_DOCS_FOUND"] == 0):
        return 0
    else:
        return (word_results_in_documents["FREQ"][index]/word_results_in_documents["MAX_FREQ"][index])* math.log((len(word_results_in_documents["DOCS"])/word_results_in_documents["NB_DOCS_FOUND"])+1, 10)

def WordSearch(word,inversed_file,tokenize):
    search_results = {}
    tokens = None
    if (tokenize == False):
        tokens = list(word.split(" "))
    else:
        tokens = CreateWordList(word)
    for token in tokens:
        word_results_in_documents = {}
        word_results_in_documents["DOCS"] = []
        word_results_in_documents["FREQ"] = []
        word_results_in_documents["NB_DOCS_FOUND"]=0
        word_results_in_documents["PONDERATION"] = []
        word_results_in_documents["MAX_FREQ"] = []
        for index in inversed_file:
            doc_dictionary = inversed_file[index]
            freq = 0
            if(token in doc_dictionary.keys()):   
                freq = doc_dictionary[token]
                word_results_in_documents["NB_DOCS_FOUND"] += 1
            word_results_in_documents["MAX_FREQ"].append(max(doc_dictionary.values()))             
            word_results_in_documents["DOCS"].append(index)
            word_results_in_documents["FREQ"].append(freq)

        for index in range(len(word_results_in_documents["DOCS"])):
            word_results_in_documents["PONDERATION"].append(Calculate_Ponderation(word_results_in_documents,index))
        
        search_results[token] = word_results_in_documents   

    return search_results

def CreateCustomInversedFile(method="ponderation"):
    global INVERSED_FILE
    custom_inversed_file = {}
    if (INVERSED_FILE == None):
        InitEngine()
    if (method == "ponderation"):
        doc_index = 0
        for doc_dic in INVERSED_FILE.keys():
            old_document_dictionary = INVERSED_FILE[doc_dic]
            new_document_dictionary = {}
            for term in old_document_dictionary.keys():
                new_document_dictionary[term] = list(dict(WordSearch(term,INVERSED_FILE,False)[str(term)])["PONDERATION"])[doc_index]
            custom_inversed_file[doc_dic] = new_document_dictionary
            doc_index += 1
        return custom_inversed_file

def TermWeightInDocument(document,term):
    global INVERSED_FILE_OF_PONDERATON
    if(term in INVERSED_FILE_OF_PONDERATON[document].keys()):
        return INVERSED_FILE_OF_PONDERATON[document][term]
    return 0

def TermWeightInQuery(document,term):
    if(TermWeightInDocument(document,term) == 0):
        return 0
    return 1

def InternalMultiplicationRelevence(doc,query_terms):
    global INVERSED_FILE_OF_PONDERATON
    sum_ponderation = 0
    for term in query_terms:
        if(term in INVERSED_FILE_OF_PONDERATON[doc].keys()):
            sum_ponderation += TermWeightInDocument(doc,term) * TermWeightInQuery(doc,term)
    return sum_ponderation

def DiceCoeff(doc,query_terms):
    global INVERSED_FILE_OF_PONDERATON
    sum_ponderation = 0
    sum_squared_ponderation = 0
    sum_squared_query_ponderation = 0
    for term in query_terms:
        if(term in INVERSED_FILE_OF_PONDERATON[doc].keys()):
            sum_ponderation += TermWeightInDocument(doc,term) * TermWeightInQuery(doc,term)
            sum_squared_ponderation += math.pow(TermWeightInDocument(doc,term),2)
            sum_squared_query_ponderation += math.pow(TermWeightInQuery(doc,term),2)
    return (2*sum_ponderation)/(sum_squared_ponderation + sum_squared_query_ponderation)

def Cosinus(doc,query_terms):
    global INVERSED_FILE_OF_PONDERATON
    sum_ponderation = 0
    sum_squared_ponderation = 0
    sum_squared_query_ponderation = 0
    for term in query_terms:
        if(term in INVERSED_FILE_OF_PONDERATON[doc].keys()):
            sum_ponderation += TermWeightInDocument(doc,term) * TermWeightInQuery(doc,term)
            sum_squared_ponderation += math.pow(TermWeightInDocument(doc,term),2)
            sum_squared_query_ponderation += math.pow(TermWeightInQuery(doc,term),2)
    return (sum_ponderation)/(math.sqrt(sum_squared_ponderation * sum_squared_query_ponderation))

def Jackard(doc,query_terms):
    global INVERSED_FILE_OF_PONDERATON
    sum_ponderation = 0
    sum_squared_ponderation = 0
    sum_squared_query_ponderation = 0
    for term in query_terms:
        if(term in INVERSED_FILE_OF_PONDERATON[doc].keys()):
            sum_ponderation += TermWeightInDocument(doc,term) * TermWeightInQuery(doc,term)
            sum_squared_ponderation += math.pow(TermWeightInDocument(doc,term),2)
            sum_squared_query_ponderation += math.pow(TermWeightInQuery(doc,term),2)
    return (sum_ponderation)/(sum_squared_ponderation + sum_squared_query_ponderation - sum_ponderation)

def CalculateRelevence(query_terms,method):

    global INVERSED_FILE_OF_PONDERATON
    relevence = {}
    relevence["DOCS"] = list(INVERSED_FILE_OF_PONDERATON.keys())
    relevence["RELEVENCE"] = []

    if (method == "internal multiplication"):
        for doc in relevence["DOCS"]:
            relevence_value = InternalMultiplicationRelevence(doc,query_terms)
            relevence["RELEVENCE"].append(relevence_value)
    
    if (method == "dice coeff"):
        for doc in relevence["DOCS"]:
            relevence_value = DiceCoeff(doc,query_terms)
            relevence["RELEVENCE"].append(relevence_value)

    if (method == "cosinus"):
        for doc in relevence["DOCS"]:
            relevence_value = Cosinus(doc,query_terms)
            relevence["RELEVENCE"].append(relevence_value)
        
    if (method == "jackard"):
        for doc in relevence["DOCS"]:
            relevence_value = Jackard(doc,query_terms)
            relevence["RELEVENCE"].append(relevence_value)
            
    ##SORT RELEVENCE
    Z = list(zip(*(sorted(zip(relevence["RELEVENCE"],relevence["DOCS"]),reverse=True))))
    relevence["RELEVENCE"] = Z[0]
    relevence["DOCS"] = Z[1]
    return relevence

