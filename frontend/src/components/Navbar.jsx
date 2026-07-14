import { NavLink } from "react-router-dom";

const linkClass = ({ isActive }) =>
  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
    isActive ? "bg-emerald-500 text-slate-950" : "text-slate-300 hover:bg-slate-800"
  }`;

function Navbar() {
  return (
    <nav className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
      <span className="text-lg font-bold text-slate-100">Lotofácil Analytics</span>
      <div className="flex gap-2">
        <NavLink to="/" end className={linkClass}>
          Dashboard
        </NavLink>
        <NavLink to="/gerar" className={linkClass}>
          Gerar Jogos
        </NavLink>
        <NavLink to="/resultados" className={linkClass}>
          Resultados
        </NavLink>
        <NavLink to="/meus-jogos" className={linkClass}>
          Meus Jogos
        </NavLink>
      </div>
    </nav>
  );
}

export default Navbar;
