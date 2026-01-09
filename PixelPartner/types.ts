
export interface UserProfile {
  age: number;
  height: number;
  weight: number;
  gender: string;
  personality: string;
  hobby: string;
  mbti: string;
  eraPreference: string;
}

export interface Soulmate {
  name: string;
  age: number;
  height: number;
  weight: number;
  gender: 'male' | 'female' | 'other';
  occupation: string;
  era: string;
  region: string;
  personality: string;
  description: string;
  spriteUrl: string;
  portraitUrl: string;
  backgroundUrl: string;
  dialogueBackgroundUrl?: string; 
  matchScore: number;
  initialDialogue: string;
}

export enum GameState {
  SPLASH = 'SPLASH',
  START_PROMPT = 'START_PROMPT',
  SURVEY = 'SURVEY',
  TRANSITION = 'TRANSITION',
  WORLD = 'WORLD'
}
