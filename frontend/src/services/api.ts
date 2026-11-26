export type Contexto = {
  empresa:string; snapshot:string; corte:string; inicio:string; semilla:number;
  version:string; checksum:string; evidencia:string; moneda:string;
  mercados:{id:string; nombre:string}[];
  manifiesto:{conteos:Record<string,number>; coberturas:Record<string,string|number>; [key:string]:unknown};
  modulos:Record<string,string>;
};
export type Metrica = {id:string; nombre:string; valor:number; anterior:number; delta_pct:number|null; unidad:"EUR"|"pedidos"; definicion:string};
export type Periodo = {inicio:string; fin:string; dias:number; mercado:string|null; snapshot:string; anterior_inicio:string; anterior_fin:string};
export type Serie = {fecha:string; ventas:number; pedidos:number; margen:number; inversion:number};
export type Canal = {id:string; nombre:string; color:string; tipo:string; inversion:number; impresiones:number|null; clics:number|null; conversiones:number; ingresos_atribuidos:number; roas_atribuido:number|null; incremental:null};
export type KPIs = {periodo:Periodo; metricas:Metrica[]; serie:Serie[]; canales:Canal[]; evidencia:string; costes:string};
export type Grupo = {id:string; nombre:string; intencion:string; elegible:boolean; clics_seo:number; clics_sem:number; inversion:number; posicion:number|null; competencia:number; conversiones_atribuidas:number; impresiones:number; cpc:number|null};
export type Creativo = {id:string; nombre:string; asset:string; vista_previa?:import("./creatividad").CreativeVariant; atributos:Record<string,string>; canal:string; formato:string; impresiones:number; clics:number; conversiones:number; inversion:number; ctr:number|null; cvr:number|null; licencia:string; categoria:string; frecuencia:number};
export type Tabla<T> = {periodo:Periodo; filas:T[]; total:number; pagina:number; paginas:number; evidencia:string; cobertura:string; advertencias:string[]};
export type Fiabilidad = {snapshot:string; estado:"valido"|"limitado"|"bloqueado"; fuentes:{id:string; nombre:string; filas:number; dias:number; cobertura:string; estado:string}[]; reglas:{id:string; nombre:string; valor:number|null; unidad:string; umbral:string; estado:string}[]; incidencias:{causa:string; accion:string}[]; diagnostico_modelos:string; checksum:string};

export type SearchInputs={recorte_pct:number; cuota_plataforma:number; coste_experimento:number; plataforma_comun:boolean; hipotesis?:string|null};
export type SearchBand={p05:number;p50:number;p95:number;probabilidad_perdida:number;delta_pedidos_p05:number;delta_pedidos_p95:number;replicas:number;metodo:string};
export type Radar={periodo:Periodo;criterio:string;filas:{id:string;titulo:string;modelo:string;prioridad:number;impacto:number;banda:SearchBand;coste:number;recorte_pct:number;estado:string;recomendacion:string;motivos:string[];url:string}[]};
export type SearchEvidence={periodo:Periodo;serie:{fecha:string;seo:number;sem:number}[];defecto:SearchInputs;soporte_pct:number[];modelo:{id:string;version:string;hipotesis:string;semilla:number;checksum_datos:string;estado:string;motivos:string[];metodo:string;unidad:string;origen?:string;experimento_actual?:string;modelo_anterior?:string;recuperacion:null;pares:number;experimentos:number;replicas:number;advertencias:string[];estratos:{id:string;pares:number;pooling:string}[];placebo:{efecto:number;ic95:number[]};intervalos:{recorte:number;tasa:number;p05:number;p95:number}[];historicos:{id:string;inicio_pre:string;inicio_post:string;fin:string;recorte:number;origen:string}[]}};
type SearchBalance={pedidos:number;margen:number;inversion:number;plataforma:number;experimento:number;contribucion:number};
export type SearchSimulation={id:string;reutilizada:boolean;resultado:{periodo:Periodo;modelo:string;version:string;hipotesis:string;semilla:number;entradas:SearchInputs;estado:string;motivos:string[];recomendacion:string;ahorro:number;delta_pedidos:number;cambio_margen:number;costes_incrementales:number;delta:number;perdida_maxima_pedidos:number|null;recuperacion:null;base:SearchBalance;alternativa:SearchBalance;banda:SearchBand;desglose:{nombre:string;importe:number;offset:number;altura:number;favorable:boolean}[];advertencias:string[]}};

type ErrorModelo = {mae:number; wape:number|null; sesgo:number|null};
export type FichaModelo = {
  id:string; version:string; snapshot:string; corte:string; semilla:number; checksum_datos:string;
  estado:"limitado"|"bloqueado"; motivos:string[]; optimizable:boolean; ambito:string; objetivo:string;
  semanas:number; train_inicio:string; train_fin:string; holdout_inicio:string; holdout_fin:string;
  segundos_ajuste:number; incertidumbre:string; advertencias:string[];
  configuracion:{replicas:number; bloque:number; holdout:number};
  diagnostico:{train:ErrorModelo; holdout:ErrorModelo; naive:ErrorModelo; autocorrelacion_lag1:number|null;
    correlacion_maxima:number; condicion:number|null; variacion_minima:number; sensibilidad:number;
    cobertura_banda_holdout:number; umbrales:{max_correlacion:number; max_condicion:number; min_variacion:number; max_sensibilidad:number}};
  folds:{train_fin:string; validacion_inicio:string; validacion_fin:string}[];
};
export type SemanaModelo = {inicio:string; fin:string; observado:number; predicho:number; baseline:number; efectos:number; residual:number; p05:number; p95:number; ancho_banda:number; naive:number|null; particion:"train"|"holdout"};
export type CurvaModelo = {id:string; nombre:string; color:string; minimo:number; maximo:number; referencia:number; stock_previo_normalizado:number; horizonte_dias:number; puntos:{inversion:number; pedidos:number; p05:number; p95:number; ancho_banda:number; marginal:number; extrapolado:boolean}[]};
export type MedicionModelo = {
  modelo:FichaModelo; periodo:Periodo; aplicable:boolean; motivo:string|null; cobertura:string;
  serie:SemanaModelo[]; curvas:CurvaModelo[];
  resumen:{id:string; nombre:string; color:string; pedidos_modelados:number; pedidos_p05:number; pedidos_p95:number; margen_asignado:number; inversion:number; saldo_modelado:number; saldo_p05:number; saldo_p95:number}[];
};

export async function api<T>(path:string, signal?:AbortSignal):Promise<T> {
  const response = await fetch(`/api/v1/${path}`, {cache:"no-store", signal});
  if (!response.ok) {
    const error = await response.json().catch(()=>({detail:"No se han podido cargar los datos."}));
    throw new Error(typeof error.detail==="string" ? error.detail : "Parámetros no válidos.");
  }
  return response.json();
}
export async function post<T>(path:string, body:unknown, method:"POST"|"PATCH"="POST"):Promise<T> {
  const response=await fetch(`/api/v1/${path}`,{method,headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  const data=await response.json();
  if(!response.ok)throw new Error(typeof data.detail==="string"?data.detail:"Revisa los parámetros de la evaluación.");
  return data;
}
export const numero = (v:number|null|undefined, decimals=0) => v==null ? "n/d" : new Intl.NumberFormat("es-ES", {maximumFractionDigits:decimals, minimumFractionDigits:decimals}).format(v);
export const euros = (v:number|null|undefined, compact=false) => v==null ? "n/d" : new Intl.NumberFormat("es-ES", {style:"currency",currency:"EUR",maximumFractionDigits:0, ...(compact?{notation:"compact" as const}: {})}).format(v);
export const porcentaje = (v:number|null|undefined, decimals=1) => v==null ? "n/d" : new Intl.NumberFormat("es-ES", {style:"percent",minimumFractionDigits:decimals,maximumFractionDigits:decimals}).format(v);
export const fecha = (v:string) => new Date(`${v}T12:00:00`).toLocaleDateString("es-ES", {day:"2-digit", month:"2-digit", year:"numeric"});
