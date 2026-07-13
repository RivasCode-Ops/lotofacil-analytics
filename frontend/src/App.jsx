import { BrowserRouter, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import { GamesProvider } from "./context/GamesContext";
import Dashboard from "./pages/Dashboard";
import Generate from "./pages/Generate";
import Results from "./pages/Results";

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
          </Routes>
        </div>
      </BrowserRouter>
    </GamesProvider>
  );
}

export default App;
