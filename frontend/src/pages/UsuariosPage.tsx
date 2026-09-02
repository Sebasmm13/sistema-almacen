import { FormEvent, useCallback, useEffect, useState } from "react";

import { api } from "../services/api";
import type { Perfil, PerfilesResponse } from "../types/perfil";
import type { Usuario, UsuarioPayload, UsuariosResponse } from "../types/usuario";

const emptyForm: UsuarioPayload = {
  dni: "",
  nombres: "",
  apellido_paterno: "",
  apellido_materno: "",
  celular: "",
  correo: "",
  password: "",
  perfiles: [],
};

export function UsuariosPage() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [perfiles, setPerfiles] = useState<Perfil[]>([]);
  const [form, setForm] = useState<UsuarioPayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [usuariosResponse, perfilesResponse] = await Promise.all([
        api.get<UsuariosResponse>("/usuarios?incluir_inactivos=true"),
        api.get<PerfilesResponse>("/perfiles?per_page=100"),
      ]);
      setUsuarios(usuariosResponse.data.items);
      setPerfiles(perfilesResponse.data.items);
    } catch {
      setError("No se pudo cargar usuarios y perfiles desde Flask.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  function toggleProfile(idPerfil: number) {
    setForm((current) => ({
      ...current,
      perfiles: current.perfiles.includes(idPerfil)
        ? current.perfiles.filter((item) => item !== idPerfil)
        : [...current.perfiles, idPerfil],
    }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    if (form.perfiles.length === 0) {
      setError("Selecciona al menos un perfil.");
      return;
    }
    try {
      if (editingId) {
        await api.put(`/usuarios/${editingId}`, form);
        setMessage("Usuario actualizado correctamente.");
      } else {
        await api.post("/usuarios", form);
        setMessage("Usuario creado correctamente.");
      }
      setForm(emptyForm);
      setEditingId(null);
      await loadData();
    } catch (requestError: any) {
      setError(
        requestError?.response?.data?.message ?? "No se pudo guardar el usuario.",
      );
    }
  }

  function edit(usuario: Usuario) {
    setEditingId(usuario.id_usuario);
    setForm({
      dni: usuario.dni,
      nombres: usuario.nombres,
      apellido_paterno: usuario.apellido_paterno,
      apellido_materno: usuario.apellido_materno ?? "",
      celular: usuario.celular ?? "",
      correo: usuario.correo,
      password: "",
      perfiles: usuario.perfiles.map((item) => item.id_perfil),
    });
    setMessage("");
    setError("");
  }

  async function toggleStatus(usuario: Usuario) {
    setError("");
    setMessage("");
    try {
      await api.patch(`/usuarios/${usuario.id_usuario}/estado`, {
        activo: !usuario.activo,
      });
      setMessage(usuario.activo ? "Usuario desactivado." : "Usuario activado.");
      await loadData();
    } catch {
      setError("No se pudo cambiar el estado del usuario.");
    }
  }

  return (
    <section className="workspace-grid users-grid">
      <form className="card form-card" onSubmit={submit}>
        <div className="section-heading">
          <span className="eyebrow">RF-02</span>
          <h2>{editingId ? "Editar usuario" : "Nuevo usuario"}</h2>
        </div>

        <div className="form-two-columns">
          <label>
            DNI
            <input
              required
              inputMode="numeric"
              pattern="[0-9]{8}"
              maxLength={8}
              value={form.dni}
              onChange={(event) => setForm({ ...form, dni: event.target.value })}
            />
          </label>
          <label>
            Celular
            <input
              inputMode="numeric"
              pattern="9[0-9]{8}"
              maxLength={9}
              value={form.celular}
              onChange={(event) =>
                setForm({ ...form, celular: event.target.value })
              }
            />
          </label>
        </div>

        <label>
          Nombres
          <input
            required
            maxLength={100}
            value={form.nombres}
            onChange={(event) => setForm({ ...form, nombres: event.target.value })}
          />
        </label>

        <div className="form-two-columns">
          <label>
            Apellido paterno
            <input
              required
              maxLength={100}
              value={form.apellido_paterno}
              onChange={(event) =>
                setForm({ ...form, apellido_paterno: event.target.value })
              }
            />
          </label>
          <label>
            Apellido materno
            <input
              maxLength={100}
              value={form.apellido_materno}
              onChange={(event) =>
                setForm({ ...form, apellido_materno: event.target.value })
              }
            />
          </label>
        </div>

        <label>
          Correo
          <input
            required
            type="email"
            maxLength={150}
            value={form.correo}
            onChange={(event) => setForm({ ...form, correo: event.target.value })}
          />
        </label>

        <label>
          {editingId ? "Nueva contraseña (opcional)" : "Contraseña"}
          <input
            required={!editingId}
            type="password"
            minLength={8}
            autoComplete="new-password"
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
          />
        </label>

        <fieldset className="profile-fieldset">
          <legend>Perfiles</legend>
          <div className="checkbox-grid">
            {perfiles.map((perfil) => (
              <label className="checkbox-option" key={perfil.id_perfil}>
                <input
                  type="checkbox"
                  checked={form.perfiles.includes(perfil.id_perfil)}
                  onChange={() => toggleProfile(perfil.id_perfil)}
                />
                {perfil.nombre}
              </label>
            ))}
          </div>
        </fieldset>

        <div className="actions">
          <button type="submit">{editingId ? "Guardar cambios" : "Crear usuario"}</button>
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
            <h2>Usuarios registrados</h2>
          </div>
          <button className="secondary" onClick={() => void loadData()}>
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
                  <th>Usuario</th>
                  <th>Contacto</th>
                  <th>Perfiles</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((usuario) => (
                  <tr key={usuario.id_usuario}>
                    <td>
                      <strong>
                        {usuario.nombres} {usuario.apellido_paterno}
                      </strong>
                      <small>DNI: {usuario.dni}</small>
                    </td>
                    <td>
                      {usuario.correo}
                      <small>{usuario.celular || "Sin celular"}</small>
                    </td>
                    <td>
                      <div className="profile-tags">
                        {usuario.perfiles.map((perfil) => (
                          <span className="profile-tag" key={perfil.id_perfil}>
                            {perfil.nombre}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <span className={usuario.activo ? "status active" : "status inactive"}>
                        {usuario.activo ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td className="row-actions">
                      <button className="link-button" onClick={() => edit(usuario)}>
                        Editar
                      </button>
                      <button
                        className="link-button danger"
                        onClick={() => void toggleStatus(usuario)}
                      >
                        {usuario.activo ? "Desactivar" : "Activar"}
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
