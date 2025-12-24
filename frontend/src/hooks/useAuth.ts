import { useCallback, useMemo, useState } from "react";
import type { AuthState, User } from "../types";

const ADMIN_EMAIL = (import.meta.env.VITE_ADMIN_EMAIL || "").trim().toLowerCase();

export function useAuth(): AuthState {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback((email: string) => {
    const normalized = email.trim().toLowerCase();

    if (!normalized.endsWith("@neemba.com")) {
      setError("Accès limité aux emails @neemba.com");
      setUser(null);
      return;
    }

    const role = ADMIN_EMAIL && normalized === ADMIN_EMAIL ? "admin" : "guest";
    setUser({ email: normalized, role });
    setError(null);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setError(null);
  }, []);

  const isAdmin = useMemo(() => user?.role === "admin", [user]);

  return { user, isAdmin, error, login, logout };
}

