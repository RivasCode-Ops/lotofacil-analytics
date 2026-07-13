import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGames } from "../context/GamesContext";
import { api } from "../services/api";

function Generate() {
  const [n, setN] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { setGames, setLastGeneratedAt } = useGames();
  const navigate = useNavigate();

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.post(`/games/generate?n=${n}`);
      setGames(res.data);
      setLastGeneratedAt(new Date().toLocaleString("pt-BR"));
      navigate("/resultados");
    } catch (err) {
      setError(err.response?.data?.detail ?? "Erro ao gerar jogos.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-100">Gerar Jogos</h1>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <label className="block text-sm text-slate-400">
          Quantidade de jogos
          <input
            type="number"
            min={1}
            max={50}
            value={n}
            onChange={(e) => setN(Number(e.target.value))}
            className="mt-1 w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-100"
          />
        </label>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 font-semibold rounded-lg py-2 transition-colors"
        >
          {loading ? "Gerando..." : "Gerar Jogos"}
        </button>

        {error && <p className="text-red-400 text-sm">{error}</p>}
      </div>

      <p className="text-slate-500 text-sm">
        Cada jogo passa pelas regras (faixas, paridade, primos, frequência, repetição, soma) e pelos filtros
        eliminatórios (sequência, distribuição no volante) antes de ser pontuado e ranqueado.
      </p>
    </div>
  );
}

export default Generate;
