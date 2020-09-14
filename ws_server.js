const fs = require('fs');
const https = require('https');
const WebSocket = require('ws');

const server = https.createServer({
  cert: fs.readFileSync('./cert.pem'),
  key: fs.readFileSync('./key.pem')
});
const wss = new WebSocket.Server({ 
    server,
    perMessageDeflate: {
        zlibDeflateOptions: {
          // See zlib defaults.
          chunkSize: 1024,
          memLevel: 7,
          level: 3
        },
        zlibInflateOptions: {
          chunkSize: 10 * 1024
        },
        // Other options settable:
        clientNoContextTakeover: true, // Defaults to negotiated value.
        serverNoContextTakeover: true, // Defaults to negotiated value.
        serverMaxWindowBits: 10, // Defaults to negotiated value.
        // Below options specified as default values.
        concurrencyLimit: 10, // Limits zlib concurrency for perf.
        threshold: 1024 // Size (in bytes) below which messages
        // should not be compressed.
    }
});

console.log('Server listen :')

var locks = [];
var locksID = [];

wss.on('connection', function connection(ws) {
  ws.on('message', function incoming(ref) {
    console.log('Received: %s', ref);
    locksID.push(ref)
    // OpenDoor(ref)
    // CloseDoor(ref)
    // ws.send('azefrg')
  });
  ws.send('Connected to JS server. Listening:')
  locks.push(ws)
});

function OpenDoor(ref){
  for (lock in locksID){
    if(locksID[lock] === ref){
      locks[lock].send(ref + ' open')
    }
  }
}

function CloseDoor(ref){
  for (lock in locksID){
    if(locksID[lock] === ref){
      locks[lock].send(ref + ' close')
    }
  }
}

wss.on('close', function deconnection(ws){
    ws.on('message', function incoming(message){
        console.log('Received: %s', message);
    })
    ws.send('Bye!')
})

server.listen(8080);