#!/usr/bin/env python
# coding: utf-8

# In[96]:


NEO4J_URI = "neo4j+s://a6208d63.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "rnl7AXFxrALS17r_57UEZ-VKjzuNlsMkyVlPwZyd4Z0"


# In[97]:


import os
## Setting up the environment variables
os.environ["NEO4J_URI"] = NEO4J_URI
os.environ["NEO4J_USERNAME"] = NEO4J_USERNAME
os.environ["NEO4J_PASSWORD"] = NEO4J_PASSWORD


# In[98]:


from langchain_community.graphs import Neo4jGraph
## Neo4jGraph actually helps u to connect to ur db with the help of the information which u have i.e. NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)
## This way also we will be able to initialize our graph, which will be basically connected to ur entire database
graph


# In[99]:


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


# In[100]:


movie_query


# In[101]:


graph.query(movie_query)  ## This is how we execute the query we have specified above


# In[102]:


graph.refresh_schema() ## Refreshing the graph schema
print(graph.schema)  ## It will show all the Node properties and all the Relationship properties


# ## From the previous notebook we know that using the query we have already inserted the data in the graph database. So now no need to do it again.

# In[103]:


import os
from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
from langchain_groq import ChatGroq
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
llm


# In[104]:


from langchain.chains import GraphCypherQAChain
## It has a parameter which is called as exclude_types=[], let's say u want to specifically exclude some kind of field and do not want to search based on that
## Here i m telling do all the searches by excluding all the "Genre" field
chain = GraphCypherQAChain.from_llm(graph = graph, llm=llm, exclude_types=["Genre"], verbose=True, allow_dangerous_requests=True, cypher_validation=True)
chain


# In[105]:


chain.schema ## It will tell what kind of schema chain is holding


# In[106]:


chain.graph_schema ## It will tell u the schema of the graph


# In[120]:


examples = [
    {
        "question": "How many artists are there?",
        "query": "MATCH (a:Person)-[:ACTED_IN]->(:Movie) RETURN count(DISTINCT a)"
    },
    {
        "question": "Which actors played in the movie Casino?",
        "query": "MATCH (m:Movie {{title: 'Casino'}})<-[:ACTED_IN]-(a) RETURN a.name"
    },
    {
        "question": "How many movies has Tom Hanks acted in?",
        "query": "MATCH (a:Person {{name: 'Tom Hanks'}})-[:ACTED_IN]->(m:Movie) RETURN count(m)"
    },
    {
        "question": "List all the genres of the movie Schindler's List",
        "query": "MATCH (m:Movie {{title: \"Schindler's List\"}})-[:IN_GENRE]->(g:Genre) RETURN g.name"
    },
    {
        "question": "Which actors have worked in movies from both the comedy and action genres?",
        "query": "MATCH (a:Person)-[:ACTED_IN]->(:Movie)-[:IN_GENRE]->(g1:Genre), (a)-[:ACTED_IN]->(:Movie)-[:IN_GENRE]->(g2:Genre) WHERE g1.name = 'Comedy' AND g2.name = 'Action' RETURN DISTINCT a.name"
    },
    {
        "question": "Which directors have made movies with at least three different actors named 'John'?",
        "query": "MATCH (d:Person)-[:DIRECTED]->(m:Movie)<-[:ACTED_IN]-(a:Person) WHERE a.name STARTS WITH 'John' WITH d, COUNT(DISTINCT a) AS JohnsCount WHERE JohnsCount >= 3 RETURN d.name"
    },
    {
        "question": "Identify movies where directors also played a role in the film.",
        "query": "MATCH (p:Person)-[:DIRECTED]->(m:Movie), (p)-[:ACTED_IN]->(m) RETURN m.title, p.name"
    },
    {
        "question": "Find the actor with the highest number of movies in the database.",
        "query": "MATCH (a:Person)-[:ACTED_IN]->(m:Movie) RETURN a.name, COUNT(m) AS movieCount ORDER BY movieCount DESC LIMIT 1"
    }
]


# In[121]:


from langchain_core.prompts import FewShotPromptTemplate,PromptTemplate

example_prompt = PromptTemplate.from_template(
    "User input: {question}\nCypher query: {query}",
)
 ## FewShotPromptTemplate when we give this specific examples, it will consider this
prompt=FewShotPromptTemplate(
    examples=examples[:5], ## Taking top 5 examples from examples above, just like sample of 5 examples
    example_prompt=example_prompt, ## Providing an example prompt from above
    prefix="You are a Neo4j expert. Given an input question,create a syntactically very accurate Cypher query", ## We are creating a prefix, the prefix will say what the LLM model has to do
    suffix="User input: {question}\nCypher query: ",
    input_variables=["question", "schema"] ## Input variables are question and schema
)


# In[122]:


prompt


# In[123]:


print(prompt.format(question="How many artists are there?", schema="foo"))


# In[ ]:


llm
chain=GraphCypherQAChain.from_llm(graph=graph,llm=llm,cypher_prompt=prompt,verbose=True, allow_dangerous_requests=True, cypher_validation=True)
## Here we are also passing cypher_prompt(we didn't passed this earlier when we created a chain), cypher_prompt is my FewShotPromptTemplate prompt
## It is just to give LLM some ideas about how : What kind of Questions we are asking ?? and What kind of cypher query is being generated ??


# In[130]:


chain.invoke("List all the genres of the movie Schindler's List")


# In[125]:


chain.invoke("Which actors played in the movie Casino?")


# In[135]:


chain.invoke("How many movies has Tom Hanks acted in?")


# In[137]:


chain.invoke("How many movies has Tom Hanks acted in, Tell me the number ?")


# In[138]:


chain.invoke("display the actors who acted in multiple movies")


# In[ ]:


chain.invoke("actors who acted in multiple movies")

