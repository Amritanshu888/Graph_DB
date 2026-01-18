## Creating Nodes for Users
- LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/krishnaik06/graph-dataset/main/users_social.csv' AS row
- CREATE (:User{userId:toInteger(row.userId),name:row.name,age:toInteger(row.age),city:row.city});  ----> for every row we are creating a user.
- The labels of the node i.e. the name by which each node will be denoted is the name of the user which we have here i.e. name:row.name

## To retrieve the users
- MATCH (n:User) RETURN n LIMIT 25 ----> For previous data that we have

## Delete all the users
- MATCH (n:User) DELETE n

## Creating Nodes for Posts
- LOAD CSV WITH HEADERS From "https://raw.githubusercontent.com/krishnaik06/graph-dataset/main/posts.csv" as row
- MATCH (u:User {userId:toInteger(row.userId)})
- CREATE (u)-[:POSTED]->(:Post{postId:toInteger(row.postId),content:row.content,timestamp:datetime(row.timestamp)});
- Here above 'Post' is the label name.
- User 'u' has the relation with the post label 'Post' and the relation is Posted.

## Retrieve posted details
- MATCH p=()-[:POSTED]->() RETURN p LIMIT 25;

## Creating Relationships
- LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/krishnaik06/graph-dataset/main/relationships.csv" as row
- MATCH (u1:User {userId: toInteger(row.userId1)}), (u2:User {userId: toInteger(row.userId2)})
- CREATE (u1)-[:FRIEND]->(u2)
- CREATE (u1)-[:LIKES]->(u2);
- In relationships.csv we have two user ids so we are matching those two, these are: userId1, userId2

## Retrieve All Users
- MATCH (u:User) RETURN u

## Retrieve All Posts
- MATCH (p:Post) RETURN p;

## Retrieve Friends of a Specific User
- MATCH (u:User {name:'John'})-[:FRIEND]-(f:User) RETURN f.name;
- 'User' is the label over here, we have created this above also.

## Retrieve Posts Made by Friends of a Specific User
- MATCH (u:User{name:'John'})-[:FRIEND]-(f:User)-[:POSTED]->(p:Post) RETURN f.name,p.content;
- This is just like executing nested queries.

## User which likes other user Post
- MATCH(u:User{name:'John'})-[:POSTED]->(p:Post)<-[:LIKES]-(l:User) Return l.name, p.content;
- When u give this kind of direction like how u have given above u are just trying to find out/traversing the relationship between this 'User' and 'Post' and inside this 'Post' u know that u have something called as likes.
- So here we are just going to use a reversed direction, where we are saying this as likes and this is another relationship that we are trying to create.
- This likes will be w.r.t another user label.
- We are finding john has posted a certain post which is being liked by a certain user and then we are returning that user name as well as the post content.

## Count the Number of Friends Each User Has
- MATCH (u:User)-[:FRIEND]-(f:User)
- RETURN u.name, COUNT(f) AS numberOfFriends
- ORDER BY numberOfFriends DESC;