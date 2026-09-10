// Interactive Neural Network Particle Background
const canvas = document.getElementById('neural-canvas');
if (canvas) {
    const ctx = canvas.getContext('2d');
    let particlesArray = [];
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });

    const mouse = {
        x: null,
        y: null,
        radius: 120
    }

    window.addEventListener('mousemove', (event) => {
        mouse.x = event.clientX;
        mouse.y = event.clientY;
    });

    window.addEventListener('mouseout', () => {
        mouse.x = undefined;
        mouse.y = undefined;
    });

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 1;
            this.baseX = this.x;
            this.baseY = this.y;
            this.dx = (Math.random() - 0.5) * 0.8;
            this.dy = (Math.random() - 0.5) * 0.8;
        }
        update() {
            this.x += this.dx;
            this.y += this.dy;

            if (this.x < 0 || this.x > canvas.width) this.dx = -this.dx;
            if (this.y < 0 || this.y > canvas.height) this.dy = -this.dy;
        }
        draw() {
            ctx.fillStyle = 'rgba(0, 240, 255, 0.7)';
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.closePath();
            ctx.fill();
        }
    }

    function init() {
        particlesArray = [];
        let numberOfParticles = (canvas.width * canvas.height) / 15000;
        for (let i = 0; i < numberOfParticles; i++) {
            particlesArray.push(new Particle());
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        for (let i = 0; i < particlesArray.length; i++) {
            particlesArray[i].update();
            particlesArray[i].draw();

            for (let j = i; j < particlesArray.length; j++) {
                let distance = ((particlesArray[i].x - particlesArray[j].x) * (particlesArray[i].x - particlesArray[j].x)) +
                               ((particlesArray[i].y - particlesArray[j].y) * (particlesArray[i].y - particlesArray[j].y));
                
                if (distance < 12000) {
                    let opacity = 1 - (distance / 12000);
                    ctx.strokeStyle = `rgba(0, 240, 255, ${opacity * 0.25})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(particlesArray[i].x, particlesArray[i].y);
                    ctx.lineTo(particlesArray[j].x, particlesArray[j].y);
                    ctx.stroke();
                }
            }

            if (mouse.x && mouse.y) {
                let mouseDistance = ((particlesArray[i].x - mouse.x) * (particlesArray[i].x - mouse.x)) +
                                    ((particlesArray[i].y - mouse.y) * (particlesArray[i].y - mouse.y));
                if (mouseDistance < 15000) {
                    ctx.strokeStyle = 'rgba(0, 240, 255, 0.5)';
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(particlesArray[i].x, particlesArray[i].y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }

    init();
    animate();
}

// Interactive Terminal Logic
function runCommand(cmd) {
    const outputDiv = document.getElementById('terminal-output');
    if (!outputDiv) return;

    let responseHtml = '';
    
    if (cmd === 'skills') {
        responseHtml = `<p class="command-line"><span class="prompt">$</span> python3 -c "print(skills)"</p>
                        <p class="output-text">Languages: Python, C++, JavaScript | Frameworks: PyTorch, OpenCV, FastAPI</p>`;
    } else if (cmd === 'projects') {
        responseHtml = `<p class="command-line"><span class="prompt">$</span> git log --oneline</p>
                        <p class="output-text">5 Active Repos: CNN from Scratch, Shape Classification, AI PDF Assistant, Bird Detector, Expense Tracker</p>`;
    } else if (cmd === 'contact') {
        responseHtml = `<p class="command-line"><span class="prompt">$</span> mailto shreyanshsonkar59@gmail.com</p>
                        <p class="output-text">Status: Open for AI/ML collaborations & software roles.</p>`;
    } else if (cmd === 'clear') {
        outputDiv.innerHTML = `<p class="command-line"><span class="prompt">$</span> clear</p>
                               <div class="terminal-actions">
                                   <button onclick="runCommand('skills')">skills</button>
                                   <button onclick="runCommand('projects')">projects</button>
                                   <button onclick="runCommand('contact')">contact</button>
                                   <button onclick="runCommand('clear')">clear</button>
                               </div>`;
        return;
    }

    // Append response above action buttons
    const actionButtons = outputDiv.querySelector('.terminal-actions');
    const newBlock = document.createElement('div');
    newBlock.innerHTML = responseHtml;
    outputDiv.insertBefore(newBlock, actionButtons);
    outputDiv.scrollTop = outputDiv.scrollHeight;
}

// Scroll Reveal Animation using Intersection Observer
const observerOptions = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('section, .project-card, .skill').forEach(el => {
    el.classList.add('reveal-item');
    observer.observe(el);
});

// Custom Cursor Movement
const cursor = document.getElementById('cursor');
const follower = document.getElementById('cursor-follower');

if (cursor && follower) {
    window.addEventListener('mousemove', (e) => {
        cursor.style.transform = `translate3d(${e.clientX - 4}px, ${e.clientY - 4}px, 0)`;
        follower.style.transform = `translate3d(${e.clientX - 16}px, ${e.clientY - 16}px, 0)`;
    });

    document.querySelectorAll('a, button, .project-card, .skill').forEach(item => {
        item.addEventListener('mouseenter', () => {
            follower.style.width = '48px';
            follower.style.height = '48px';
            follower.style.borderColor = 'var(--primary)';
        });
        item.addEventListener('mouseleave', () => {
            follower.style.width = '32px';
            follower.style.height = '32px';
            follower.style.borderColor = 'rgba(0, 240, 255, 0.4)';
        });
    });
}