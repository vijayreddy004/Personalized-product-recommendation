import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AuthContextType {
  userId: number | null;
  setUserId: (id: number | null) => void;
  isAuthenticated: boolean;
  login: (id: number) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [userId, setUserId] = useState<number | null>(null);

  const login = (id: number) => {
    setUserId(id);
  };

  const logout = () => {
    setUserId(null);
  };

  return (
    <AuthContext.Provider value={{
      userId,
      setUserId,
      isAuthenticated: userId !== null,
      login,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}