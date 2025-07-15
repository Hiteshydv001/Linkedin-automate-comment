// server/signaling.ts
import { createServer } from 'http';
import WebSocket, { WebSocketServer } from 'ws';
import { v4 as uuidv4 } from 'uuid';

interface Room {
  [roomId: string]: Map<string, WebSocket>;
}

const rooms: Room = {};

// Create an HTTP server
const server = createServer((req, res) => {
  console.log(`HTTP request received: ${req.method} ${req.url}`);
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('WebSocket server running\n');
});

// Attach WebSocket server to the HTTP server
// This automatically handles the 'upgrade' event
const wss = new WebSocketServer({ server });

wss.on('connection', (ws: WebSocket, req) => {
  const clientId = uuidv4();
  console.log(`Client ${clientId} connected via WebSocket from ${req.url}`);

  ws.on('message', (message: string) => {
    console.log(`Received message from client ${clientId}: ${message}`);
    try {
      const data = JSON.parse(message);

      switch (data.type) {
        case 'join':
          const { roomId, peerId } = data;
          if (!roomId || !peerId) {
            ws.send(JSON.stringify({ type: 'error', message: 'Missing roomId or peerId' }));
            return;
          }

          if (!rooms[roomId]) {
            rooms[roomId] = new Map();
          }

          rooms[roomId].set(peerId, ws);

          // Notify all other peers in the room
          rooms[roomId].forEach((client, existingPeerId) => {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
              client.send(JSON.stringify({
                type: 'peerId',
                peerId: peerId,
                roomId,
              }));
            }
            if (existingPeerId !== peerId && ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({
                type: 'peerId',
                peerId: existingPeerId,
                roomId,
              }));
            }
          });
          break;

        case 'offer':
        case 'answer':
        case 'ice-candidate':
          const { roomId: targetRoomId, targetPeerId } = data;
          if (!targetRoomId || !targetPeerId) {
            ws.send(JSON.stringify({ type: 'error', message: 'Missing roomId or targetPeerId' }));
            return;
          }
          const room = rooms[targetRoomId];
          if (room) {
            const targetClient = room.get(targetPeerId);
            if (targetClient && targetClient.readyState === WebSocket.OPEN) {
              targetClient.send(JSON.stringify(data));
            } else {
              console.log(`Target peer ${targetPeerId} not found in room ${targetRoomId}`);
            }
          } else {
            console.log(`Room ${targetRoomId} not found`);
          }
          break;

        default:
          ws.send(JSON.stringify({ type: 'error', message: 'Unknown message type' }));
      }
    } catch (error) {
      console.error(`Error processing message from client ${clientId}:`, error);
      ws.send(JSON.stringify({ type: 'error', message: 'Invalid message format' }));
    }
  });

  ws.on('close', () => {
    for (const roomId in rooms) {
      const room = rooms[roomId];
      room.forEach((client, peerId) => {
        if (client === ws) {
          room.delete(peerId);
        }
      });
      if (room.size === 0) {
        delete rooms[roomId];
      }
    }
    console.log(`Client ${clientId} disconnected`);
  });

  ws.on('error', (error) => {
    console.error(`WebSocket error for client ${clientId}:`, error);
  });
});

wss.on('error', (error) => {
  console.error('WebSocket server error:', error);
});

// Start the HTTP server on port 8080
server.listen(8080, () => {
  console.log('Signaling server running on ws://localhost:8080');
});