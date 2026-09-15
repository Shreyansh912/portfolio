// ==========================================
// 1. Interactive Neural Network + Synapses Canvas
// ==========================================
const canvas = document.getElementById('neural-canvas');
if (canvas) {
    const ctx = canvas.getContext('2d');
    let neurons = [];
    let signals = [];
    const aiGlyphs = ["∇L", "σ(z)", "W·x + b", "ReLU", "∂L/∂w", "Softmax", "ŷ", "L_ce"];
    let glyphs = [];

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        initAIWorld();
    }

    const mouse = { x: null, y: null, radius: 150 };
    window.addEventListener('resize', resizeCanvas);
    window.addEventListener('mousemove', (e) => { 
        mouse.x = e.clientX; 
        mouse.y = e.clientY; 
    });
    window.addEventListener('mouseout', () => { 
        mouse.x = null; 
        mouse.y = null; 
    });

    class NeuronNode {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.45;
            this.vy = (Math.random() - 0.5) * 0.45;
            this.radius = Math.random() * 2 + 1.2;
            this.pulse = Math.random() * Math.PI * 2;
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.pulse += 0.04;
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;

            if (mouse.x !== null && mouse.y !== null) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const dist = Math.hypot(dx, dy);
                if (dist < mouse.radius && dist > 0) {
                    const force = (mouse.radius - dist) / mouse.radius;
                    this.x -= (dx / dist) * force * 2.5;
                    this.y -= (dy / dist) * force * 2.5;
                }
            }
        }
        draw() {
            const glow = (Math.sin(this.pulse) + 1) / 2;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius + glow * 1.5, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 240, 255, ${0.4 + glow * 0.5})`;
            ctx.shadowBlur = 8;
            ctx.shadowColor = '#00f0ff';
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    class FloatingGlyph {
        constructor() { 
            this.reset(); 
            this.y = Math.random() * canvas.height; 
        }
        reset() {
            this.x = Math.random() * canvas.width;
            this.y = canvas.height + 20;
            this.vy = Math.random() * 0.35 + 0.15;
            this.text = aiGlyphs[Math.floor(Math.random() * aiGlyphs.length)];
            this.alpha = Math.random() * 0.2 + 0.08;
            this.size = Math.random() * 3 + 12;
        }
        update() { 
            this.y -= this.vy; 
            if (this.y < -30) this.reset(); 
        }
        draw() {
            ctx.font = `${this.size}px monospace`;
            ctx.fillStyle = `rgba(0, 240, 255, ${this.alpha})`;
            ctx.fillText(this.text, this.x, this.y);
        }
    }

    class SynapseSignal {
        constructor(from, to) {
            this.from = from; 
            this.to = to; 
            this.progress = 0;
            this.speed = Math.random() * 0.02 + 0.01;
        }
        update() { 
            this.progress += this.speed; 
        }
        draw() {
            const cx = this.from.x + (this.to.x - this.from.x) * this.progress;
            const cy = this.from.y + (this.to.y - this.from.y) * this.progress;
            ctx.beginPath();
            ctx.arc(cx, cy, 2.2, 0, Math.PI * 2);
            ctx.fillStyle = '#ffffff';
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#00f0ff';
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    function initAIWorld() {
        neurons = []; 
        signals = []; 
        glyphs = [];
        const count = Math.floor((canvas.width * canvas.height) / 14000);
        for (let i = 0; i < count; i++) neurons.push(new NeuronNode());
        for (let i = 0; i < Math.floor(canvas.width / 95); i++) glyphs.push(new FloatingGlyph());
    }

    function animateAI() {
        ctx.fillStyle = 'rgba(6, 8, 16, 0.32)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        glyphs.forEach(g => { g.update(); g.draw(); });
        neurons.forEach(n => { n.update(); n.draw(); });

        const maxDist = 135;
        for (let i = 0; i < neurons.length; i++) {
            for (let j = i + 1; j < neurons.length; j++) {
                const dist = Math.hypot(neurons[i].x - neurons[j].x, neurons[i].y - neurons[j].y);
                if (dist < maxDist) {
                    const alpha = (1 - dist / maxDist) * 0.32;
                    ctx.beginPath();
                    ctx.moveTo(neurons[i].x, neurons[i].y);
                    ctx.lineTo(neurons[j].x, neurons[j].y);
                    ctx.strokeStyle = `rgba(0, 240, 255, ${alpha})`;
                    ctx.lineWidth = 1;
                    ctx.stroke();

                    if (Math.random() < 0.0009 && signals.length < 25) {
                        signals.push(new SynapseSignal(neurons[i], neurons[j]));
                    }
                }
            }
        }

        for (let i = signals.length - 1; i >= 0; i--) {
            signals[i].update();
            signals[i].draw();
            if (signals[i].progress >= 1) signals.splice(i, 1);
        }
        requestAnimationFrame(animateAI);
    }
    resizeCanvas();
    animateAI();
}

// ==========================================
// 2. Holographic 3D AI Face Mesh
// ==========================================
const fCanvas = document.getElementById('ai-face-canvas');
if (fCanvas) {
    const fCtx = fCanvas.getContext('2d');
    const w = fCanvas.width;
    const h = fCanvas.height;
    const cx = w / 2;
    const cy = h / 2;

    const pts = [];
    const rows = 18;
    const cols = 22;

    for (let i = 0; i <= rows; i++) {
        const phi = (i / rows) * Math.PI;
        for (let j = 0; j < cols; j++) {
            const theta = (j / cols) * Math.PI * 2;
            let rx = 80 * Math.sin(phi);
            let ry = -115 * Math.cos(phi);
            let rz = 90 * Math.sin(phi) * Math.cos(theta);

            if (rz > 0) {
                if (ry > 25) rx *= 0.75;
                if (ry > -25 && ry < 15) rz *= 1.15;
            }
            if (rz > -40) {
                pts.push({ x: rx * Math.sin(theta), y: ry, z: rz, r: i, c: j });
            }
        }
    }

    let tRotY = 0, tRotX = 0, cRotY = 0, cRotX = 0;
    window.addEventListener('mousemove', (e) => {
        tRotY = ((e.clientX / window.innerWidth) - 0.5) * 0.75;
        tRotX = -((e.clientY / window.innerHeight) - 0.5) * 0.45;
    });

    function renderFace() {
        fCtx.clearRect(0, 0, w, h);
        cRotY += (tRotY - cRotY) * 0.05;
        cRotX += (tRotX - cRotX) * 0.05;

        const cosY = Math.cos(cRotY), sinY = Math.sin(cRotY);
        const cosX = Math.cos(cRotX), sinX = Math.sin(cRotX);
        const projected = [];

        pts.forEach(p => {
            let x1 = p.x * cosY + p.z * sinY;
            let z1 = -p.x * sinY + p.z * cosY;
            let y2 = p.y * cosX - z1 * sinX;
            let z2 = p.y * sinX + z1 * cosX;

            const scale = 340 / (340 + z2 + 90);
            const px = cx + x1 * scale;
            const py = cy + y2 * scale;
            projected.push({ x: px, y: py, z: z2, scale, r: p.r, c: p.c });

            const alpha = Math.max(0.12, (z2 + 80) / 180);
            fCtx.fillStyle = `rgba(0, 240, 255, ${alpha * 0.85})`;
            fCtx.beginPath();
            fCtx.arc(px, py, Math.max(1, 1.8 * scale), 0, Math.PI * 2);
            fCtx.fill();
        });

        fCtx.strokeStyle = 'rgba(0, 240, 255, 0.16)';
        fCtx.lineWidth = 0.8;
        for (let i = 0; i < projected.length; i++) {
            for (let j = i + 1; j < projected.length; j++) {
                const p1 = projected[i], p2 = projected[j];
                const isNeighbor = (p1.r === p2.r && Math.abs(p1.c - p2.c) === 1) ||
                                   (p1.c === p2.c && Math.abs(p1.r - p2.r) === 1);
                if (isNeighbor && Math.hypot(p1.x - p2.x, p1.y - p2.y) < 32) {
                    fCtx.beginPath();
                    fCtx.moveTo(p1.x, p1.y);
                    fCtx.lineTo(p2.x, p2.y);
                    fCtx.stroke();
                }
            }
        }
        requestAnimationFrame(renderFace);
    }
    renderFace();
}

// ==========================================
// 3. Dynamic Typewriter
// ==========================================
const words = [
    "AI Student @ IIT Hyderabad",
    "Deep Learning Researcher",
    "Full-Stack ML Builder",
    "Computer Vision Engineer"
];
let wIdx = 0, cIdx = 0, isDel = false;
const twEl = document.getElementById('typewriter');

function typeLoop() {
    if (!twEl) return;
    const cur = words[wIdx];
    twEl.textContent = isDel ? cur.substring(0, cIdx - 1) : cur.substring(0, cIdx + 1);
    cIdx = isDel ? cIdx - 1 : cIdx + 1;

    let spd = isDel ? 40 : 80;
    if (!isDel && cIdx === cur.length) { 
        spd = 2000; 
        isDel = true; 
    } else if (isDel && cIdx === 0) { 
        isDel = false; 
        wIdx = (wIdx + 1) % words.length; 
        spd = 400; 
    }
    setTimeout(typeLoop, spd);
}
document.addEventListener('DOMContentLoaded', typeLoop);

// ==========================================
// 4. Terminal Command Logic
// ==========================================
function runCommand(cmd) {
    const out = document.getElementById('terminal-output');
    if (!out) return;
    let html = '';
    if (cmd === 'skills') {
        html = `<p class="command-line"><span class="prompt">$</span> python3 -c "print(skills)"</p>
                <p class="output-text">Languages: Python, C++, JS | AI/ML: PyTorch, OpenCV, ResNet, FastAPI</p>`;
    } else if (cmd === 'projects') {
        html = `<p class="command-line"><span class="prompt">$</span> git status</p>
                <p class="output-text">Active Repos: PyTorch CNN, NumPy from Scratch, Price Tracker, Bird Detection</p>`;
    } else if (cmd === 'contact') {
        html = `<p class="command-line"><span class="prompt">$</span> echo $CONTACT_EMAIL</p>
                <p class="output-text">Shreyanshsonkar59@gmail.com (Open for AI/ML Roles)</p>`;
    } else if (cmd === 'clear') {
        out.innerHTML = `<p class="command-line"><span class="prompt">$</span> clear</p>
            <div class="terminal-actions">
                <button onclick="runCommand('skills')">skills</button>
                <button onclick="runCommand('projects')">projects</button>
                <button onclick="runCommand('contact')">contact</button>
                <button onclick="runCommand('clear')">clear</button>
            </div>`;
        return;
    }
    const btns = out.querySelector('.terminal-actions');
    const d = document.createElement('div');
    d.innerHTML = html;
    out.insertBefore(d, btns);
    out.scrollTop = out.scrollHeight;
}

// ==========================================
// 5. 3D Tilt on Cards & Custom Cursor
// ==========================================
document.querySelectorAll('.project-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const r = card.getBoundingClientRect();
        const x = e.clientX - r.left, y = e.clientY - r.top;
        const rx = ((y - r.height / 2) / (r.height / 2)) * -6;
        const ry = ((x - r.width / 2) / (r.width / 2)) * 6;
        card.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-4px)`;
    });
    card.addEventListener('mouseleave', () => {
        card.style.transform = `perspective(800px) rotateX(0deg) rotateY(0deg) translateY(0)`;
    });
});

const cur = document.getElementById('cursor');
const fol = document.getElementById('cursor-follower');
if (cur && fol) {
    window.addEventListener('mousemove', (e) => {
        cur.style.transform = `translate3d(${e.clientX - 4}px, ${e.clientY - 4}px, 0)`;
        fol.style.transform = `translate3d(${e.clientX - 16}px, ${e.clientY - 16}px, 0)`;
    });
    document.querySelectorAll('a, button, .project-card').forEach(el => {
        el.addEventListener('mouseenter', () => {
            fol.style.width = '48px';
            fol.style.height = '48px';
            fol.style.borderColor = 'var(--primary)';
        });
        el.addEventListener('mouseleave', () => {
            fol.style.width = '32px';
            fol.style.height = '32px';
            fol.style.borderColor = 'rgba(0, 240, 255, 0.45)';
        });
    });
}

// ==========================================
// 6. Scroll Reveal Observer
// ==========================================
const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            obs.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('section, .project-card, .skill').forEach(el => {
    el.classList.add('reveal-item');
    observer.observe(el);
});
// ==========================================
// 7. J.A.R.V.I.S. 3D Face & Audio Speech System
// ==========================================
const jCanvas = document.getElementById('jarvis-canvas');
let isJarvisSpeaking = false;
let hasAutoSpoken = false;

if (jCanvas) {
    const ctx = jCanvas.getContext('2d');
    const width = jCanvas.width;
    const height = jCanvas.height;
    const cx = width / 2;
    const cy = height / 2;

    // Build 3D Parametric Face Wireframe Coordinates
    const points = [];
    const rows = 18;
    const cols = 22;

    for (let i = 0; i <= rows; i++) {
        const phi = (i / rows) * Math.PI;
        for (let j = 0; j < cols; j++) {
            const theta = (j / cols) * Math.PI * 2;
            let rx = 78 * Math.sin(phi);
            let ry = -115 * Math.cos(phi);
            let rz = 90 * Math.sin(phi) * Math.cos(theta);

            if (rz > 0) {
                if (ry > 25) rx *= 0.75; // Chin
                if (ry > -25 && ry < 15) rz *= 1.15; // Eye & nose bridge
            }
            if (rz > -40) {
                points.push({ x: rx * Math.sin(theta), y: ry, z: rz, r: i, c: j });
            }
        }
    }

    let targetRotY = 0, targetRotX = 0, curRotY = 0, curRotX = 0;
    window.addEventListener('mousemove', (e) => {
        targetRotY = ((e.clientX / window.innerWidth) - 0.5) * 0.7;
        targetRotX = -((e.clientY / window.innerHeight) - 0.5) * 0.45;
    });

    function drawJarvisFrame() {
        ctx.clearRect(0, 0, width, height);

        curRotY += (targetRotY - curRotY) * 0.05;
        curRotX += (targetRotX - curRotX) * 0.05;

        const cosY = Math.cos(curRotY), sinY = Math.sin(curRotY);
        const cosX = Math.cos(curRotX), sinX = Math.sin(curRotX);
        const projected = [];

        // Audio waveform distortion when J.A.R.V.I.S. is speaking
        const speechJitter = isJarvisSpeaking ? (Math.random() - 0.5) * 4.5 : 0;

        points.forEach(p => {
            let x1 = (p.x + speechJitter) * cosY + p.z * sinY;
            let z1 = -(p.x + speechJitter) * sinY + p.z * cosY;
            let y2 = p.y * cosX - z1 * sinX;
            let z2 = p.y * sinX + z1 * cosX;

            const scale = 340 / (340 + z2 + 90);
            const px = cx + x1 * scale;
            const py = cy + y2 * scale;
            projected.push({ x: px, y: py, z: z2, scale, r: p.r, c: p.c });

            const alpha = Math.max(0.12, (z2 + 80) / 180);
            ctx.fillStyle = isJarvisSpeaking ? `rgba(255, 255, 255, ${alpha * 0.95})` : `rgba(0, 240, 255, ${alpha * 0.8})`;
            ctx.beginPath();
            ctx.arc(px, py, Math.max(1, 1.8 * scale), 0, Math.PI * 2);
            ctx.fill();
        });

        // Draw wireframe connection links
        ctx.strokeStyle = isJarvisSpeaking ? 'rgba(0, 240, 255, 0.4)' : 'rgba(0, 240, 255, 0.16)';
        ctx.lineWidth = 0.8;
        for (let i = 0; i < projected.length; i++) {
            for (let j = i + 1; j < projected.length; j++) {
                const p1 = projected[i], p2 = projected[j];
                const isNeighbor = (p1.r === p2.r && Math.abs(p1.c - p2.c) === 1) ||
                                   (p1.c === p2.c && Math.abs(p1.r - p2.r) === 1);
                if (isNeighbor && Math.hypot(p1.x - p2.x, p1.y - p2.y) < 32) {
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }

        requestAnimationFrame(drawJarvisFrame);
    }
    drawJarvisFrame();
}

// ==========================================
// Speech Synthesis & Automatic Vocal Intro
// ==========================================
function speakJarvisIntro(forceReplay = false) {
    if (isJarvisSpeaking && !forceReplay) return;

    const statusEl = document.getElementById('jarvis-status-text');
    const transcriptEl = document.getElementById('jarvis-transcript');
    const introScript = "Hello Guys. I am  Shreyansh Sonkar, Artificial Intelligence student at I.I.T. Hyderabad. Systems and neural repositories are online and available for inspection.";

    if (!('speechSynthesis' in window)) {
        if (transcriptEl) transcriptEl.textContent = introScript;
        return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(introScript);
    const voices = window.speechSynthesis.getVoices();

    // Priority hierarchy for authentic J.A.R.V.I.S.-style voices
    const jarvisVoice = voices.find(v => 
        v.name.includes("Google UK English Male") || 
        v.name.includes("Microsoft Ryan Online (Natural)") || 
        v.name.includes("Oliver") || 
        (v.lang === "en-GB" && !v.name.includes("Female"))
    ) || voices.find(v => v.lang === "en-GB") || voices.find(v => v.lang.startsWith("en"));

    if (jarvisVoice) {
        utterance.voice = jarvisVoice;
    }

    // Calibrated speed and frequency for a calm, crisp AI persona
    utterance.rate = 0.95; 
    utterance.pitch = 0.88; 

    utterance.onstart = () => {
        isJarvisSpeaking = true;
        if (statusEl) statusEl.textContent = "SYSTEM: VOCALIZING PROTOCOL";
        if (transcriptEl) transcriptEl.textContent = "J.A.R.V.I.S.: Transmitting portfolio summary...";
    };

    utterance.onend = () => {
        isJarvisSpeaking = false;
        if (statusEl) statusEl.textContent = "SYSTEM: READY & MONITORING";
        if (transcriptEl) transcriptEl.textContent = "J.A.R.V.I.S.: Introduction complete.";
    };

    window.speechSynthesis.speak(utterance);
}

// Auto-trigger speech on first user interaction (bypasses browser autoplay blocks)
function setupAutoIntroduction() {
    const triggerEvents = ['click', 'keydown', 'scroll'];
    const autoHandler = () => {
        if (!hasAutoSpoken) {
            hasAutoSpoken = true;
            speakJarvisIntro(false);
            triggerEvents.forEach(evt => window.removeEventListener(evt, autoHandler));
        }
    };
    triggerEvents.forEach(evt => window.addEventListener(evt, autoHandler, { once: true }));
}

document.addEventListener('DOMContentLoaded', () => {
    // Warm up voice list
    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }
    setupAutoIntroduction();
});