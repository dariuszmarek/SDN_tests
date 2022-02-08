FROM node:latest

WORKDIR /src

COPY server/ ./
COPY /dist/onos-app/* ./index/ 

RUN npm install

EXPOSE 8080
CMD [ "node", "server.js" ]