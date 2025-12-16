import { WEB_SOCKET_URL } from '../config/settings';

class AuctionWebSocket {
  constructor(auctionId, token) {
    this.auctionId = auctionId;
    this.token = token;
    this.socket = null;
    this.onUpdateCallback = null;
    this.onErrorCallback = null;
    this.onConnectCallback = null;
    this.onDisconnectCallback = null;
    this.onBidSuccessCallback = null;
  }

  connect() {
    return new Promise((resolve, reject) => {
      const url = `${WEB_SOCKET_URL}/${this.auctionId}/?token=${this.token}`;

      try {
        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
          console.log('WebSocket connected');
          if (this.onConnectCallback) {
            this.onConnectCallback();
          }
        };

        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

            // Handle initial connection data
            if (data.type === 'auction_update' || data.title) {
              const auctionData = data.data || data;
              if (this.onUpdateCallback) {
                this.onUpdateCallback(auctionData);
              }
              // Resolve on first message (initial data)
              resolve(auctionData);
            }

            // Handle bid response
            if (data.success) {
              console.log('Bid success:', data.success);
              if (this.onBidSuccessCallback) {
                this.onBidSuccessCallback(data.success);
              }
            }
            if (data.error) {
              console.error('Bid error:', data.error);
              if (this.onErrorCallback) {
                // Format error message properly (handle string, array, or object)
                let errorMessage = data.error;
                if (Array.isArray(errorMessage)) {
                  errorMessage = errorMessage.join(' ');
                } else if (typeof errorMessage === 'object') {
                  errorMessage = Object.values(errorMessage).flat().join(' ');
                }
                this.onErrorCallback(errorMessage);
              }
            }
          } catch (e) {
            console.error('Error parsing WebSocket message:', e);
          }
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          if (this.onErrorCallback) {
            this.onErrorCallback('Connection error');
          }
          reject(error);
        };

        this.socket.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          if (this.onDisconnectCallback) {
            this.onDisconnectCallback();
          }
        };
      } catch (error) {
        console.error('Error creating WebSocket:', error);
        reject(error);
      }
    });
  }

  sendBid(price) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        action: 'place_bid',
        price: price.toString(),
      }));
      return true;
    }
    return false;
  }

  onUpdate(callback) {
    this.onUpdateCallback = callback;
  }

  onError(callback) {
    this.onErrorCallback = callback;
  }

  onConnect(callback) {
    this.onConnectCallback = callback;
  }

  onDisconnect(callback) {
    this.onDisconnectCallback = callback;
  }

  onBidSuccess(callback) {
    this.onBidSuccessCallback = callback;
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  isConnected() {
    return this.socket && this.socket.readyState === WebSocket.OPEN;
  }
}

export default AuctionWebSocket;
