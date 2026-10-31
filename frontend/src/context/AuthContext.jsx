import { createContext, useEffect, useState } from "react";
import { api, tokenStore } from "../services/api";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(tokenStore.get());
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(tokenStore.get())); // true while we check a saved token

  // On page load: if a token is saved, ask the API who it belongs to.
  useEffect(() => {
    if (!tokenStore.get()) return;
    api
      .me()
      .then(setUser)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  // The API service fires this when it gets a 401 for a saved token.
  useEffect(() => {
    const onExpired = () => {
      tokenStore.clear();
      setToken(null);
      setUser(null);
    };
    window.addEventListener("auth:expired", onExpired);
    return () => window.removeEventListener("auth:expired", onExpired);
  }, []);

  async function login(email, password) {
    const data = await api.login(email, password);
    tokenStore.set(data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  }

  async function register(payload) {
    await api.register(payload);
    return login(payload.email, payload.password);
  }

  function logout() {
    tokenStore.clear();
    setToken(null);
    setUser(null);
  }

  const value = { user, token, role: user?.role ?? null, loading, login, register, logout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}