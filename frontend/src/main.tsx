import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
console.log("Main.tsx executing...");

import ErrorBoundary from "./components/ErrorBoundary";

try {
  const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);
  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </React.StrictMode>,
  );
  console.log("React Render called");
} catch (e) {
  console.error("React Render failed", e);
}
