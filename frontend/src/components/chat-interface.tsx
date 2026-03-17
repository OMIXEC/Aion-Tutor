"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Sparkles, Loader2, Mic, Video, MessageSquare } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { getMessages } from "@/lib/api";

export function ChatInterface({ profile, userId, sessionId, onAgentChange }: { 
  profile: any; 
  userId?: string; 
  sessionId?: string; 
  onAgentChange?: (agent: string) => void 
}) {
  const defaultWelcome = [{
    id: "welcome",
    role: "assistant",
    content: "Hello! I am your Aion Tutor. I've initialized your personalized cognitive engine based on your goals. How can I help you today?",
    agentType: "Orchestrator"
  }];
  const [messages, setMessages] = useState(defaultWelcome);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<string | null>(null);
  const currentStreamingMessageRef = useRef<string | null>(null);
  
  const [currentAgent, setCurrentAgent] = useState("Tutor");
  const currentAgentRef = useRef<string>("Tutor");
  
  const [interactionMode, setInteractionMode] = useState<"text" | "voice" | "video">("text");
  
  const scrollRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const fallbackSessionId = useRef(`session_${Date.now()}`);
  const activeSessionId = sessionId || fallbackSessionId.current;
  const audioCtxRef = useRef<AudioContext | null>(null);
  const nextPlayTimeRef = useRef<number>(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const playAudioChunk = async (base64Chunk: string) => {
    if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
    }
    const ctx = audioCtxRef.current;
    if (ctx.state === 'suspended') await ctx.resume();
    
    const binaryString = atob(base64Chunk);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    
    const view = new DataView(bytes.buffer);
    const floatArray = new Float32Array(bytes.length / 2);
    for (let i = 0; i < floatArray.length; i++) {
        floatArray[i] = view.getInt16(i * 2, true) / 32768.0;
    }
    
    const audioBuffer = ctx.createBuffer(1, floatArray.length, 16000);
    audioBuffer.getChannelData(0).set(floatArray);
    
    const source = ctx.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(ctx.destination);
    
    if (nextPlayTimeRef.current < ctx.currentTime) {
        nextPlayTimeRef.current = ctx.currentTime;
    }
    
    source.start(nextPlayTimeRef.current);
    nextPlayTimeRef.current += audioBuffer.duration;
  };

  useEffect(() => {
    let ws: WebSocket | null = null;
    
    const initSocket = async () => {
      const wsBaseUrl = process.env.NEXT_PUBLIC_BACKEND_WS_URL || "ws://localhost:8000";
      const wsUrl = `${wsBaseUrl}/ws/session/${activeSessionId}`;
      ws = new WebSocket(wsUrl);

      ws.onopen = () => console.log("[WS] Connected to Aion Bidi-Stream");
      ws.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        
        // Handle Custom Status Messages (e.g. agent switches)
        if (data.type === "status" && data.agent) {
            const agentMap: Record<string, string> = {
                "socratic_tutor": "Tutor",
                "curriculum_planner": "Planner",
                "rag_knowledge": "RAG",
                "silent_assessor": "Assessor",
                "profile_manager": "Profile",
                "deep_search": "Search"
            };
            const formattedAgentName = agentMap[data.agent] || (data.agent.charAt(0).toUpperCase() + data.agent.slice(1));
            currentAgentRef.current = formattedAgentName;
            setCurrentAgent(formattedAgentName);
            if (onAgentChange) onAgentChange(data.agent);
            setIsTyping(true);
            return;
        }

        // Parse ADK Response Parts (Gemini Multimodal Live format)
        // Check for serverContent -> modelTurn -> parts
        const modelTurn = data.serverContent?.modelTurn;
        if (modelTurn && modelTurn.parts) {
          modelTurn.parts.forEach(async (part: any) => {
            if (part.text) {
              currentStreamingMessageRef.current = (currentStreamingMessageRef.current || "") + part.text;
              setCurrentStreamingMessage(currentStreamingMessageRef.current);
              setIsTyping(true);
            } else if (part.inlineData) {
              await playAudioChunk(part.inlineData.data);
              setIsTyping(true);
            }
          });
        }
        
        // Handle direct tokens/audio (legacy or fallback)
        if (data.type === "token") {
            currentStreamingMessageRef.current = (currentStreamingMessageRef.current || "") + data.content;
            setCurrentStreamingMessage(currentStreamingMessageRef.current);
            setIsTyping(true);
        } else if (data.type === "audio") {
            await playAudioChunk(data.data);
            setIsTyping(true);
        } else if (data.type === "progress_update") {
            // Update global state
            const store = (await import("@/lib/store")).useAppStore.getState();
            if (data.payload?.overall_progress !== undefined) {
               store.setProgress(data.payload.overall_progress);
            }
            if (data.payload?.topic && data.payload?.mastery !== undefined) {
               store.updateTopicMastery(data.payload.topic, data.payload.mastery);
            }
            return;
        }

        // Check for session completion or turn-switch
        const serverContent = data.serverContent;
        if (serverContent?.turnComplete || data.finishReason === "STOP") {
          setIsTyping(false);
          if (currentStreamingMessageRef.current) {
            setMessages(prev => [
              ...prev, 
              {
                id: Date.now().toString(),
                role: "assistant",
                content: currentStreamingMessageRef.current!,
                agentType: currentAgentRef.current
              }
            ]);
            currentStreamingMessageRef.current = null;
            setCurrentStreamingMessage(null);
          }
        }
      };

      ws.onclose = () => console.log("[WS] Disconnected");
      ws.onerror = (err) => console.error("[WS] Error:", err);
      socketRef.current = ws;
    };
    
    initSocket();

    return () => {
      if (ws) ws.close();
      else if (socketRef.current) socketRef.current.close();
    };
  }, [userId, activeSessionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping, currentStreamingMessage]);

  const startRecording = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mimeType = 'audio/webm;codecs=opus';
        const recorder = new MediaRecorder(stream, { mimeType });
        
        recorder.ondataavailable = async (e) => {
            if (e.data.size > 0 && socketRef.current?.readyState === WebSocket.OPEN) {
                const reader = new FileReader();
                reader.readAsDataURL(e.data);
                reader.onloadend = () => {
                    const result = reader.result as string;
                    const base64data = result.split(',')[1];
                    socketRef.current?.send(JSON.stringify({
                        realtime_input: {
                            media_chunks: [{
                                mime_type: mimeType,
                                data: base64data
                            }]
                        }
                    }));
                };
            }
        };
        
        recorder.start(500);
        mediaRecorderRef.current = recorder;
    } catch (e) {
        console.error("Mic error:", e);
    }
  };

  const stopRecording = () => {
      if (mediaRecorderRef.current) {
          mediaRecorderRef.current.stop();
          mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop());
      }
  };

  useEffect(() => {
      if (interactionMode === "voice") {
          startRecording();
      } else {
          stopRecording();
      }
      return () => stopRecording();
  }, [interactionMode]);

  const handleSend = () => {
    if (!input.trim() || !socketRef.current) return;
    
    const userMsg = { id: Date.now().toString(), role: "user", content: input, agentType: "User" };
    setMessages(prev => [...prev, userMsg]);
    
    // Send via WebSocket in format expected by orchestrator
    socketRef.current.send(JSON.stringify({
      message: input,
      user_id: userId,
      profile: profile 
    }));

    setInput("");
    setIsTyping(true);
  };


  return (
    <Card className="flex flex-col h-[600px] border-slate-800 bg-slate-950/50 backdrop-blur shadow-2xl overflow-hidden">
      <CardHeader className="border-b border-slate-800 bg-slate-900/50">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-xl font-medium tracking-tight text-white">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            Aion Tutor
          </CardTitle>
          <div className="flex gap-2">
            <div className="flex bg-slate-950 rounded-lg p-1 border border-slate-800 mr-2">
              <button 
                onClick={() => setInteractionMode("text")}
                className={`p-1.5 rounded-md transition-all ${interactionMode === 'text' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                title="Text Chat"
              >
                <MessageSquare className="w-4 h-4" />
              </button>
              <button 
                onClick={() => setInteractionMode("voice")}
                className={`p-1.5 rounded-md transition-all ${interactionMode === 'voice' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                title="Real-time Voice"
              >
                <Mic className="w-4 h-4" />
              </button>
              <button 
                onClick={() => setInteractionMode("video")}
                className={`p-1.5 rounded-md transition-all ${interactionMode === 'video' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                title="Video Interaction"
              >
                <Video className="w-4 h-4" />
              </button>
            </div>
            <div className="flex gap-2 items-center text-xs">
                <Badge variant="outline" className="border-emerald-500 text-emerald-400 bg-emerald-500/10 animate-pulse hidden sm:flex">Live WebSocket</Badge>
                <Badge variant="outline" className="border-indigo-500 text-indigo-400 bg-indigo-500/10 hidden sm:flex">ADK Swarm Active</Badge>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 p-0 relative flex flex-col min-h-0">
        {interactionMode === "video" && (
           <div className="absolute inset-0 z-10 bg-slate-900/90 backdrop-blur-sm flex flex-col items-center justify-center p-6 border-b border-slate-800">
               <div className="w-full max-w-md aspect-video bg-slate-950 rounded-2xl border border-indigo-500/30 shadow-[0_0_30px_rgba(99,102,241,0.1)] flex items-center justify-center relative overflow-hidden">
                   <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-cyan-500/5" />
                   <div className="w-24 h-24 rounded-full bg-indigo-600/20 flex flex-col items-center justify-center animate-pulse border border-indigo-500/50">
                       <Video className="w-10 h-10 text-indigo-400 mb-1" />
                   </div>
                   <div className="absolute bottom-4 left-4 flex gap-2">
                       <div className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                       <span className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">Video Feed Active</span>
                   </div>
               </div>
               <p className="text-slate-400 text-sm mt-6 text-center max-w-xs">
                   Your multi-modal video session is ready. Aion is analyzing your expressions and environment.
               </p>
           </div>
        )}

        {interactionMode === "voice" && (
           <div className="absolute inset-0 z-10 bg-slate-900/90 backdrop-blur-sm flex flex-col items-center justify-center p-6 border-b border-slate-800">
               <div className="w-full max-w-sm p-8 bg-slate-950 rounded-3xl border border-indigo-500/30 shadow-[0_0_40px_rgba(99,102,241,0.1)] flex flex-col items-center justify-center relative">
                   <div className="relative mb-6">
                       <div className="absolute inset-0 bg-indigo-500 rounded-full blur-2xl opacity-20 animate-pulse" />
                       <div className="w-24 h-24 rounded-full bg-indigo-600/30 flex items-center justify-center border-2 border-indigo-400 relative z-10">
                           <Mic className="w-10 h-10 text-indigo-300" />
                       </div>
                   </div>
                   
                   <div className="flex items-center gap-1 h-8 mb-4">
                       {[1, 2, 3, 4, 5, 4, 3, 2, 1].map((h, i) => (
                           <div key={i} className="w-1.5 bg-indigo-400 rounded-full animate-pulse transition-all duration-75" style={{ height: h * 6 }} />
                       ))}
                   </div>

                   <span className="text-xs uppercase font-bold text-indigo-300 tracking-widest">Listening...</span>
               </div>
           </div>
        )}

        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          <div className="flex flex-col gap-6">
            {messages.map((m) => (
              <div key={m.id} className={`flex gap-4 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
                <Avatar className="w-10 h-10 border border-slate-700 bg-slate-800 shadow-sm shrink-0">
                  {m.role === "user" ? (
                    <AvatarFallback className="bg-indigo-600 text-white"><User className="w-5 h-5" /></AvatarFallback>
                  ) : (
                    <AvatarFallback className="bg-slate-800 text-indigo-400"><Bot className="w-5 h-5" /></AvatarFallback>
                  )}
                </Avatar>
                
                <div className={`flex flex-col gap-1 max-w-[80%] ${m.role === "user" ? "items-end" : "items-start"}`}>
                  <div className="flex items-center gap-2 px-1">
                    <span className="text-xs font-medium text-slate-400">{m.role === "user" ? "You" : m.agentType}</span>
                  </div>
                  <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                    m.role === "user" 
                      ? "bg-indigo-600 text-white rounded-tr-sm" 
                      : "bg-slate-800/80 text-slate-200 border border-slate-700 rounded-tl-sm shadow-sm"
                  }`}>
                    {m.content}
                  </div>
                </div>
              </div>
            ))}
            
            {currentStreamingMessage && (
              <div className="flex gap-4">
                <Avatar className="w-10 h-10 border border-slate-700 bg-slate-800 shrink-0">
                  <AvatarFallback className="bg-slate-800 text-indigo-400"><Bot className="w-5 h-5" /></AvatarFallback>
                </Avatar>
                <div className="flex flex-col gap-1 max-w-[80%] items-start">
                  <div className="flex items-center gap-2 px-1">
                    <span className="text-xs font-medium text-slate-400">{currentAgent}</span>
                  </div>
                  <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-slate-800/80 text-slate-200 border border-slate-700 shadow-sm">
                    {currentStreamingMessage}
                    <span className="inline-block w-1.5 h-4 ml-1 bg-indigo-500 animate-pulse align-middle" />
                  </div>
                </div>
              </div>
            )}

            {isTyping && !currentStreamingMessage && (
              <div className="flex gap-4">
                <Avatar className="w-10 h-10 border border-slate-700 bg-slate-800 shrink-0">
                  <AvatarFallback className="bg-slate-800 text-indigo-400"><Bot className="w-5 h-5" /></AvatarFallback>
                </Avatar>
                <div className="flex flex-col gap-1 items-start">
                   <div className="flex items-center gap-2 px-1">
                    <span className="text-xs font-medium text-slate-400">{currentAgent}</span>
                  </div>
                  <div className="flex items-center gap-1 bg-slate-800/50 px-4 py-3 rounded-2xl rounded-tl-sm border border-slate-800">
                    <div className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce" />
                    <div className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce delay-150" />
                    <div className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce delay-300" />
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
      
      <CardFooter className="p-4 border-t border-slate-800 bg-slate-900/50">
        <form 
          className="flex w-full items-center gap-2 relative"
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
        >
          <Input 
            type="text" 
            placeholder="Ask about Azure (using AWS analogies)..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isTyping}
            className="flex-1 bg-slate-950 border-slate-700 text-white placeholder:text-slate-500 h-12 rounded-xl px-4 focus-visible:ring-indigo-500"
          />
          <Button 
            type="submit" 
            size="icon" 
            disabled={isTyping || !input.trim()}
            className="absolute right-1 bg-indigo-600 hover:bg-indigo-700 text-white h-10 w-10 rounded-lg transition-all"
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}
