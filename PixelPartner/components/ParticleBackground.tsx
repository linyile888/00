
import React, { useRef, useEffect } from 'react';

interface Particle {
  x: number;
  y: number;
  originX: number;
  originY: number;
  vx: number;
  vy: number;
  size: number;
  color: string;
  t: number; // For heart path parameter
}

const ParticleBackground: React.FC<{ mode: 'disperse' | 'heart' }> = ({ mode }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particles = useRef<Particle[]>([]);
  const mouse = useRef({ x: 0, y: 0, active: false });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initParticles();
    };

    const initParticles = () => {
      const count = 600;
      const newParticles: Particle[] = [];
      for (let i = 0; i < count; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        newParticles.push({
          x, y,
          originX: x, originY: y,
          vx: 0, vy: 0,
          size: Math.random() * 2 + 1,
          color: '',
          t: (i / count) * Math.PI * 2
        });
      }
      particles.current = newParticles;
    };

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const time = Date.now() * 0.001;

      particles.current.forEach((p, i) => {
        let tx = p.originX;
        let ty = p.originY;

        // Heart logic: centered on mouse
        if (mouse.current.active) {
          // Heart Shape Formula
          const scale = 12;
          const hx = 16 * Math.pow(Math.sin(p.t), 3);
          const hy = -(13 * Math.cos(p.t) - 5 * Math.cos(2 * p.t) - 2 * Math.cos(3 * p.t) - Math.cos(4 * p.t));
          
          // Add some noise to the edges
          const noise = Math.sin(time * 2 + p.t * 5) * 5;
          tx = mouse.current.x + hx * scale + noise;
          ty = mouse.current.y + hy * scale + noise;

          // Color Gradient: From center (pink) to outer (blue/purple)
          const distFromCenter = Math.sqrt(hx*hx + hy*hy) / 16;
          const r = Math.floor(255 - distFromCenter * 50);
          const g = Math.floor(100 + distFromCenter * 100);
          const b = Math.floor(150 + distFromCenter * 100);
          p.color = `rgba(${r}, ${g}, ${b}, ${0.6 + (1 - distFromCenter) * 0.4})`;
        } else {
          p.color = i % 2 === 0 ? 'rgba(244, 114, 182, 0.4)' : 'rgba(96, 165, 250, 0.4)';
        }

        const dx = tx - p.x;
        const dy = ty - p.y;
        
        p.vx += dx * 0.04;
        p.vy += dy * 0.04;
        p.vx *= 0.88;
        p.vy *= 0.88;
        p.x += p.vx;
        p.y += p.vy;

        ctx.fillStyle = p.color;
        ctx.fillRect(p.x, p.y, p.size, p.size);
      });

      requestAnimationFrame(animate);
    };

    window.addEventListener('resize', resize);
    const handleMouseMove = (e: MouseEvent) => {
      mouse.current.x = e.clientX;
      mouse.current.y = e.clientY;
      mouse.current.active = true;
    };
    const handleMouseLeave = () => { mouse.current.active = false; };
    
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);

    resize();
    animate();

    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return <canvas ref={canvasRef} className="fixed top-0 left-0 w-full h-full pointer-events-none z-0" />;
};

export default ParticleBackground;
