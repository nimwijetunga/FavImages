# FavImages

## Hosted

google.com

## Descrption

Application that allows users to create a repository of their favourite images

## Features (User Facing)

 - Fully functional authentication system that allows users to create accounts
 - Ability to add images and view images that others have uploaded
 - Ability to favourite certain images
 - Ability to search images by their title or description
 - Swagger API for ease of communication between the User and the backend

## Features (Technical)

 - Secure <b> JSON Web Token authentiation </b> system with password encryption
 - Scalable backend server placed behind a <b> Nginx round robin load balancer </b>
 - Scalable <b> ElasticSearch cluster </b> to search image titles/descriptions
 - <b> Redis caching layer </b> which sits infront of a PostgresDB allowing for low latency data reterival
 - <b> Kafka queue </b> which has a python producer and will write to the Elasticsearch consumer

## Running Locally
