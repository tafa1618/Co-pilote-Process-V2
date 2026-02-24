/**
 * Centralized configuration for the frontend application.
 * Environment variables are managed via Vite (import.meta.env).
 */

export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";
export const ADMIN_EMAIL = (import.meta.env.VITE_ADMIN_EMAIL || "admin@neemba.com").trim().toLowerCase();
export const ADMIN_PASSWORD = import.meta.env.VITE_ADMIN_PASSWORD || "";

// Standard Neemba Branding Colors
export const COLORS = {
    YELLOW: "#FFD700",
    ONYX: "#353935",
    BLACK: "#000000",
};
