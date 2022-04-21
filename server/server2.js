var express         = require('express');
var proxy = require('express-http-proxy');
var http = require('http')
var app             = express();
var PORT            = 8080;
var server          = app.listen(PORT,() => console.log(`Listening on ${ PORT }`));
var http = require('http');

const cors = require('cors');

app.use(cors());
app.use(express.static(__dirname + '/index/'));





const fetch = require('node-fetch');


app.get("/interfaces/:ip", (req, res, next) => {
  let ip = req.params.ip;
  (async () => {
    try {
      const response = await fetch(`http://${ip}:7070/interfaces`)
      const json = await response.json()
      res.json(json)
    } catch (error) {
      res.end(error.response);
    }
  })();
});


app.get("/ping/:ip/:address/:interface", (req, res, next) => {
  let ip = req.params.ip;
  let address = req.params.address;
  let interface = req.params.interface;
  (async () => {
    try {
      const response = await fetch(`http://${ip}:7070/ping/${address}/${interface}`)
      const json = await response.json()
      res.json(json)
    } catch (error) {
      res.end(error.response);
    }
  })();
});


app.get("/ping/:ip/:address", (req, res, next) => {
  let ip = req.params.ip;
  let address = req.params.address;
  (async () => {
    try {
      const response = await fetch(`http://${ip}:7070/ping/${address}`)
      const json = await response.json()
      res.json(json)
    } catch (error) {
      res.end(error.response);
    }
  })();
});

app.get("/arp/del/:ip/:address", (req, res, next) => {
  let ip = req.params.ip;
    let address = req.params.address;
  (async () => {
    try {
      const response = await fetch(`http://${ip}:7070/arp/del/${address}`)
      const json = await response.json()
      res.json(json)
    } catch (error) {
      res.end(error.response);
    }
  })();
});

app.get("/arp/add/:ip/:address/:mac", (req, res, next) => {
  let ip = req.params.ip;
  let address = req.params.address;
  let mac = req.params.mac;
  (async () => {
    try {
      const response = await fetch(`http://${ip}:7070/arp/add/${address}/${mac}`)
      const json = await response.json()
      res.json(json)
    } catch (error) {
      res.end(error.response);
    }
  })();
});


app.use('/onos/v1/', proxy('container-onos-sdn-controller:8182/', ))