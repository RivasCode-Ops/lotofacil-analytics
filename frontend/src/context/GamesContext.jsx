import { createContext, useContext, useState } from "react";

const GamesContext = createContext(null);

export function GamesProvider({ children }) {
  const [games, setGames] = useState([]);
  const [lastGeneratedAt, setLastGeneratedAt] = useState(null);

  return (
    <GamesContext.Provider value={{ games, setGames, lastGeneratedAt, setLastGeneratedAt }}>
      {children}
    </GamesContext.Provider>
  );
}

export function useGames() {
  const ctx = useContext(GamesContext);
  if (!ctx) throw new Error("useGames deve ser usado dentro de GamesProvider");
  return ctx;
}
