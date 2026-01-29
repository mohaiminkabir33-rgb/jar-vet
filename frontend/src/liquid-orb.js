import * as THREE from 'three';
import { gsap } from 'gsap';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

export class LiquidOrb {
    constructor(scene, camera, renderer) {
        this.scene = scene;
        this.camera = camera;
        this.renderer = renderer;
        
        this.time = 0;
        this.timeSpeed = 1.0;
        
        this.createOrb();
        this.setupPostProcessing();
    }

    createOrb() {
        const geometry = new THREE.SphereGeometry(1.7, 256, 256);
        
        const material = new THREE.ShaderMaterial({
            uniforms: {
                uTime: { value: 0 },
                uColor: { value: new THREE.Color(0x5E87FF) },
                uNoiseStrength: { value: 0.18 },
                uFresnelPower: { value: 3.0 },
                uNoiseFrequency: { value: 0.9 },
                uNoiseLacunarity: { value: 0.4 }
            },
            vertexShader: `
                varying vec3 vNormal;
                varying vec3 vPosition;
                varying vec2 vUv;
                uniform float uTime;
                uniform float uNoiseStrength;
                uniform float uNoiseFrequency;
                uniform float uNoiseLacunarity;
                
                // Simplex 3D Noise
                vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
                vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
                vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
                vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
                
                float snoise(vec3 v) {
                    const vec2 C = vec2(1.0/6.0, 1.0/3.0);
                    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
                    
                    vec3 i  = floor(v + dot(v, C.yyy));
                    vec3 x0 = v - i + dot(i, C.xxx);
                    
                    vec3 g = step(x0.yzx, x0.xyz);
                    vec3 l = 1.0 - g;
                    vec3 i1 = min(g.xyz, l.zxy);
                    vec3 i2 = max(g.xyz, l.zxy);
                    
                    vec3 x1 = x0 - i1 + C.xxx;
                    vec3 x2 = x0 - i2 + C.yyy;
                    vec3 x3 = x0 - D.yyy;
                    
                    i = mod289(i);
                    vec4 p = permute(permute(permute(
                        i.z + vec4(0.0, i1.z, i2.z, 1.0))
                        + i.y + vec4(0.0, i1.y, i2.y, 1.0))
                        + i.x + vec4(0.0, i1.x, i2.x, 1.0));
                    
                    float n_ = 0.142857142857;
                    vec3 ns = n_ * D.wyz - D.xzx;
                    
                    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
                    
                    vec4 x_ = floor(j * ns.z);
                    vec4 y_ = floor(j - 7.0 * x_);
                    
                    vec4 x = x_ *ns.x + ns.yyyy;
                    vec4 y = y_ *ns.x + ns.yyyy;
                    vec4 h = 1.0 - abs(x) - abs(y);
                    
                    vec4 b0 = vec4(x.xy, y.xy);
                    vec4 b1 = vec4(x.zw, y.zw);
                    
                    vec4 s0 = floor(b0)*2.0 + 1.0;
                    vec4 s1 = floor(b1)*2.0 + 1.0;
                    vec4 sh = -step(h, vec4(0.0));
                    
                    vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
                    vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
                    
                    vec3 p0 = vec3(a0.xy, h.x);
                    vec3 p1 = vec3(a0.zw, h.y);
                    vec3 p2 = vec3(a1.xy, h.z);
                    vec3 p3 = vec3(a1.zw, h.w);
                    
                    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
                    p0 *= norm.x;
                    p1 *= norm.y;
                    p2 *= norm.z;
                    p3 *= norm.w;
                    
                    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
                    m = m * m;
                    return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
                }
                
                // Cubic smoothstep for ultra-smooth interpolation
                float smootherstep(float edge0, float edge1, float x) {
                    x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
                    return x * x * x * (x * (x * 6.0 - 15.0) + 10.0);
                }
                
                void main() {
                    vUv = uv;
                    vNormal = normalize(normalMatrix * normal);
                    
                    vec3 pos = position;
                    
                    // Multi-octave smooth noise with low frequency for liquid effect
                    float freq1 = uNoiseFrequency * 0.6;
                    float freq2 = uNoiseFrequency * 0.8;
                    float freq3 = uNoiseFrequency * 1.0;
                    
                    float time1 = uTime * 0.15;
                    float time2 = uTime * 0.12;
                    float time3 = uTime * 0.10;
                    
                    // Layer multiple smooth noise octaves
                    float noise1 = snoise(pos * freq1 + time1);
                    float noise2 = snoise(pos * freq2 + time2);
                    float noise3 = snoise(pos * freq3 + time3);
                    
                    // Apply smootherstep to each octave for ultra-smooth transitions
                    noise1 = smootherstep(-1.0, 1.0, noise1);
                    noise2 = smootherstep(-1.0, 1.0, noise2);
                    noise3 = smootherstep(-1.0, 1.0, noise3);
                    
                    // Blend octaves with decreasing amplitude (lacunarity)
                    float noise = noise1 * 0.5 + noise2 * 0.3 + noise3 * 0.2;
                    
                    // Remap from [0,1] to [-1,1] smoothly
                    noise = noise * 2.0 - 1.0;
                    noise = smootherstep(-1.0, 1.0, noise);
                    noise = noise * 2.0 - 1.0;
                    
                    // Apply displacement with reduced strength for smoothness
                    pos += normal * noise * uNoiseStrength;
                    
                    vPosition = pos;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 uColor;
                uniform float uTime;
                uniform float uFresnelPower;
                
                varying vec3 vNormal;
                varying vec3 vPosition;
                varying vec2 vUv;
                
                // Cubic smoothstep for smooth color transitions
                float smootherstep(float edge0, float edge1, float x) {
                    x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
                    return x * x * x * (x * (x * 6.0 - 15.0) + 10.0);
                }
                
                void main() {
                    // Fresnel effect with smooth interpolation
                    vec3 viewDirection = normalize(cameraPosition - vPosition);
                    float fresnelRaw = 1.0 - abs(dot(viewDirection, vNormal));
                    float fresnel = pow(fresnelRaw, uFresnelPower);
                    
                    // Apply smootherstep for ultra-smooth gradient
                    fresnel = smootherstep(0.0, 1.0, fresnel);
                    
                    // Thinner rim glow
                    vec3 rimColor = uColor * fresnel * 1.6;
                    
                    // Soft highlights with smooth falloff
                    float highlight = pow(fresnel, 8.0);
                    highlight = smootherstep(0.0, 1.0, highlight);
                    vec3 hotSpot = vec3(1.0) * highlight * 0.5;
                    
                    // Smooth center-to-edge gradient
                    float centerGlow = smootherstep(0.0, 1.0, 1.0 - fresnel) * 0.2;
                    vec3 centerColor = uColor * centerGlow;
                    
                    // Combine with smooth blending
                    vec3 finalColor = rimColor + hotSpot + centerColor;
                    float alpha = smootherstep(0.0, 1.0, fresnel) * 0.85;
                    
                    gl_FragColor = vec4(finalColor, alpha);
                }
            `,
            transparent: true,
            side: THREE.DoubleSide,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        });

        this.orb = new THREE.Mesh(geometry, material);
        this.orb.frustumCulled = false;
        geometry.computeVertexNormals();
        this.scene.add(this.orb);
        
        // Add point light for extra glow
        this.light = new THREE.PointLight(0x5E87FF, 1.5, 12);
        this.light.position.set(0, 0, 0);
        this.scene.add(this.light);
    }

    setupPostProcessing() {
        this.composer = new EffectComposer(this.renderer);
        
        const renderPass = new RenderPass(this.scene, this.camera);
        this.composer.addPass(renderPass);
        
        this.bloomPass = new UnrealBloomPass(
            new THREE.Vector2(window.innerWidth, window.innerHeight),
            1.2,  // strength - reduced brightness
            0.9,  // radius - moderate glow spread
            0.08  // threshold - higher to reduce brightness
        );
        this.composer.addPass(this.bloomPass);
    }

    setState(state) {
        const animations = {
            idle: () => {
                gsap.to(this.orb.scale, { x: 1, y: 1, z: 1, duration: 1, ease: 'power2.out' });
                gsap.to(this.orb.position, { z: 0, duration: 1, ease: 'power2.out' });
                gsap.to(this, { timeSpeed: 1.0, duration: 1 });
                gsap.to(this.orb.material.uniforms.uColor.value, {
                    r: new THREE.Color(0x5E87FF).r,
                    g: new THREE.Color(0x5E87FF).g,
                    b: new THREE.Color(0x5E87FF).b,
                    duration: 1
                });
            },
            searching: () => {
                gsap.to(this, { timeSpeed: 3.0, duration: 0.5 });
                gsap.to(this.orb.material.uniforms.uColor.value, {
                    r: new THREE.Color(0x00FFFF).r,
                    g: new THREE.Color(0x00FFFF).g,
                    b: new THREE.Color(0x00FFFF).b,
                    duration: 0.5
                });
            },
            results: () => {
                gsap.to(this.orb.scale, { x: 0.5, y: 0.5, z: 0.5, duration: 1, ease: 'power2.out' });
                gsap.to(this.orb.position, { z: -3, duration: 1, ease: 'power2.out' });
                gsap.to(this, { timeSpeed: 0.5, duration: 1 });
            },
            listening: () => {
                gsap.to(this, { timeSpeed: 2.0, duration: 0.5 });
                gsap.to(this.orb.scale, { x: 1.1, y: 1.1, z: 1.1, duration: 0.5, ease: 'elastic.out(1, 0.5)' });
            }
        };
        
        if (animations[state]) {
            animations[state]();
        }
    }

    update(deltaTime, autoRotate = true) {
        const smoothDelta = Math.min(deltaTime, 0.1);
        this.time += smoothDelta * this.timeSpeed;
        
        if (this.orb.material.uniforms) {
            this.orb.material.uniforms.uTime.value = this.time;
        }
        
        if (autoRotate) {
            this.orb.rotation.y += 0.0008 * this.timeSpeed * smoothDelta * 60;
            this.orb.rotation.x = Math.sin(this.time * 0.15) * 0.08;
        }
    }

    render() {
        this.composer.render();
    }

    onWindowResize(width, height) {
        this.composer.setSize(width, height);
        this.bloomPass.setSize(width, height);
    }
}
