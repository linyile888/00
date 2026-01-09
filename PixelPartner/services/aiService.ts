
import { GoogleGenAI, Type } from "@google/genai";
import { UserProfile, Soulmate } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || "" });

const slugify = (text: string) => {
  const map: Record<string, string> = {
    '东方古风': 'ancient_east',
    '西方中世纪': 'medieval_west',
    '赛博未来': 'cyberpunk',
    '维多利亚时代': 'victorian',
    '星际大航海': 'space',
    '男': 'male',
    '女': 'female',
    '其他': 'other'
  };
  return map[text] || 'default';
};

async function generatePortrait(description: string, era: string): Promise<string | undefined> {
  try {
    const prompt = `Premium 2D high-res pixel art bust portrait of a ${description}, themed around ${era}. Modern anime style, sharp outlines, detailed eyes, solid white background for transparency.`;
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-image',
      contents: { parts: [{ text: prompt }] },
      config: { imageConfig: { aspectRatio: "1:1" } }
    });
    for (const part of response.candidates[0].content.parts) {
      if (part.inlineData) return `data:image/png;base64,${part.inlineData.data}`;
    }
  } catch (e) { console.error(e); }
  return undefined;
}

async function generatePixelBackground(prompt: string): Promise<string | undefined> {
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-image',
      contents: { parts: [{ text: `Beautiful pixel art game background, ${prompt}, vibrant colors, nostalgic atmospheric lighting, 16:9.` }] },
      config: { imageConfig: { aspectRatio: "16:9" } }
    });
    for (const part of response.candidates[0].content.parts) {
      if (part.inlineData) return `data:image/png;base64,${part.inlineData.data}`;
    }
  } catch (e) { console.error(e); }
  return undefined;
}

export const generateSoulmate = async (profile: UserProfile): Promise<Soulmate> => {
  const eraId = slugify(profile.eraPreference);
  
  const baseInstruction = `
    You are a Matchmaker AI. Create a detailed soulmate for a user with these traits: 
    Age: ${profile.age}, Height: ${profile.height}, Personality: ${profile.personality}, MBTI: ${profile.mbti}, Preferred Era: ${profile.eraPreference}.
    
    If match score is below 60%, make the character an 'extreme contrast' (e.g., a quiet user meets a boisterous hero).
    
    Return a JSON object with: name, gender (male/female/other), age, height, weight, occupation, era, region, personality, appearanceDescription (for image gen), description, matchScore, initialDialogue.
  `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3-pro-preview",
      contents: baseInstruction,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            name: { type: Type.STRING },
            gender: { type: Type.STRING, enum: ['male', 'female', 'other'] },
            age: { type: Type.NUMBER },
            height: { type: Type.NUMBER },
            weight: { type: Type.NUMBER },
            occupation: { type: Type.STRING },
            era: { type: Type.STRING },
            region: { type: Type.STRING },
            personality: { type: Type.STRING },
            appearanceDescription: { type: Type.STRING },
            description: { type: Type.STRING },
            matchScore: { type: Type.NUMBER },
            initialDialogue: { type: Type.STRING },
          },
          required: ["name", "gender", "age", "height", "weight", "occupation", "era", "region", "personality", "appearanceDescription", "description", "matchScore", "initialDialogue"],
        }
      }
    });

    const data = JSON.parse(response.text);
    const genderKey = data.gender === 'female' ? 'female' : 'male';
    
    const [worldBg, generatedPortrait] = await Promise.all([
      generatePixelBackground(`${data.region} in ${data.era}`),
      generatePortrait(data.appearanceDescription, data.era)
    ]);

    return {
      ...data,
      spriteUrl: `https://api.dicebear.com/7.x/pixel-art/svg?seed=${data.name}&size=64`, 
      portraitUrl: generatedPortrait || `https://api.dicebear.com/7.x/pixel-art/svg?seed=${data.name}&size=256`, 
      backgroundUrl: worldBg || 'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&q=80&w=800'
    };
  } catch (error) {
    console.error(error);
    return {
      name: "艾比", gender: 'female', age: 22, height: 165, weight: 50,
      occupation: "时间旅人", era: "现代", region: "星之谷", personality: "开朗好客",
      description: "一个在森林里迷路的女孩，却总能带给你温暖。",
      spriteUrl: "https://api.dicebear.com/7.x/pixel-art/svg?seed=Abby",
      portraitUrl: "https://api.dicebear.com/7.x/pixel-art/svg?seed=Abby&size=256",
      backgroundUrl: "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&q=80&w=800",
      matchScore: 88,
      initialDialogue: "嘿！既然命运让你来到了这里，不如坐下来喝杯茶？"
    };
  }
};

export const getAiResponse = async (soulmate: Soulmate, userMessage: string, profile: UserProfile): Promise<string> => {
  const prompt = `
    Roleplay as ${soulmate.name}, a ${soulmate.occupation} from ${soulmate.era}.
    Personality: ${soulmate.personality}.
    User (${profile.gender}, age ${profile.age}) says: "${userMessage}"
    Respond in character, keeping it under 30 words. Make it feel like a cozy RPG game dialogue.
  `;
  try {
    const response = await ai.models.generateContent({ model: "gemini-3-flash-preview", contents: prompt });
    return response.text || "...";
  } catch (error) { return "（风声沙沙作响...）"; }
};
