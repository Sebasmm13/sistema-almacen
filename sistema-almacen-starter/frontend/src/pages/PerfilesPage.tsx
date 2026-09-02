import { FormEvent, useCallback, useEffect, useState } from "react";

import { api } from "../services/api";
import type { Perfil, PerfilPayload, PerfilesResponse } from "../types/perfil";

const emptyForm: PerfilPayload = { codigo: "", nombre: "", descripcion: "" };

export function PerfilesPage() {
  const [perfiles, setPerfiles] = useState<Perfil[]>([]);
  const [form, setForm] = useState<PerfilPayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadProfiles = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get<PerfilesResponse>(
        "/perfiles?incluir_inactivos=true&per_page=100",
      );
      setPerfiles(data.items);
    } catch {
      setError("No se pudo conectar con Flask. Verifica que el backend esté activo.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadProfiles();
  }, [loadProfiles]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      if (editingId) {
        await api.put(`/perfiles/${editingId}`, form);
        setMessage("Perfil actualizado correctamente.");
      } else {
        await api.post("/perfiles", form);
        setMessage("Perfil creado correctamente.");
      }
      setForm(emptyForm);
      setEditingId(null);
      await loadProfiles();
    } catch (requestError: any) {
      setError(
        requestError?.response?.data?.message ?? "No se pudo guardar el perfil.",
      );
    }
  }

  function edit(perfil: Perfil) {
    setEditingId(perfil.id_perfil);
    setForm({
      codigo: perfil.codigo,
      nombre: perfil.nombre,
      descripcion: perfil.descripcion ?? "",
    });
    setMessage("");
    setError("");
  }

  async function toggleStatus(perfil: Perfil) {
    setError("");
    await api.patch(`/perfiles/${perfil.id_perfil}/estado`, {
      activo: !perfil.activo,
    });
    setMessage(perfil.activo ? "Perfil desactivado." : "Perfil activado.");
    await loadProfiles();
  }

  return (
    <section className="workspace-grid">
      <form className="card form-card" onSubmit={submit}>
        <div className="section-heading">
          <span className="eyebrow">RF-01</span>
          <h2>{editingId ? "Editar perfil" : "Nuevo perfil"}</h2>
        </div>

        <label>
          Código
          <input
            required
            pattern="[a-z][a-z0-9_]*"
            value={form.codigo}
            onChange={(event) =>
              setForm({ ...form, codigo: event.target.value.toLowerCase() })
            }
            placeholder="ejemplo: tecnico"
          />
        </label>
        <label>
          Nombre
          <input
            required
            maxLength={100}
            value={form.nombre}
            onChange={(event) => setForm({ ...form, nombre: event.target.value })}
          />
        </label>
        <label>
          Descripción
          <textarea
            maxLength={250}
            rows={4}
            value={form.descripcion ?? ""}
            onChange={(event) =>
              setForm({ ...form, descripcion: event.target.value })
            }
          />
        </label>

        <div className="actions">
          <button type="submit">{editingId ? "Guardar cambios" : "Crear perfil"}</button>
          {editingId && (
            <button
              type="button"
              className="secondary"
              onClick={() => {
                setEditingId(null);
                setForm(emptyForm);
              }}
            >
              Cancelar
            </button>
          )}
        </div>
        {message && <p className="notice success">{message}</p>}
        {error && <p className="notice error">{error}</p>}
      </form>

      <section className="card list-card">
        <div className="section-heading list-heading">
          <div>
            <span className="eyebrow">Mantenimiento</span>
            <h2>Perfiles registrados</h2>
          </div>
          <button className="secondary" onClick={() => void loadProfiles()}>
            Actualizar
          </button>
        </div>

        {loading ? (
          <p>Cargando...</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Código</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {perfiles.map((perfil) => (
                  <tr key={perfil.id_perfil}>
                    <td>
                      <strong>{perfil.nombre}</strong>
                      <small>{perfil.descripcion || "Sin descripción"}</small>
                    </td>
                    <td><code>{perfil.codigo}</code></td>
                    <td>
                      <span className={perfil.activo ? "status active" : "status inactive"}>
                        {perfil.activo ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td className="row-actions">
                      <button className="link-button" onClick={() => edit(perfil)}>
                        Editar
                      </button>
                      <button
                        className="link-button danger"
                        onClick={() => void toggleStatus(perfil)}
                      >
                        {perfil.activo ? "Desactivar" : "Activar"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </section>
  );
}

