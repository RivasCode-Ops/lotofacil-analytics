import { BrowserRouter, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import { GamesProvider } from "./context/GamesContext";
import Dashboard from "./pages/Dashboard";
import Generate from "./pages/Generate";
import Results from "./pages/Results";
import SavedGames from "./pages/SavedGames";

function App() {
  return (
    <GamesProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-950 text-slate-100">
          <Navbar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/gerar" element={<Generate />} />
            <Route path="/resultados" element={<Results />} />
            <Route path="/meus-jogos" element={<SavedGames />} />
          </Routes>
        </div>
      </BrowserRouter>
    </GamesProvider>
  );
}

export default App;
