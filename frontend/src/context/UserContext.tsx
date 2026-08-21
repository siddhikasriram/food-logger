import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import type { User } from "../api/types";

const STORAGE_KEY = "food-logger-user-id";

type UserContextValue = {
  ready: boolean;
  userId: number | null;
  user: User | null;
  setCurrentUserId: (userId: number) => void;
  refresh: () => Promise<void>;
};

const UserContext = createContext<UserContextValue | null>(null);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [userId, setUserId] = useState<number | null>(null);
  const [user, setUser] = useState<User | null>(null);

  const load = async (id: number | null) => {
    if (id === null) {
      setUser(null);
      return;
    }
    try {
      setUser(await api.getUser(id));
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      setUserId(null);
      setUser(null);
    }
  };

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    const parsed = stored ? Number(stored) : null;
    const initial = parsed && !Number.isNaN(parsed) ? parsed : null;
    setUserId(initial);
    void load(initial).finally(() => setReady(true));
  }, []);

  const setCurrentUserId = (id: number) => {
    localStorage.setItem(STORAGE_KEY, String(id));
    setUserId(id);
    void load(id);
  };

  const value = useMemo(
    () => ({
      ready,
      userId,
      user,
      setCurrentUserId,
      refresh: () => load(userId),
    }),
    [ready, userId, user],
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUser must be used within UserProvider");
  }
  return context;
}
