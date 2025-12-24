import { useCallback, useState } from "react";
import type { UploadKpiResponse, User } from "../types";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

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
      if (!user) {
        setState((prev) => ({ ...prev, error: "Utilisateur non authentifié" }));
        return;
      }

      setState({ loading: true, error: null, result: null });

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch(`${BACKEND_URL}/upload`, {
          method: "POST",
          headers: {
            "X-User-Email": user.email,
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

