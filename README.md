<div align="center">
  <img src="/assets/pics/svg/Logo _ foxy.svg" alt="Логотип проекта" width="200"/>
  
  # Akiora

  
</div>


## About

League of Legends platform 

## Build
To build it on Linux with docker run this -> \
```console
touch .env && cat .env_example >> .env && \
mkdir -p ./docker_volumes/mongo_init && \
touch ./docker_volumes/mongo_init/init-mongo.js && \
cat init-mongo-example.js >> ./docker_volumes/mongo_init/init-mongo.js && \
docker-compose up --build -d
```
## Services map
- localhost:8000 - **ORM**

