import { Link } from "react-router-dom";
import { useGames } from "../context/GamesContext";

function scoreColor(total) {
  if (total >= 85) return "text-emerald-400";
  if (total >= 70) return "text-yellow-400";
  return "text-red-400";
}

function Results() {
  const { games, lastGeneratedAt } = useGames();

  if (!games.length) {
    return (
      <div className="p-6 text-center space-y-4">
        <p className="text-slate-400">Nenhum jogo gerado ainda.</p>
        <Link to="/gerar" className="text-emerald-400 underline">
          Gerar jogos
        </Link>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-baseline justify-between">
        <h1 className="text-2xl font-bold text-slate-100">Resultados</h1>
        {lastGeneratedAt && <span className="text-xs text-slate-500">gerado em {lastGeneratedAt}</span>}
      </div>

      <div className="grid gap-4">
        {games.map((item, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-slate-400 text-sm">Jogo {idx + 1}</span>
              <span className={`text-xl font-bold ${scoreColor(item.total)}`}>{item.total.toFixed(1)}</span>
            </div>

            <div className="flex flex-wrap gap-2 mb-3">
              {item.game.map((num) => (
                <span
                  key={num}
                  className="w-8 h-8 flex items-center justify-center rounded-full bg-slate-800 text-slate-100 text-sm font-medium"
                >
                  {String(num).padStart(2, "0")}
                </span>
              ))}
            </div>

            <div className="grid grid-cols-5 gap-2 text-xs text-slate-500">
              {Object.entries(item.criterios).map(([nome, valor]) => (
                <div key={nome}>
                  <p className="capitalize">{nome}</p>
                  <p className="text-slate-300">{valor.toFixed(0)}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Results;
