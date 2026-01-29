export class SpeechSynthesis {
    constructor() {
        this.synth = window.speechSynthesis;
        this.voice = null;
        this.enabled = true;
        this.isSpeaking = false;
        this.onSpeakStart = null;
        this.onSpeakEnd = null;
        this.onWordBoundary = null;
        
        this.initVoice();
    }

    initVoice() {
        if (!this.synth) {
            console.warn('Speech synthesis not supported');
            this.enabled = false;
            return;
        }

        const setVoice = () => {
            const voices = this.synth.getVoices();
            
            const preferredVoices = [
                'Google US English',
                'Microsoft Zira - English (United States)',
                'Microsoft David - English (United States)',
                'Samantha',
                'Alex',
                'Google UK English Female',
                'Google UK English Male'
            ];
            
            for (const preferred of preferredVoices) {
                const found = voices.find(v => v.name === preferred);
                if (found) {
                    this.voice = found;
                    console.log('Voice selected:', this.voice.name);
                    return;
                }
            }
            
            this.voice = voices.find(v => v.lang.startsWith('en-US') && v.localService === false)
                      || voices.find(v => v.lang.startsWith('en-US'))
                      || voices.find(v => v.lang.startsWith('en'))
                      || voices[0];
            
            console.log('Voice selected:', this.voice?.name);
        };

        if (this.synth.getVoices().length > 0) {
            setVoice();
        } else {
            this.synth.addEventListener('voiceschanged', setVoice);
        }
    }

    speak(text, options = {}) {
        if (!this.enabled || !this.synth) {
            console.log('Speech disabled or not supported');
            return Promise.resolve();
        }

        this.synth.cancel();

        return new Promise((resolve) => {
            const utterance = new SpeechSynthesisUtterance(text);
            
            if (this.voice) {
                utterance.voice = this.voice;
            }
            
            utterance.rate = options.rate || 1.1;
            utterance.pitch = options.pitch || 1.0;
            utterance.volume = options.volume || 1.0;

            utterance.onstart = () => {
                this.isSpeaking = true;
                console.log('Speaking:', text);
                if (this.onSpeakStart) {
                    this.onSpeakStart(text);
                }
            };

            utterance.onend = () => {
                this.isSpeaking = false;
                if (this.onSpeakEnd) {
                    this.onSpeakEnd();
                }
                resolve();
            };

            utterance.onboundary = (event) => {
                if (event.name === 'word' && this.onWordBoundary) {
                    this.onWordBoundary(event);
                }
            };

            utterance.onerror = (event) => {
                console.error('Speech error:', event);
                this.isSpeaking = false;
                resolve();
            };

            this.synth.speak(utterance);
        });
    }

    stop() {
        if (this.synth) {
            this.synth.cancel();
            this.isSpeaking = false;
        }
    }

    toggle() {
        this.enabled = !this.enabled;
        if (!this.enabled) {
            this.stop();
        }
        return this.enabled;
    }

    getSpeaking() {
        return this.isSpeaking;
    }
}
