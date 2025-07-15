export function connectToSignalingServer(roomId: string): Promise<WebSocket> {
  return new Promise((resolve, reject) => {
    console.log(`Attempting to connect to signaling server for room ${roomId}`);
    const ws = new WebSocket('ws://localhost:8080');

    const timeout = setTimeout(() => {
      console.error('Signaling server connection timed out');
      reject(new Error('Signaling server connection timed out'));
    }, 5000);

    ws.onopen = () => {
      console.log(`Successfully connected to signaling server for room ${roomId}`);
      clearTimeout(timeout);
      resolve(ws);
    };

    ws.onerror = (error) => {
      console.error('Signaling server connection error:', error);
      clearTimeout(timeout);
      reject(new Error('Failed to connect to signaling server'));
    };

    ws.onclose = (event) => {
      console.log(`Signaling server connection closed: code=${event.code}, reason=${event.reason}`);
      clearTimeout(timeout);
      reject(new Error(`Signaling server connection closed unexpectedly: ${event.reason || 'Unknown reason'}`));
    };
  });
}