export type UsuarioPerfil = {
  id_perfil: number;
  codigo: string;
  nombre: string;
};

export type Usuario = {
  id_usuario: number;
  dni: string;
  nombres: string;
  apellido_paterno: string;
  apellido_materno: string | null;
  celular: string | null;
  correo: string;
  activo: boolean;
  perfiles: UsuarioPerfil[];
  creado_en: string | null;
};

export type UsuarioPayload = {
  dni: string;
  nombres: string;
  apellido_paterno: string;
  apellido_materno: string;
  celular: string;
  correo: string;
  password: string;
  perfiles: number[];
};

export type UsuariosResponse = {
  items: Usuario[];
};
