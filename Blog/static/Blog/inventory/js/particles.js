const particleCanvas = document.getElementById('item-particles');
const pctx = particleCanvas.getContext('2d');
let particles = [];
let particleColor = '#ffffff';
let particleFrame = null;
let mouse = { x: -9999, y: -9999 };

const REPEL_RADIUS = 300;   // distance d'influence en px
const REPEL_FORCE = 45;     // amplitude de la fuite

function onPointerMove(e) {
    const rect = particleCanvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
}

export function startParticles(color) {
    particleColor = color || '#ffffff';
    particleCanvas.classList.add('active');

    const rect = particleCanvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    particleCanvas.width = rect.width * dpr;
    particleCanvas.height = rect.height * dpr;
    pctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const cx = rect.width / 2;
    const cy = rect.height / 2;
    const radius = Math.min(rect.width, rect.height) * 0.42;

    particles = Array.from({ length: 110 }, () => {
        const angle = Math.random() * Math.PI * 2;
        return {
            angle,
            dist: radius * (0.75 + Math.random() * 0.45),
            r: 1 + Math.random() * 2,
            speed: (Math.random() - 0.5) * 0.004,
            phase: Math.random() * Math.PI * 2,
            pulse: 0.015 + Math.random() * 0.02,
            ox: 0,   // décalage de fuite courant
            oy: 0,
        };
    });

    mouse = { x: -9999, y: -9999 };
    window.addEventListener('pointermove', onPointerMove);

    if (!particleFrame) {
        particleFrame = requestAnimationFrame(() => drawParticles(cx, cy));
    }
}

function drawParticles(cx, cy) {
    const rect = particleCanvas.getBoundingClientRect();
    pctx.clearRect(0, 0, rect.width, rect.height);
    pctx.fillStyle = particleColor;
    pctx.shadowBlur = 8;
    pctx.shadowColor = particleColor;

    for (const p of particles) {
        p.angle += p.speed;
        p.phase += p.pulse;

        // position d'orbite « au repos »
        const baseX = cx + Math.cos(p.angle) * p.dist;
        const baseY = cy + Math.sin(p.angle) * p.dist;

        // fuite : cible de décalage en fonction de la souris
        let targetOx = 0;
        let targetOy = 0;
        const dx = baseX - mouse.x;
        const dy = baseY - mouse.y;
        const d = Math.hypot(dx, dy);

        if (d < REPEL_RADIUS && d > 0.01) {
            const strength = (1 - d / REPEL_RADIUS) ** 2;
            targetOx = (dx / d) * REPEL_FORCE * strength;
            targetOy = (dy / d) * REPEL_FORCE * strength;
        }

        // lissage : approche progressive, et retour au repos quand la souris s'éloigne
        p.ox += (targetOx - p.ox) * 0.12;
        p.oy += (targetOy - p.oy) * 0.12;

        pctx.globalAlpha = 0.25 + 0.55 * (Math.sin(p.phase) * 0.5 + 0.5);
        pctx.beginPath();
        pctx.arc(baseX + p.ox, baseY + p.oy, p.r, 0, Math.PI * 2);
        pctx.fill();
    }

    pctx.globalAlpha = 1;
    particleFrame = requestAnimationFrame(() => drawParticles(cx, cy));
}

export function stopParticles() {
    if (particleFrame) {
        cancelAnimationFrame(particleFrame);
        particleFrame = null;
    }
    window.removeEventListener('pointermove', onPointerMove);
    const rect = particleCanvas.getBoundingClientRect();
    pctx.clearRect(0, 0, rect.width, rect.height);
    particleCanvas.classList.remove('active');
}