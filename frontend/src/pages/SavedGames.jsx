import { useEffect, useState } from "react";
import { api } from "../services/api";

function hitsColor(hits) {
  if (hits === null || hits === undefined) return "text-slate-500";
  if (hits >= 14) return "text-emerald-400";
  if (hits >= 11) return "text-yellow-400";
  return "text-slate-400";
}

function SavedGames() {
  const [savedGames, setSavedGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState(null);
  const [checkMessage, setCheckMessage] = useState(null);

  const load = () => {
    setLoading(true);
    api
      .get("/saved-games")
      .then((res) => setSavedGames(res.data))
      .catch(() => setError("Não foi possível carregar os jogos salvos."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleCheck = async () => {
    setChecking(true);
    setCheckMessage(null);
    try {
      const res = await api.post("/saved-games/check");
      setCheckMessage(
        res.data.checked_now > 0
          ? `${res.data.checked_now} jogo(s) conferido(s) agora. ${res.data.still_pending} ainda aguardando o concurso sair.`
          : `Nenhum concurso novo disponível ainda. ${res.data.still_pending} jogo(s) aguardando.`
      );
      load();
    } catch (err) {
      setCheckMessage(err.response?.data?.detail ?? "Erro ao conferir os jogos.");
    } finally {
      setChecking(false);
    }
  };

  if (loading) return <p className="text-slate-400 p-6">Carregando...</p>;
  if (error) return <p className="text-red-400 p-6">{error}</p>;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-100">Meus Jogos</h1>
        <button
          onClick={handleCheck}
          disabled={checking}
          className="bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 font-semibold rounded-lg px-4 py-2 text-sm transition-colors"
        >
          {checking ? "Conferindo..." : "Conferir resultados"}
        </button>
      </div>

      {checkMessage && <p className="text-sm text-slate-400">{checkMessage}</p>}

      {!savedGames.length && (
        <p className="text-slate-400">Nenhum jogo salvo ainda — gere jogos e clique em "Salvar jogo do dia".</p>
      )}

      <div className="grid gap-4">
        {savedGames.map((entry) => (
          <div key={entry.id} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-slate-400 text-sm">Concurso {entry.target_contest}</span>
              {entry.checked ? (
                <span className={`text-xl font-bold ${hitsColor(entry.hits)}`}>{entry.hits} acertos</span>
              ) : (
                <span className="text-xs text-slate-500 bg-slate-800 rounded-full px-3 py-1">pendente</span>
              )}
            </div>

            <div className="flex flex-wrap gap-2 mb-2">
              {entry.numbers.map((num) => (
                <span
                  key={num}
                  className="w-8 h-8 flex items-center justify-center rounded-full bg-slate-800 text-slate-100 text-sm font-medium"
                >
                  {String(num).padStart(2, "0")}
                </span>
              ))}
            </div>

            <p className="text-xs text-slate-500">
              score {entry.score.toFixed(1)} · salvo em {new Date(entry.created_at).toLocaleString("pt-BR")}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SavedGames;
