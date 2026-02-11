import { ArrowLeft, User, LayoutDashboard, Calculator } from "lucide-react";
import { AuthState } from "../types";
import { SepSimulator } from "../components/sep/SepSimulator";
import { ManagerChatAgent } from "../components/sep/ManagerChatAgent";
import { useState } from "react";

export function ManagerView({ auth, onBack }: { auth: AuthState; onBack: () => void }) {
    const [activeTab, setActiveTab] = useState<"simulator" | "dashboard">("simulator");

    return (
        <div className="flex flex-col h-screen overflow-hidden bg-gradient-to-br from-black via-zinc-900 to-black">
            {/* Header */}
            <div className="h-16 border-b border-cat-yellow/20 bg-black/50 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-10">
                <div className="flex items-center gap-4">
                    <button
                        onClick={onBack}
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors text-sand"
                    >
                        <ArrowLeft size={20} />
                    </button>
                    <h1 className="text-xl font-bold text-white flex items-center gap-2">
                        <User className="text-cat-yellow" />
                        Manager Digital Twin
                    </h1>
                </div>

                <div className="flex bg-onyx/50 p-1 rounded-lg border border-white/10">
                    <button
                        onClick={() => setActiveTab("simulator")}
                        className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === "simulator" ? "bg-cat-yellow text-onyx shadow-lg" : "text-sand hover:text-white"}`}
                    >
                        <Calculator size={16} /> Simulateur & AI
                    </button>
                    <button
                        onClick={() => setActiveTab("dashboard")}
                        className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === "dashboard" ? "bg-cat-yellow text-onyx shadow-lg" : "text-sand hover:text-white"}`}
                    >
                        <LayoutDashboard size={16} /> Dashboard
                    </button>
                </div>
            </div>

            {/* Content Content */}
            <div className="flex-1 overflow-hidden relative">
                <div className="absolute inset-0 p-6 overflow-y-auto">
                    <div className="max-w-[1800px] mx-auto h-full flex flex-col lg:flex-row gap-6">

                        {/* Left: Chat Agent - 1/3 width */}
                        <div className="lg:w-1/3 h-[600px] lg:h-full min-h-[500px]">
                            <ManagerChatAgent />
                        </div>

                        {/* Right: Simulator - 2/3 width */}
                        <div className="lg:w-2/3 h-full">
                            <SepSimulator />
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}

export default ManagerView;
