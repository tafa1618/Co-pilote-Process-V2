import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Sparkles } from "lucide-react";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
}

const SUGGESTED_QUESTIONS = [
    "Quelle a été la productivité équipe C au Q4?",
    "Combien d'OR clôturer pour LLTI < 7j?",
    "Quel est notre score SEP actuel?",
    "Montre moi l'évolution du Tech Capacity"
];

export function ManagerChatAgent() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "1",
            role: "assistant",
            content: "Bonjour Moustapha ! Je suis votre assistant digital SEP. Je peux analyser vos données, simuler des scores ou répondre à vos questions sur la performance. Que voulez-vous savoir aujourd'hui ?",
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async (text: string = input) => {
        if (!text.trim()) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: "user",
            content: text,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setIsTyping(true);

        // Mock AI Response
        setTimeout(() => {
            const aiMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: generateMockResponse(text),
                timestamp: new Date()
            };
            setMessages(prev => [...prev, aiMsg]);
            setIsTyping(false);
        }, 1500);
    };

    const generateMockResponse = (query: string): string => {
        const q = query.toLowerCase();
        if (q.includes("productivité") && q.includes("équipe c")) {
            return "📊 **Productivité Équipe C - Q4 2024**\n\n• Résultat : **81.5%**\n• Tendance : 📈 +3.2% vs Q3\n• vs Target (82%) : -0.5%\n\nL'équipe est proche du niveau *Advanced*. Une légère amélioration sur les heures facturables (+40h) permettrait d'atteindre l'objectif.";
        }
        if (q.includes("llti") && q.includes("7")) {
            return "🎯 **Calcul Calcul Inverse LLTI**\n\nPour passer de **9.2j** à **< 7j** :\n\n📌 Vous devez clôturer environ **35 OR** actuellement en retard (>15 jours sans main d'œuvre).\n\nCela réduirait le numérateur de 330 jours cumulés.";
        }
        if (q.includes("score")) {
            return "🏆 **Score SEP Simulé Actuel**\n\n• Global : **68.5%** (🥈 Silver)\n• Foundation : 26.5/40\n• Services Growth : 42.0/60\n\nManque **6.5 points** pour le Gold. Focus prioritaire : **Inspection Rate**.";
        }
        return "Je vois que vous posez une question intéressante. Pour l'instant, je suis en mode démonstration, mais bientôt je serai connecté à vos données réelles pour répondre précisément à cette requête !";
    };

    return (
        <div className="flex flex-col h-full bg-onyx/30 rounded-xl overflow-hidden border border-white/10">
            {/* Header */}
            <div className="bg-black/40 p-4 border-b border-cat-yellow/20 flex items-center gap-3">
                <div className="p-2 bg-cat-yellow/20 rounded-lg">
                    <Bot className="text-cat-yellow" size={24} />
                </div>
                <div>
                    <h3 className="text-white font-bold">SEP Assistant AI</h3>
                    <p className="text-xs text-sand/60 flex items-center gap-1">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> En ligne
                    </p>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {messages.map(msg => (
                    <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === "user" ? "bg-cat-yellow text-onyx" : "bg-zinc-700 text-white"}`}>
                            {msg.role === "user" ? <User size={16} /> : <Bot size={16} />}
                        </div>
                        <div className={`max-w-[80%] p-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${msg.role === "user" ? "bg-cat-yellow/20 text-white rounded-tr-none border border-cat-yellow/30" : "bg-onyx text-sand/90 rounded-tl-none border border-white/10"}`}>
                            {msg.content}
                        </div>
                    </div>
                ))}

                {isTyping && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 bg-zinc-700 rounded-full flex items-center justify-center shrink-0">
                            <Bot size={16} className="text-white" />
                        </div>
                        <div className="bg-onyx p-3 rounded-2xl rounded-tl-none border border-white/10 flex gap-1 items-center">
                            <span className="w-1.5 h-1.5 bg-sand/50 rounded-full animate-bounce"></span>
                            <span className="w-1.5 h-1.5 bg-sand/50 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                            <span className="w-1.5 h-1.5 bg-sand/50 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                        </div>
                    </div>
                )}
            </div>

            {/* Suggestions */}
            <div className="p-2 bg-black/20 flex gap-2 overflow-x-auto no-scrollbar">
                {SUGGESTED_QUESTIONS.map((q, i) => (
                    <button
                        key={i}
                        onClick={() => handleSend(q)}
                        className="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-xs text-sand whitespace-nowrap transition-colors flex items-center gap-1"
                    >
                        <Sparkles size={12} className="text-cat-yellow" /> {q}
                    </button>
                ))}
            </div>

            {/* Input Area */}
            <div className="p-4 bg-black/40 border-t border-white/10">
                <div className="flex gap-2 relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSend()}
                        placeholder="Posez une question sur vos KPIs..."
                        className="w-full bg-onyx border border-white/20 rounded-xl pl-4 pr-12 py-3 text-white focus:border-cat-yellow focus:outline-none transition-all placeholder:text-zinc-600"
                    />
                    <button
                        onClick={() => handleSend()}
                        className="absolute right-2 top-2 p-1.5 bg-cat-yellow text-onyx rounded-lg hover:bg-cat-yellow/90 transition-colors"
                    >
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
}
