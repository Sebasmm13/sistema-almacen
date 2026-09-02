import { PerfilesPage } from "./pages/PerfilesPage";

export default function App() {
  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <span className="eyebrow">Módulo de seguridad</span>
          <h1>Sistema de gestión de almacén</h1>
        </div>
        <span className="profile-chip">Perfil activo: desarrollo</span>
      </header>
      <PerfilesPage />
    </main>
  );
}

