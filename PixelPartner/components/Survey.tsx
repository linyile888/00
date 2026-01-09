
import React, { useState, useEffect, useRef } from 'react';
import { UserProfile } from '../types';

interface SurveyProps {
  onComplete: (profile: UserProfile) => void;
}

const Survey: React.FC<SurveyProps> = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [profile, setProfile] = useState<UserProfile>({
    age: 20,
    height: 170,
    weight: 60,
    gender: '其他',
    personality: '',
    hobby: '',
    mbti: '',
    eraPreference: '随缘穿越'
  });

  const questions = [
    { key: 'age', label: '你的年龄是多少？', type: 'number' },
    { key: 'height', label: '你的身高 (cm)？', type: 'number' },
    { key: 'weight', label: '你的体重 (kg)？', type: 'number' },
    { key: 'gender', label: '你的性别？', type: 'select', options: ['男', '女', '其他'] },
    { key: 'personality', label: '用三个词形容你的性格？', type: 'text' },
    { key: 'hobby', label: '你最大的爱好是什么？', type: 'text' },
    { key: 'mbti', label: '你的 MBTI 类型？', type: 'text', placeholder: '如: INFP' },
    { key: 'eraPreference', label: '你向往哪种命运背景？', type: 'select', options: ['东方古风', '西方中世纪', '赛博未来', '维多利亚时代', '星际大航海', '随缘穿越'] }
  ];

  const currentQ = questions[step];

  const handleNext = () => {
    if (step < questions.length - 1) {
      setStep(s => s + 1);
    } else {
      onComplete(profile);
    }
  };

  // Point Cloud Border Animation
  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    const particles: { x: number; y: number; size: number; speed: number; offset: number; color: string }[] = [];
    const particleCount = 200;

    const initParticles = () => {
      const { width, height } = container.getBoundingClientRect();
      canvas.width = width + 40; // Add padding for "cloud" overflow
      canvas.height = height + 40;
      
      particles.length = 0;
      for (let i = 0; i < particleCount; i++) {
        // Decide which edge this particle belongs to (0: Top, 1: Right, 2: Bottom, 3: Left)
        const edge = Math.floor(Math.random() * 4);
        let x = 0, y = 0;
        
        if (edge === 0) { x = Math.random() * width; y = 0; }
        else if (edge === 1) { x = width; y = Math.random() * height; }
        else if (edge === 2) { x = Math.random() * width; y = height; }
        else if (edge === 3) { x = 0; y = Math.random() * height; }

        particles.push({
          x: x + 20,
          y: y + 20,
          size: Math.random() * 2 + 1,
          speed: Math.random() * 0.02 + 0.01,
          offset: Math.random() * Math.PI * 2,
          color: i % 2 === 0 ? '#f472b6' : '#60a5fa' // Pink or Blue
        });
      }
    };

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const time = Date.now() * 0.002;

      particles.forEach((p) => {
        // Apply "cloudy" noise movement
        const dx = Math.sin(time + p.offset) * 4;
        const dy = Math.cos(time + p.offset) * 4;
        
        ctx.fillStyle = p.color;
        ctx.globalAlpha = 0.4 + Math.sin(time + p.offset) * 0.3;
        ctx.fillRect(p.x + dx, p.y + dy, p.size, p.size);
      });

      animationId = requestAnimationFrame(draw);
    };

    const resizeObserver = new ResizeObserver(() => {
      initParticles();
    });
    resizeObserver.observe(container);

    initParticles();
    draw();

    return () => {
      cancelAnimationFrame(animationId);
      resizeObserver.disconnect();
    };
  }, [step]); // Re-init on step change in case height changes

  return (
    <div className="relative group">
      {/* Point Cloud Canvas Border */}
      <canvas 
        ref={canvasRef} 
        className="absolute -top-[20px] -left-[20px] pointer-events-none z-0"
      />
      
      <div 
        ref={containerRef}
        className="relative z-10 w-full max-w-lg p-8 bg-[#1a1a2e]/95 text-white transition-all duration-700 animate-float"
        style={{ boxShadow: '0 0 20px rgba(0,0,0,0.5)' }}
      >
        <h2 className="text-xl mb-6 text-pink-400 text-shadow">命运调查卷</h2>
        
        <div className="mb-8">
          <label className="block text-xs mb-4 text-blue-300 font-bold">{currentQ.label}</label>
          
          {currentQ.type === 'number' && (
            <input 
              type="number"
              className="w-full bg-black/50 border-2 border-blue-500/50 p-3 text-white outline-none focus:border-pink-500 transition-colors pixelated"
              value={(profile as any)[currentQ.key]}
              onChange={(e) => setProfile({ ...profile, [currentQ.key]: Number(e.target.value) })}
            />
          )}

          {currentQ.type === 'text' && (
            <input 
              type="text"
              placeholder={(currentQ as any).placeholder}
              className="w-full bg-black/50 border-2 border-blue-500/50 p-3 text-white outline-none focus:border-pink-500 transition-colors pixelated"
              value={(profile as any)[currentQ.key]}
              onChange={(e) => setProfile({ ...profile, [currentQ.key]: e.target.value })}
            />
          )}

          {currentQ.type === 'select' && (
            <div className="grid grid-cols-2 gap-3">
              {(currentQ as any).options.map((opt: string) => (
                <button
                  key={opt}
                  onClick={() => setProfile({ ...profile, [currentQ.key]: opt })}
                  className={`p-3 text-[10px] border-2 transition-all pixelated font-bold ${
                    (profile as any)[currentQ.key] === opt ? 'border-pink-500 bg-pink-900/40 text-pink-200 shadow-[0_0_10px_rgba(236,72,153,0.3)]' : 'border-blue-500/30 hover:border-blue-400 bg-black/20'
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-between items-center">
          <div className="text-[8px] text-gray-500 font-mono tracking-widest">PHASE {step + 1} / {questions.length}</div>
          <button 
            onClick={handleNext}
            className="bg-blue-600 hover:bg-pink-600 px-8 py-3 text-xs border-2 border-white/50 shadow-lg transition-all active:scale-95 font-bold text-shadow"
          >
            {step === questions.length - 1 ? '契约达成' : '下一步'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Survey;
