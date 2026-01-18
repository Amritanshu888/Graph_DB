#!/usr/bin/env python
# coding: utf-8

# ### Build a Question Answering application over a Graph Database

# - Initialize the variables u downloaded while creating a free instance from Neo4j

# In[1]:


NEO4J_URI = "neo4j+s://a6208d63.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "rnl7AXFxrALS17r_57UEZ-VKjzuNlsMkyVlPwZyd4Z0"
## U can also put these in the environment varaible if u want and probably read from those environment variables


# In[2]:


import os
## Setting up the environment variables
os.environ["NEO4J_URI"] = NEO4J_URI
os.environ["NEO4J_USERNAME"] = NEO4J_USERNAME
os.environ["NEO4J_PASSWORD"] = NEO4J_PASSWORD


# In[3]:


from langchain_community.graphs import Neo4jGraph
## Neo4jGraph actually helps u to connect to ur db with the help of the information which u have i.e. NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)
## This way also we will be able to initialize our graph, which will be basically connected to ur entire database
graph


# In[4]:


## Dataset Movie
URL = "https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv"
## Above is the RAW Data URL
movie_query = """
LOAD CSV WITH HEADERS FROM
'https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv' as row

MERGE(m:Movie{id:row.movieId})
SET m.released = date(row.released),
    m.title = row.title,
    m.imdbRating = toFloat(row.imdbRating)
FOREACH (director in split(row.director, '|') |
    MERGE (p:Person {name:trim(director)})
    MERGE (p)-[:DIRECTED]->(m))
FOREACH (actor in split(row.actors, '|') |
    MERGE (p:Person {name:trim(actor)})
    MERGE (p)-[:ACTED_IN]->(m))
FOREACH (genre in split(row.genres, '|') |
    MERGE (g:Genre {name:trim(genre)})
    MERGE (m)-[:IN_GENRE]->(g))    
"""
## We will be putting all the directors in the person node itself
## Above we have used SET keyword to assign property to the variables
## Above using for each loop we have created multiple relationships: person to movie, actor to movie, movie to genre
## This is the query to probably load this entire dataset


# In[5]:


movie_query


# In[ ]:


graph.query(movie_query)  ## This is how we execute the query we have specified above


# In[ ]:


graph.refresh_schema() ## Refreshing the graph schema
print(graph.schema)  ## It will show all the Node properties and all the Relationship properties


# - Now since u have used the credentials u downloaded for that particular instance in neo4j auradb, u will be able to view it(the graph, nodes, relationships and data) in the Neo4jAuraDB when u try to refresh it.

# - To insert this entire data we just used graph.query() function --> And this executed the entire query itself inside the graph database.

# In[29]:


import os
from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")


# In[30]:


from langchain_groq import ChatGroq
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
llm


# - Our plan was whenever user writes the query it should probably go to the LLM model this LLM model should create my Cypher Query, and then further by using this cypher query we should be able to query from my graph database and get the output and along with the output i should be able to get back the response.

# In[31]:


from langchain.chains import GraphCypherQAChain
chain = GraphCypherQAChain.from_llm(graph=graph, llm=llm, allow_dangerous_requests=True, cypher_validation=True, verbose=True)
## Bcoz of verbose = True i will be able to see that how the conversation is happening.
chain


# - Prompt template over here by default, in this GraphCypherQAChain i do not have to seperately specify my prompt template, bcoz if u go forward there is a prompt template and it is internally using this llm chain. As per this prompt template i need to pass question and schema.
# - With GraphCypherQAChain it has a default prompt generated along with this.

# In[33]:


response = chain.invoke({"query":"Who was the director of the movie Casino"})
response


# - Query: MATCH (m:Movie {title:"Casino"})<-[:DIRECTED]-(p:Person) RETURN p.name

# In[ ]:


response = chain.invoke({"query":"Who were the actors of the movie Casino"})
response
## Note: Along with the output it is being able to generate the full context.


# In[43]:


response = chain.invoke({"query":"How many artists are there?"})
response


# In[44]:


response = chain.invoke({"query":"How many movies has Tom Hanks acted in?"})
response


# ## Prompting Statergies GraphDB With LLM
# - Earlier with the help of LLM's we were creating our entire Cypher Queries and based on that we were executing it and retrieving the results from the Graph Database.
# - There may be scenarios where the LLM may not perform well w.r.t different different complex kind of queries so it is better that we try to improve this graph database query generation mechanism.
# - Now here what we will do is that we will go with some proper prompting statergies which will try to improve the Graph Database Query Generation.
# - We will largely focus on methods for getting the relevant database specific information in ur prompt.
