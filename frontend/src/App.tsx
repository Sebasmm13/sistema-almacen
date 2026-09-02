import { useState } from "react";

import { PerfilesPage } from "./pages/PerfilesPage";
import { UsuariosPage } from "./pages/UsuariosPage";

export default function App() {
  const [module, setModule] = useState<"perfiles" | "usuarios">("perfiles");

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <span className="eyebrow">Módulo de seguridad</span>
          <h1>Sistema de gestión de almacén</h1>
        </div>
        <span className="profile-chip">Perfil activo: desarrollo</span>
      </header>
      <nav className="module-nav" aria-label="Módulos de seguridad">
        <button
          className={module === "perfiles" ? "active" : ""}
          onClick={() => setModule("perfiles")}
        >
          Perfiles
        </button>
        <button
          className={module === "usuarios" ? "active" : ""}
          onClick={() => setModule("usuarios")}
        >
          Usuarios
        </button>
      </nav>
      {module === "perfiles" ? <PerfilesPage /> : <UsuariosPage />}
    </main>
  );
}
