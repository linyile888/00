
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { UserProfile, Soulmate } from '../types';
import { getAiResponse } from '../services/aiService';

interface PixelWorldProps {
  profile: UserProfile;
  soulmate: Soulmate;
}

interface Particle {
  x: number; y: number; vx: number; vy: number; color: string; alpha: number; life: number;
}

const PixelWorld: React.FC<PixelWorldProps> = ({ profile, soulmate }) => {
  const [pos, setPos] = useState({ x: 340, y: 530 });
  const [npcPos] = useState({ x: 600, y: 530 });
  const [showDialogue, setShowDialogue] = useState(false);
  const [dialogueEnabled, setDialogueEnabled] = useState(true);
  
  const [chatHistory, setChatHistory] = useState<{ role: string, text: string }[]>([
    { role: 'npc', text: soulmate.initialDialogue }
  ]);
  const [userInput, setUserInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  const eraId = useMemo(() => {
    const combined = (soulmate.era + soulmate.region).toLowerCase();
    if (combined.includes('古风') || combined.includes('east')) return 'ancient_east';
    if (combined.includes('星际') || combined.includes('space')) return 'space';
    return 'default';
  }, [soulmate.era, soulmate.region]);

  // Strictly gender-based portraits for the player
  const userPortraitUrl = useMemo(() => {
    return profile.gender === '男' ? 'male.png' : 'female.png';
  }, [profile.gender]);

  const theme = useMemo(() => {
    if (eraId === 'ancient_east') return { accent: '#f59e0b', glow: 'rgba(245, 158, 11, 0.4)', text: '#fef3c7' };
    if (eraId === 'space') return { accent: '#06b6d4', glow: 'rgba(6, 182, 212, 0.4)', text: '#cffafe' };
    return { accent: '#ec4899', glow: 'rgba(236, 72, 153, 0.4)', text: '#fce7f3' };
  }, [eraId]);

  const cloudCanvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);

  useEffect(() => {
    if (!showDialogue || !dialogueEnabled) return;
    const canvas = cloudCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    const update = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (particlesRef.current.length < 40) {
        particlesRef.current.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.1,
          vy: (Math.random() - 0.5) * 0.1,
          color: theme.accent, alpha: 1, life: 1.0
        });
      }

      particlesRef.current = particlesRef.current.filter(p => {
        p.x += p.vx; p.y += p.vy; p.life -= 0.005;
        if (p.life <= 0) return false;
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.life * 0.15;
        ctx.fillRect(p.x, p.y, 2, 2);
        return true;
      });
      animationId = requestAnimationFrame(update);
    };
    update();
    return () => cancelAnimationFrame(animationId);
  }, [showDialogue, dialogueEnabled, theme]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (document.activeElement?.tagName === 'INPUT') return;
      setPos(prev => {
        let nX = prev.x, nY = prev.y;
        if (['w', 'ArrowUp'].includes(e.key)) nY -= 15;
        if (['s', 'ArrowDown'].includes(e.key)) nY += 15;
        if (['a', 'ArrowLeft'].includes(e.key)) nX -= 15;
        if (['d', 'ArrowRight'].includes(e.key)) nX += 15;
        nX = Math.max(50, Math.min(nX, 750));
        nY = Math.max(480, Math.min(nY, 580));
        const dist = Math.sqrt((nX - npcPos.x)**2 + (nY - npcPos.y)**2);
        setShowDialogue(dist < 70);
        return { x: nX, y: nY };
      });
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [npcPos]);

  const handleSend = async () => {
    if (!userInput.trim()) return;
    const m = userInput; setUserInput('');
    setChatHistory(p => [...p, { role: 'user', text: m }]);
    setIsTyping(true);
    const res = await getAiResponse(soulmate, m, profile);
    setIsTyping(false);
    setChatHistory(p => [...p, { role: 'npc', text: res }]);
  };

  const activePortrait = (isFocused || userInput.length > 0) ? userPortraitUrl : soulmate.portraitUrl;
  const activeName = (isFocused || userInput.length > 0) ? "你" : soulmate.name;

  return (
    <div className="relative w-[800px] h-[600px] border-4 border-black overflow-hidden bg-black shadow-2xl">
      {/* Background with Blur effect when talking */}
      <div className="absolute inset-0">
        <img src={soulmate.backgroundUrl} className={`absolute inset-0 w-full h-full object-cover pixelated transition-all duration-1000 ${showDialogue && dialogueEnabled ? 'opacity-30 blur-sm' : 'opacity-100'}`} />
      </div>

      {/* UI Toggle Button */}
      <button 
        onClick={() => setDialogueEnabled(!dialogueEnabled)}
        className="absolute top-4 right-4 z-[110] px-4 py-2 bg-black/60 border-2 border-white/20 text-[8px] text-white hover:bg-white/20 transition-all font-['Press_Start_2P']"
      >
        {dialogueEnabled ? 'HIDE UI' : 'SHOW UI'}
      </button>

      {/* NPC Sprite */}
      <div className="absolute pointer-events-none" style={{ left: npcPos.x, top: npcPos.y, zIndex: 10 }}>
        <img src={soulmate.spriteUrl} className="w-16 h-16 pixelated animate-pixel-breath" onError={e=>e.currentTarget.style.display='none'} />
        <div className="w-10 h-1 bg-black/40 rounded-full mt-1 animate-shadow mx-auto" />
      </div>
      
      {/* Player Character */}
      <div className="absolute transition-all duration-100 flex flex-col items-center" style={{ left: pos.x, top: pos.y, zIndex: 11 }}>
        <div className="w-12 h-12 bg-blue-500 border-2 border-white pixelated flex items-center justify-center animate-pixel-bounce text-white text-[16px] shadow-lg">:)</div>
        <div className="w-8 h-1 bg-black/40 rounded-full mt-1 animate-shadow" />
      </div>

      {/* Interaction Interface */}
      {showDialogue && dialogueEnabled && (
        <div className="absolute bottom-6 left-6 right-6 flex items-end z-[100] animate-in slide-in-from-bottom duration-500">
          
          {/* Portrait: Fixed 200x200 */}
          <div className="relative w-[200px] h-[200px] flex items-center justify-center shrink-0 select-none pointer-events-none overflow-hidden bg-black/40 border-l-2 border-t-2 border-b-2 border-white/30 rounded-l-sm shadow-2xl">
            <img 
              src={activePortrait}
              alt={activeName}
              className="w-full h-full object-cover pixelated transition-all duration-500"
              onError={(e) => {
                const fallback = activePortrait.includes('female') ? 'refined_female' : 'refined_male';
                e.currentTarget.src = `https://api.dicebear.com/7.x/pixel-art/svg?seed=${fallback}&backgroundColor=b6e3f4`;
              }}
            />
          </div>

          {/* Dialogue Box */}
          <div className="flex-1 relative h-[200px]">
             <canvas ref={cloudCanvasRef} width={500} height={200} className="absolute inset-0 pointer-events-none z-0" />
             
             <div className="relative z-10 bg-black/15 backdrop-blur-3xl h-full p-6 border-2 border-white/20 shadow-2xl flex flex-col rounded-r-sm">
                <div className="mb-2">
                   <span className="text-[10px] font-bold tracking-widest text-shadow uppercase font-['Press_Start_2P']" style={{ color: theme.accent }}>
                      {activeName}
                   </span>
                </div>
                
                <div className="flex-1 overflow-y-auto scrollbar-hide text-[8px] leading-relaxed font-['Press_Start_2P']" style={{ color: theme.text }}>
                   {chatHistory.slice(-3).map((c, i) => (
                      <div key={i} className={`mb-3 ${c.role === 'user' ? 'text-right opacity-60' : 'text-left'}`}>
                         <span className="inline-block px-3 py-1.5 bg-white/5 rounded-sm">
                           {c.text}
                         </span>
                      </div>
                   ))}
                   {isTyping && <div className="animate-pulse opacity-40 text-[6px] mt-1 font-['Press_Start_2P']">SYNCING...</div>}
                </div>

                <div className="mt-4 flex gap-3">
                   <input 
                      autoFocus
                      onFocus={() => setIsFocused(true)}
                      onBlur={() => setIsFocused(false)}
                      className="flex-1 bg-white/5 border-b-2 border-white/20 px-4 py-2 text-[8px] font-['Press_Start_2P'] outline-none focus:border-white/50 transition-all text-white placeholder:text-white/20" 
                      placeholder="TYPE YOUR HEART..."
                      value={userInput} 
                      onChange={e=>setUserInput(e.target.value)} 
                      onKeyDown={e=>e.key==='Enter'&&handleSend()} 
                   />
                   <button 
                      onClick={handleSend}
                      className="px-6 py-2 bg-white/10 hover:bg-white/20 text-[8px] font-['Press_Start_2P'] border-2 border-white/30 transition-all active:scale-95"
                      style={{ color: theme.accent }}
                   >
                      SEND
                   </button>
                </div>
             </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PixelWorld;
