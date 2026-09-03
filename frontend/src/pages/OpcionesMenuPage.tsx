import { FormEvent, useCallback, useEffect, useState } from "react";

import { api } from "../services/api";
import type {
  OpcionMenu,
  OpcionMenuPayload,
  OpcionesMenuResponse,
} from "../types/opcionMenu";

const emptyForm: OpcionMenuPayload = {
  codigo: "",
  nombre: "",
  ruta: "",
  descripcion: "",
  icono: "",
  id_padre: null,
  orden: 1,
};

export function OpcionesMenuPage() {
  const [opciones, setOpciones] = useState<OpcionMenu[]>([]);
  const [form, setForm] = useState<OpcionMenuPayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadOptions = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get<OpcionesMenuResponse>(
        "/opciones-menu?incluir_inactivos=true",
      );
      setOpciones(data.items);
    } catch {
      setError("No se pudieron cargar las opciones desde Flask.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadOptions();
  }, [loadOptions]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      if (editingId) {
        await api.put(`/opciones-menu/${editingId}`, form);
        setMessage("Opción actualizada correctamente.");
      } else {
        await api.post("/opciones-menu", form);
        setMessage("Opción creada correctamente.");
      }
      setForm(emptyForm);
      setEditingId(null);
      await loadOptions();
    } catch (requestError: any) {
      setError(
        requestError?.response?.data?.message ?? "No se pudo guardar la opción.",
      );
    }
  }

  function edit(opcion: OpcionMenu) {
    setEditingId(opcion.id_opcion_menu);
    setForm({
      codigo: opcion.codigo,
      nombre: opcion.nombre,
      ruta: opcion.ruta ?? "",
      descripcion: opcion.descripcion ?? "",
      icono: opcion.icono ?? "",
      id_padre: opcion.id_padre,
      orden: opcion.orden,
    });
    setMessage("");
    setError("");
  }

  async function toggleStatus(opcion: OpcionMenu) {
    setError("");
    setMessage("");
    try {
      await api.patch(`/opciones-menu/${opcion.id_opcion_menu}/estado`, {
        activo: !opcion.activo,
      });
      setMessage(opcion.activo ? "Opción desactivada." : "Opción activada.");
      await loadOptions();
    } catch {
      setError("No se pudo cambiar el estado de la opción.");
    }
  }

  return (
    <section className="workspace-grid users-grid">
      <form className="card form-card" onSubmit={submit}>
        <div className="section-heading">
          <span className="eyebrow">RF-03</span>
          <h2>{editingId ? "Editar opción" : "Nueva opción"}</h2>
        </div>

        <label>
          Código
          <input
            required
            pattern="[a-z][a-z0-9_]*"
            maxLength={80}
            value={form.codigo}
            onChange={(event) =>
              setForm({ ...form, codigo: event.target.value.toLowerCase() })
            }
            placeholder="ejemplo: reportes"
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
          Opción padre
          <select
            value={form.id_padre ?? ""}
            onChange={(event) =>
              setForm({
                ...form,
                id_padre: event.target.value ? Number(event.target.value) : null,
              })
            }
          >
            <option value="">Sin padre (opción principal)</option>
            {opciones
              .filter((item) => item.id_opcion_menu !== editingId)
              .map((item) => (
                <option key={item.id_opcion_menu} value={item.id_opcion_menu}>
                  {item.nombre}{item.activo ? "" : " (inactiva)"}
                </option>
              ))}
          </select>
        </label>

        <div className="form-two-columns">
          <label>
            Ruta
            <input
              maxLength={200}
              value={form.ruta}
              onChange={(event) => setForm({ ...form, ruta: event.target.value })}
              placeholder="/seguridad/perfiles"
            />
          </label>
          <label>
            Orden
            <input
              required
              type="number"
              min={1}
              max={32767}
              value={form.orden}
              onChange={(event) =>
                setForm({ ...form, orden: Number(event.target.value) })
              }
            />
          </label>
        </div>

        <label>
          Icono
          <input
            maxLength={80}
            value={form.icono}
            onChange={(event) => setForm({ ...form, icono: event.target.value })}
            placeholder="ejemplo: shield"
          />
        </label>

        <label>
          Descripción
          <textarea
            maxLength={300}
            rows={3}
            value={form.descripcion}
            onChange={(event) =>
              setForm({ ...form, descripcion: event.target.value })
            }
          />
        </label>

        <div className="actions">
          <button type="submit">{editingId ? "Guardar cambios" : "Crear opción"}</button>
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
            <span className="eyebrow">Jerarquía</span>
            <h2>Opciones registradas</h2>
          </div>
          <button className="secondary" onClick={() => void loadOptions()}>
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
                  <th>Opción</th>
                  <th>Padre</th>
                  <th>Ruta / tipo</th>
                  <th>Orden</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {opciones.map((opcion) => (
                  <tr key={opcion.id_opcion_menu}>
                    <td>
                      <strong>{opcion.nombre}</strong>
                      <small><code>{opcion.codigo}</code></small>
                    </td>
                    <td>{opcion.nombre_padre ?? "Principal"}</td>
                    <td>
                      {opcion.ruta ? <code>{opcion.ruta}</code> : "Agrupador"}
                    </td>
                    <td>{opcion.orden}</td>
                    <td>
                      <span className={opcion.activo ? "status active" : "status inactive"}>
                        {opcion.activo ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td className="row-actions">
                      <button className="link-button" onClick={() => edit(opcion)}>
                        Editar
                      </button>
                      <button
                        className="link-button danger"
                        onClick={() => void toggleStatus(opcion)}
                      >
                        {opcion.activo ? "Desactivar" : "Activar"}
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
