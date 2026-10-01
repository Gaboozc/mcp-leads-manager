import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, getToken, setToken, setUnauthorizedHandler } from "./api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setTok] = useState(getToken());
  const [notice, setNotice] = useState(null);
  const navigate = useNavigate();

  const signOut = useCallback(
    (message = null) => {
      setToken(null);
      setTok(null);
      setNotice(message);
      navigate("/signin", { replace: true });
    },
    [navigate],
  );

  useEffect(() => setUnauthorizedHandler((msg) => signOut(msg)), [signOut]);

  const signIn = useCallback(
    async (email, password) => {
      const data = await api("/auth/login", { method: "POST", body: { email, password } });
      setToken(data.token);
      setTok(data.token);
      setNotice(null);
      navigate("/", { replace: true });
    },
    [navigate],
  );

  const value = useMemo(() => ({ token, signIn, signOut, notice }), [token, signIn, signOut, notice]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
