import { useCallback, useMemo, useState } from "react";
import type { AuthState, User } from "../types";

import { ADMIN_EMAIL, ADMIN_PASSWORD } from "../config/constants";

export function useAuth(): AuthState {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const raw = sessionStorage.getItem("auth:user");
      return raw ? (JSON.parse(raw) as User) : null;
    } catch {
      return null;
    }
  });
  const [error, setError] = useState<string | null>(null);

  const login = useCallback((email: string, adminPassword?: string) => {
    const normalized = email.trim().toLowerCase();

    if (!normalized.endsWith("@neemba.com")) {
      setError("Accès limité aux emails @neemba.com");
      setUser(null);
      return;
    }

    const isAdminEmail = ADMIN_EMAIL && normalized === ADMIN_EMAIL;
    if (isAdminEmail && !(adminPassword || ADMIN_PASSWORD)) {
      setError("Mot de passe admin requis");
      setUser(null);
      return;
    }

    const role: User["role"] = isAdminEmail ? "admin" : "guest";
    const nextUser: User = { email: normalized, role, adminPassword: adminPassword || ADMIN_PASSWORD };
    setUser(nextUser);
    try {
      sessionStorage.setItem("auth:user", JSON.stringify(nextUser));
    } catch {
      /* ignore */
    }
    setError(null);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setError(null);
    try {
      sessionStorage.removeItem("auth:user");
    } catch {
      /* ignore */
    }
  }, []);

  const isAdmin = useMemo(() => user?.role === "admin", [user]);

  return { user, isAdmin, error, login, logout };
}

