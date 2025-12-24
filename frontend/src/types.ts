export type UserRole = "admin" | "guest";

export interface User {
  email: string;
  role: UserRole;
}

export interface UploadKpiResponse {
  message: string;
  kpi: {
    rows: number;
    columns: string[];
    role: UserRole;
    owner: string;
  };
}

export interface AuthState {
  user: User | null;
  isAdmin: boolean;
  error: string | null;
  login: (email: string) => void;
  logout: () => void;
}

