import { useCallback, useState } from "react";
import type { UploadKpiResponse, User } from "../types";

import { BACKEND_URL } from "../config/constants";
const DEFAULT_EMAIL = (import.meta.env.VITE_ADMIN_EMAIL || "admin@neemba.com").trim().toLowerCase();
const DEFAULT_ADMIN_PASSWORD = import.meta.env.VITE_ADMIN_PASSWORD || "";

interface UploadState {
  loading: boolean;
  error: string | null;
  result: UploadKpiResponse | null;
}

export function useUpload(user: User | null) {
  const [state, setState] = useState<UploadState>({
    loading: false,
    error: null,
    result: null,
  });

  const upload = useCallback(
    async (file: File) => {
      setState({ loading: true, error: null, result: null });

      const formData = new FormData();
      formData.append("file", file);

      const email = (user?.email || DEFAULT_EMAIL).trim().toLowerCase();
      const adminPwd = user?.adminPassword || DEFAULT_ADMIN_PASSWORD;

      try {
        const response = await fetch(`${BACKEND_URL}/kpi/productivite/upload`, {
          method: "POST",
          headers: {
            "X-User-Email": email,
            ...(adminPwd ? { "X-Admin-Password": adminPwd } : {}),
          },
          body: formData,
        });

        if (!response.ok) {
          const detail = await response.json().catch(() => ({}));
          throw new Error(detail.detail || "Échec du téléversement");
        }

        const payload: UploadKpiResponse = await response.json();
        setState({ loading: false, error: null, result: payload });
      } catch (error) {
        const message = error instanceof Error ? error.message : "Erreur inconnue";
        setState({ loading: false, error: message, result: null });
      }
    },
    [user],
  );

  return {
    upload,
    loading: state.loading,
    error: state.error,
    result: state.result,
  };
}

