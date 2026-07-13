import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function FrequencyChart({ frequency, classification }) {
  const quentes = new Set(classification?.quentes ?? []);
  const frios = new Set(classification?.frios ?? []);

  const data = Object.entries(frequency ?? {})
    .map(([numero, vezes]) => ({ numero: Number(numero), vezes }))
    .sort((a, b) => a.numero - b.numero);

  const colorFor = (numero) => {
    if (quentes.has(numero)) return "#f97316";
    if (frios.has(numero)) return "#38bdf8";
    return "#64748b";
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <p className="text-slate-300 font-semibold mb-3">Frequência dos números</p>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="numero" stroke="#64748b" fontSize={12} />
          <YAxis stroke="#64748b" fontSize={12} />
          <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #1e293b" }} />
          <Bar dataKey="vezes">
            {data.map((entry) => (
              <Cell key={entry.numero} fill={colorFor(entry.numero)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex gap-4 mt-3 text-xs text-slate-400">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-orange-500 inline-block" /> quente
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-slate-500 inline-block" /> médio
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-sky-400 inline-block" /> frio
        </span>
      </div>
    </div>
  );
}

export default FrequencyChart;
