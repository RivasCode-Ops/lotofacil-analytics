import { useEffect, useState } from "react";
import FrequencyChart from "../components/FrequencyChart";
import StatCard from "../components/StatCard";
import { api } from "../services/api";

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/statistics")
      .then((res) => setStats(res.data))
      .catch(() =>
        setError("Não foi possível carregar as estatísticas. Rode a atualização de concursos primeiro.")
      )
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400 p-6">Carregando...</p>;
  if (error) return <p className="text-red-400 p-6">{error}</p>;
  if (!stats) return null;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-100">Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Concursos analisados" value={stats.total_concursos_analisados} />
        <StatCard label="Soma média" value={stats.soma_media.toFixed(1)} />
        <StatCard label="Pares (média)" value={stats.paridade.pares_media.toFixed(1)} />
        <StatCard label="Primos (média)" value={stats.primos.primos_media.toFixed(1)} />
      </div>

      <FrequencyChart frequency={stats.frequencia} classification={stats.classificacao} />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-orange-400 font-semibold mb-2">Quentes</p>
          <p className="text-slate-300">{stats.classificacao.quentes.join(", ")}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-slate-300 font-semibold mb-2">Médios</p>
          <p className="text-slate-300">{stats.classificacao.medios.join(", ")}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-sky-400 font-semibold mb-2">Frios</p>
          <p className="text-slate-300">{stats.classificacao.frios.join(", ")}</p>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
