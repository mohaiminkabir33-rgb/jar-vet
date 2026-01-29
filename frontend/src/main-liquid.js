import * as THREE from 'three';
import { gsap } from 'gsap';
import { LiquidOrb } from './liquid-orb.js';
import { WebSocketClient } from './websocket-client.js';
import { SpeechSynthesis } from './speech-synthesis.js';

class LiquidJarvisUI {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true,
            powerPreference: "high-performance",
            stencil: false,
            depth: true,
            logarithmicDepthBuffer: false,
            precision: "highp"
        });
        this.clock = new THREE.Clock();
        
        this.state = 'idle';
        this.isListening = false;
        
        this.wsClient = new WebSocketClient();
        this.tts = new SpeechSynthesis();
        
        this.voiceSettings = {
            rate: 1.1,
            pitch: 1.0,
            volume: 1.0
        };
        
        this.mouse = new THREE.Vector2();
        this.raycaster = new THREE.Raycaster();
        this.isDragging = false;
        this.dragStarted = false;
        this.previousMousePosition = { x: 0, y: 0 };
        this.autoRotate = true;
        
        this.init();
    }

    init() {
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.setClearColor(0x000000, 0);
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.0;
        document.getElementById('canvas-container').appendChild(this.renderer.domElement);

        this.camera.position.z = 5;

        this.setupLights();
        this.orb = new LiquidOrb(this.scene, this.camera, this.renderer);
        
        this.setupEventListeners();
        this.setupWebSocket();
        this.animate();
    }

    setupLights() {
        const ambientLight = new THREE.AmbientLight(0x2E87FF, 0.3);
        this.scene.add(ambientLight);
    }

    setupEventListeners() {
        window.addEventListener('resize', () => this.onWindowResize());
        
        const canvas = this.renderer.domElement;
        const bottomBar = document.getElementById('bottom-bar');
        const closeCard = document.getElementById('close-card');
        const speakerToggle = document.getElementById('speaker-toggle');
        const micIcon = document.getElementById('mic-icon');
        const textInput = document.getElementById('text-input');
        const sendButton = document.getElementById('send-button');
        
        // Orb mouse interactions
        canvas.addEventListener('mousedown', (e) => this.onOrbMouseDown(e));
        canvas.addEventListener('mousemove', (e) => this.onOrbMouseMove(e));
        canvas.addEventListener('mouseup', (e) => this.onOrbMouseUp(e));
        canvas.addEventListener('mouseleave', () => {
            if (this.isDragging) {
                this.isDragging = false;
                this.dragStarted = false;
                document.body.style.cursor = 'default';
                if (this.dragStarted) {
                    setTimeout(() => {
                        this.autoRotate = true;
                    }, 2000);
                }
            }
        });
        
        micIcon.addEventListener('click', (e) => {
            e.stopPropagation();
            this.handleBottomBarClick();
        });
        
        speakerToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleSpeaker();
        });
        
        textInput.addEventListener('focus', () => {
            bottomBar.classList.add('focused');
        });
        
        textInput.addEventListener('blur', () => {
            bottomBar.classList.remove('focused');
        });
        
        textInput.addEventListener('input', (e) => {
            const hasText = e.target.value.trim().length > 0;
            if (hasText) {
                sendButton.classList.add('visible');
            } else {
                sendButton.classList.remove('visible');
            }
        });
        
        textInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const query = textInput.value.trim();
                if (query && this.state === 'idle') {
                    this.handleTextQuery(query);
                    textInput.value = '';
                    sendButton.classList.remove('visible');
                }
            }
        });
        
        sendButton.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            console.log('Send button clicked');
            const query = textInput.value.trim();
            console.log('Query:', query, 'State:', this.state);
            if (query) {
                if (this.state === 'idle') {
                    this.handleTextQuery(query);
                    textInput.value = '';
                    sendButton.classList.remove('visible');
                    textInput.blur();
                } else {
                    console.log('Not idle, current state:', this.state);
                }
            } else {
                console.log('No query text');
            }
        });
        
        closeCard.addEventListener('click', () => this.closeResults());
        
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && e.target.tagName !== 'INPUT' && this.state === 'idle') {
                e.preventDefault();
                this.handleBottomBarClick();
            }
            if (e.code === 'Escape') {
                this.closeResults();
            }
        });
    }

    toggleSpeaker() {
        const speakerToggle = document.getElementById('speaker-toggle');
        const enabled = this.tts.toggle();
        
        if (enabled) {
            speakerToggle.classList.add('active');
        } else {
            speakerToggle.classList.remove('active');
        }
    }

    onOrbMouseDown(event) {
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObject(this.orb.orb);
        
        if (intersects.length > 0) {
            this.isDragging = true;
            this.dragStarted = false;
            this.previousMousePosition = {
                x: event.clientX,
                y: event.clientY
            };
            document.body.style.cursor = 'grabbing';
        }
    }

    onOrbMouseMove(event) {
        if (this.isDragging) {
            const deltaX = event.clientX - this.previousMousePosition.x;
            const deltaY = event.clientY - this.previousMousePosition.y;
            
            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
            
            if (distance > 3) {
                this.dragStarted = true;
                this.autoRotate = false;
                
                this.orb.orb.rotation.y += deltaX * 0.01;
                this.orb.orb.rotation.x += deltaY * 0.01;
            }
            
            this.previousMousePosition = {
                x: event.clientX,
                y: event.clientY
            };
        } else {
            this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            this.raycaster.setFromCamera(this.mouse, this.camera);
            const intersects = this.raycaster.intersectObject(this.orb.orb);
            
            if (intersects.length > 0) {
                document.body.style.cursor = 'pointer';
            } else {
                document.body.style.cursor = 'default';
            }
        }
    }

    onOrbMouseUp(event) {
        if (this.isDragging) {
            const wasDragging = this.dragStarted;
            this.isDragging = false;
            this.dragStarted = false;
            document.body.style.cursor = 'default';
            
            if (!wasDragging && this.state === 'idle') {
                this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
                this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
                
                this.raycaster.setFromCamera(this.mouse, this.camera);
                const intersects = this.raycaster.intersectObject(this.orb.orb);
                
                if (intersects.length > 0) {
                    console.log('Orb clicked - starting voice recognition');
                    
                    gsap.to(this.orb.orb.scale, {
                        x: 1.15, y: 1.15, z: 1.15,
                        duration: 0.2,
                        ease: 'power2.out',
                        onComplete: () => {
                            gsap.to(this.orb.orb.scale, {
                                x: 1, y: 1, z: 1,
                                duration: 0.5,
                                ease: 'elastic.out(1, 0.5)'
                            });
                        }
                    });
                    
                    this.startVoiceRecognition();
                }
            }
            
            if (wasDragging) {
                setTimeout(() => {
                    this.autoRotate = true;
                }, 2000);
            }
        }
    }

    setupWebSocket() {
        this.wsClient.on('connected', () => {
            console.log('Backend connected');
        });

        this.wsClient.on('result', (data) => {
            console.log('Result:', data);
            
            if (data.success) {
                this.showResults(this.currentQuery, data.message);
            } else {
                this.updateBottomBar('Error: ' + data.message);
                this.setState('idle');
            }
        });

        this.wsClient.on('error', (data) => {
            console.error('Error:', data);
            this.updateBottomBar('Connection error');
            this.setState('idle');
        });

        this.wsClient.connect().catch(err => {
            console.error('Failed to connect to backend:', err);
        });
    }

    handleBottomBarClick() {
        if (this.state !== 'idle') return;
        
        this.startVoiceRecognition();
    }

    handleTextQuery(query) {
        if (this.state !== 'idle') return;
        
        this.currentQuery = query;
        this.setState('searching');
        
        this.wsClient.sendTextCommand(query);
    }

    startVoiceRecognition() {
        console.log('startVoiceRecognition called, current state:', this.state);
        
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('Speech recognition not supported');
            alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.setState('listening');
        this.updateBottomBar('Listening...');
        
        console.log('Voice recognition starting...');

        this.recognition.onstart = () => {
            console.log('Voice recognition started successfully');
        };

        this.recognition.onresult = (event) => {
            const last = event.results.length - 1;
            const text = event.results[last][0].transcript;
            
            console.log('Transcript received:', text, 'isFinal:', event.results[last].isFinal);
            this.updateBottomBar(text);

            if (event.results[last].isFinal) {
                console.log('Final transcript:', text);
                this.currentQuery = text;
                this.triggerSearch(text);
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error, event);
            
            if (event.error === 'not-allowed') {
                alert('Microphone access denied. Please allow microphone access in your browser settings.');
            } else if (event.error === 'no-speech') {
                this.updateBottomBar('No speech detected. Try again.');
            } else {
                this.updateBottomBar('Error: ' + event.error);
            }
            
            this.setState('idle');
        };

        this.recognition.onend = () => {
            console.log('Voice recognition ended');
            if (this.state === 'listening') {
                this.setState('idle');
                this.updateBottomBar('Ask anything...');
            }
        };

        try {
            this.recognition.start();
            console.log('Recognition.start() called');
        } catch (error) {
            console.error('Failed to start recognition:', error);
            alert('Failed to start voice recognition: ' + error.message);
            this.setState('idle');
        }
    }

    triggerSearch(query) {
        this.setState('searching');
        this.updateBottomBar('Searching<span class="loading-dots"><span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span></span>');
        
        this.wsClient.sendVoiceCommand(query);
    }

    showResults(query, response) {
        this.setState('results');
        
        const greeting = document.getElementById('greeting');
        const bottomBar = document.getElementById('bottom-bar');
        const resultsCard = document.getElementById('results-card');
        const userQuery = document.getElementById('user-query');
        const responseContent = document.getElementById('response-content');
        
        greeting.classList.add('hidden');
        bottomBar.classList.add('hidden');
        
        userQuery.textContent = query;
        
        const formattedResponse = this.formatResponse(response);
        responseContent.innerHTML = formattedResponse;
        
        setTimeout(() => {
            resultsCard.classList.add('active');
        }, 100);
        
        if (this.tts.enabled) {
            this.tts.speak(response, this.voiceSettings);
        }
    }

    formatResponse(text) {
        // Split into paragraphs
        const paragraphs = text.split('\n').filter(p => p.trim());
        
        let html = '';
        paragraphs.forEach(para => {
            if (para.trim().startsWith('•') || para.trim().startsWith('-')) {
                // List item
                const content = para.replace(/^[•\-]\s*/, '');
                if (!html.includes('<ul>')) {
                    html += '<ul>';
                }
                html += `<li>${content}</li>`;
            } else if (para.trim().match(/^\d+\./)) {
                // Numbered list
                const content = para.replace(/^\d+\.\s*/, '');
                if (!html.includes('<ol>')) {
                    html += '<ol>';
                }
                html += `<li>${content}</li>`;
            } else if (para.trim().match(/^[A-Z][^.!?]*:$/)) {
                // Heading
                if (html.includes('<ul>') && !html.includes('</ul>')) {
                    html += '</ul>';
                }
                if (html.includes('<ol>') && !html.includes('</ol>')) {
                    html += '</ol>';
                }
                html += `<h3>${para.trim()}</h3>`;
            } else {
                // Regular paragraph
                if (html.includes('<ul>') && !html.includes('</ul>')) {
                    html += '</ul>';
                }
                if (html.includes('<ol>') && !html.includes('</ol>')) {
                    html += '</ol>';
                }
                html += `<p>${para}</p>`;
            }
        });
        
        // Close any open lists
        if (html.includes('<ul>') && !html.includes('</ul>')) {
            html += '</ul>';
        }
        if (html.includes('<ol>') && !html.includes('</ol>')) {
            html += '</ol>';
        }
        
        return html || `<p>${text}</p>`;
    }

    closeResults() {
        const greeting = document.getElementById('greeting');
        const bottomBar = document.getElementById('bottom-bar');
        const resultsCard = document.getElementById('results-card');
        
        resultsCard.classList.remove('active');
        
        setTimeout(() => {
            greeting.classList.remove('hidden');
            bottomBar.classList.remove('hidden');
            this.setState('idle');
            this.updateBottomBar('Ask anything...');
        }, 500);
    }

    setState(newState) {
        this.state = newState;
        this.orb.setState(newState);
    }

    updateBottomBar(text) {
        const textInput = document.getElementById('text-input');
        if (textInput) {
            textInput.placeholder = text;
        }
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.orb.onWindowResize(window.innerWidth, window.innerHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const delta = this.clock.getDelta();

        this.orb.update(delta, this.autoRotate);

        const cameraRadius = 0.1;
        const cameraSpeed = 0.05;
        const time = this.clock.getElapsedTime();
        this.camera.position.x = Math.sin(time * cameraSpeed) * cameraRadius;
        this.camera.position.y = Math.cos(time * cameraSpeed * 0.7) * cameraRadius;
        this.camera.lookAt(0, 0, 0);

        this.orb.render();
    }
}

new LiquidJarvisUI();
