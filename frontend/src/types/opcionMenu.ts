export type OpcionMenu = {
  id_opcion_menu: number;
  codigo: string;
  nombre: string;
  ruta: string | null;
  descripcion: string | null;
  icono: string | null;
  id_padre: number | null;
  nombre_padre: string | null;
  orden: number;
  activo: boolean;
};

export type OpcionMenuPayload = {
  codigo: string;
  nombre: string;
  ruta: string;
  descripcion: string;
  icono: string;
  id_padre: number | null;
  orden: number;
};

export type OpcionesMenuResponse = {
  items: OpcionMenu[];
};
