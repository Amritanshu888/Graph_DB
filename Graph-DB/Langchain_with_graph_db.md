## Langchain With Graph DB
- Plan:
- If a user queries or let's say if a user is querying anything, now w.r.t this specific query this will probably initially go to our LLMs/LLM model, now this LLM model what it should be doing is that it should be creating my Cypher Query.
- Let's say if i go ahead and say who is this particular person who is acting in this particular movie if i ask that question to my LLM, my LLM should be able to create my Cypher Query.
- Now once i get my Cypher Query it should be able to probably query from our graph db database and once it is able to query it should probably get the response from this and give it to my LLM model and based on our prompt it should be able to give our output response.
- This is the entire thing that we are specifically going to create.
- If i consider this block where we are specifically using LLM, Cypher Query, Graph DB ---> This block is specifically called as Graph Agent.
- Here instead of only generating cypher query we are also going to use a graph db and we are going to query the graph db w.r.t this specific query the user is putting and once we get the output we should basically be able to combine with the prompt, along with my LLM model and get my output response.