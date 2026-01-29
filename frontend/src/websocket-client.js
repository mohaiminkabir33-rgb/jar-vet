export class WebSocketClient {
    constructor(url = null) {
        const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        
        if (!url) {
            if (isProduction) {
                this.url = `${protocol}//${window.location.hostname.replace('jar-vet', 'jar-vet-backend')}/ws`;
            } else {
                this.url = 'ws://localhost:8000/ws';
            }
        } else {
            this.url = url;
        }
        
        console.log('WebSocket URL:', this.url);
        
        this.ws = null;
        this.reconnectInterval = 3000;
        this.listeners = {};
        this.isConnected = false;
    }

    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(this.url);

                this.ws.onopen = () => {
                    console.log('Connected to JARVIS backend');
                    this.isConnected = true;
                    this.emit('connected', {});
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (e) {
                        console.error('Failed to parse message:', e);
                    }
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.emit('error', error);
                };

                this.ws.onclose = () => {
                    console.log('Disconnected from backend');
                    this.isConnected = false;
                    this.emit('disconnected', {});
                    this.reconnect();
                };

            } catch (error) {
                reject(error);
            }
        });
    }

    reconnect() {
        setTimeout(() => {
            console.log('Attempting to reconnect...');
            this.connect().catch(err => {
                console.error('Reconnection failed:', err);
            });
        }, this.reconnectInterval);
    }

    handleMessage(data) {
        const type = data.type;
        
        switch (type) {
            case 'connection':
                console.log('Connection established:', data.message);
                break;
            
            case 'status':
                this.emit('status', data);
                break;
            
            case 'transcription':
                this.emit('transcription', data);
                break;
            
            case 'intent':
                this.emit('intent', data);
                break;
            
            case 'result':
                this.emit('result', data);
                break;
            
            case 'speech':
                this.emit('speech', data);
                break;
            
            case 'error':
                this.emit('error', data);
                break;
            
            default:
                console.log('Unknown message type:', type, data);
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error('WebSocket not connected');
        }
    }

    sendVoiceCommand(text) {
        this.send({
            type: 'voice_command',
            text: text
        });
    }

    sendTextCommand(text) {
        this.send({
            type: 'text_command',
            text: text
        });
    }

    sendAudioData(audioData) {
        this.send({
            type: 'audio_data',
            audio: audioData
        });
    }

    requestStatus() {
        this.send({
            type: 'status_request'
        });
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }

    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}
