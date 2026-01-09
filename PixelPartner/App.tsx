
import React, { useState, useEffect } from 'react';
import ParticleBackground from './components/ParticleBackground';
import Survey from './components/Survey';
import PixelWorld from './components/PixelWorld';
import { GameState, UserProfile, Soulmate } from './types';
import { generateSoulmate } from './services/aiService';

const App: React.FC = () => {
  const [state, setState] = useState<GameState>(GameState.SPLASH);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [soulmate, setSoulmate] = useState<Soulmate | null>(null);
  const [loadingMsg, setLoadingMsg] = useState('命运正在编织...');

  useEffect(() => {
    if (state === GameState.SPLASH) {
      const timer = setTimeout(() => setState(GameState.START_PROMPT), 3000);
      return () => clearTimeout(timer);
    }
  }, [state]);

  const handleSurveyComplete = async (p: UserProfile) => {
    setProfile(p);
    setState(GameState.TRANSITION);
    
    const messages = [
        "正在穿越时空之门...",
        "搜寻千年的缘分...",
        "量子纠缠同步中...",
        "命中注定之人已显现！"
    ];
    
    let i = 0;
    const timer = setInterval(() => {
        setLoadingMsg(messages[i]);
        i++;
        if (i >= messages.length) clearInterval(timer);
    }, 1500);

    try {
        const result = await generateSoulmate(p);
        setSoulmate(result);
        setTimeout(() => {
            setState(GameState.WORLD);
        }, 6000);
    } catch (err) {
        console.error(err);
        setState(GameState.SURVEY);
    }
  };

  return (
    <div className="relative w-screen h-screen flex items-center justify-center overflow-hidden bg-[#0c0c1e]">
      <ParticleBackground mode={state === GameState.WORLD ? 'heart' : 'disperse'} />

      {state === GameState.SPLASH && (
        <div className="z-20 text-center animate-pulse transition-opacity duration-1000">
          <p className="text-white text-xl tracking-[0.5em] text-shadow">命运的齿轮开始转动。。。</p>
        </div>
      )}

      {state === GameState.START_PROMPT && (
        <div className="z-20 text-center flex flex-col items-center gap-12 animate-in fade-in zoom-in duration-1000">
          <p className="text-white text-lg tracking-widest text-shadow">请完善你的信息，随机伴侣即将生成</p>
          <button 
            onClick={() => setState(GameState.SURVEY)}
            className="px-12 py-4 bg-pink-600/20 border-2 border-pink-500 text-pink-400 text-sm font-bold tracking-[0.3em] hover:bg-pink-600 hover:text-white transition-all animate-pulse shadow-[0_0_20px_rgba(236,72,153,0.3)]"
          >
            开启缘分
          </button>
        </div>
      )}

      {state === GameState.SURVEY && (
        <Survey onComplete={handleSurveyComplete} />
      )}

      {state === GameState.TRANSITION && (
        <div className="relative z-20 text-center">
            <div className="text-4xl text-white mb-8 animate-pulse text-shadow">穿越中</div>
            <div className="text-pink-400 text-sm font-bold tracking-widest">{loadingMsg}</div>
            <div className="fixed inset-0 bg-white/5 animate-ping pointer-events-none" />
        </div>
      )}

      {state === GameState.WORLD && profile && soulmate && (
        <div className="relative z-10 flex flex-col items-center">
            <div className="mb-6 text-center">
                <h1 className="text-2xl text-pink-400 mb-2 text-shadow">邂逅之境</h1>
                <p className="text-[10px] text-white/70">匹配度: <span className="text-green-400 font-bold">{soulmate.matchScore}%</span></p>
            </div>
            <PixelWorld profile={profile} soulmate={soulmate} />
            <button 
                onClick={() => window.location.reload()}
                className="mt-6 text-[8px] text-white/30 hover:text-white transition-colors"
            >
                [ 重新编织命运 ]
            </button>
        </div>
      )}

      <div className="fixed bottom-4 right-4 text-[8px] text-white/20 select-none pointer-events-none">
        PIXEL SOULMATE ENGINE v1.1.0
      </div>
    </div>
  );
};

export default App;
