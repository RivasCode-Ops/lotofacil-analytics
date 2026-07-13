function StatCard({ label, value, hint }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <p className="text-slate-400 text-sm">{label}</p>
      <p className="text-2xl font-bold text-slate-100 mt-1">{value}</p>
      {hint && <p className="text-xs text-slate-500 mt-1">{hint}</p>}
    </div>
  );
}

export default StatCard;
