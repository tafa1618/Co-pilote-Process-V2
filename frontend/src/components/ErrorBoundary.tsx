import React from "react";

class ErrorBoundary extends React.Component<any, { hasError: boolean; error: Error | null }> {
    constructor(props: any) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error) {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: any) {
        console.error("ErrorBoundary caught an error", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-black text-white p-8">
                    <div className="max-w-2xl w-full bg-gray-900 border border-red-500 rounded-xl p-8 shadow-2xl">
                        <h1 className="text-2xl font-bold text-red-500 mb-4">Une erreur est survenue</h1>
                        <p className="mb-4 text-gray-300">L'application n'a pas pu s'afficher correctement.</p>
                        <div className="bg-black/50 p-4 rounded-lg overflow-auto max-h-64 border border-gray-800">
                            <code className="font-mono text-sm text-red-300">
                                {this.state.error && this.state.error.toString()}
                            </code>
                        </div>
                        <button
                            onClick={() => window.location.reload()}
                            className="mt-6 px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
                        >
                            Recharger la page
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
