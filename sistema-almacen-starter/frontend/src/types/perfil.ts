export type Perfil = {
  id_perfil: number;
  codigo: string;
  nombre: string;
  descripcion: string | null;
  activo: boolean;
  creado_en: string | null;
  modificado_en: string | null;
};

export type PerfilPayload = Pick<Perfil, "codigo" | "nombre" | "descripcion">;

export type PerfilesResponse = {
  items: Perfil[];
  page: number;
  per_page: number;
  total: number;
  pages: number;
};

