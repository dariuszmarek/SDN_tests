var express         = require('express');
var proxy = require('express-http-proxy');
var app             = express();
var PORT            = 8080;
var server          = app.listen(PORT,() => console.log(`Listening on ${ PORT }`));

const cors = require('cors');

app.use(cors());
app.use(express.static(__dirname + '/index/'));
app.use('/', proxy('container-onos-sdn-controller:8181/', ))

