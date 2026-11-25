"use client";

import {useState} from "react";
import {useSearchParams} from "next/navigation";
import Link from "next/link";
import {ArrowRight,BookOpen} from "lucide-react";
import {Badge,Drawer,Loading} from "@/components/ui";
import {ErrorState} from "@/components/error-state";
import {fecha,numero,porcentaje} from "@/services/api";
import {useRemote} from "@/services/use-remote";
import type {CreativeCatalog,CreativeEvaluation,CreativeHistory} from "@/services/creatividad";
import {Workbench} from "@/features/pretest-creativo";
import {BibliotecaCreativa} from "@/features/views";

function Method({data,onClose}:{data:CreativeCatalog;onClose:()=>void}){
  const m=data.modelo,p=m.particiones;
  return <Drawer title="Modelo creativo: método y validación" onClose={onClose}><Badge tone={m.estado==="bloqueado"?"warning":"neutral"}>{m.estado==="bloqueado"?"Predictor bloqueado":"Estimación limitada"}</Badge><h2>Qué se aprende del histórico</h2><p>{m.metodo}</p><p>El modelo usa conteos de clics y su denominador de impresiones. La categoría, el tono y el CTA forman un paquete observado; su asociación no identifica el efecto de cambiar un atributo.</p>
    <h2>Validación con grupos y fechas separados</h2><dl className="definition-list"><dt>Entrenamiento</dt><dd>{fecha(p.train_inicio)} — {fecha(p.train_fin)} · {numero(p.filas_train)} filas · {p.grupos_train.length} composiciones</dd><dt>Holdout reservado</dt><dd>{fecha(p.holdout_inicio)} — {fecha(p.holdout_fin)} · {numero(p.filas_holdout)} filas · {p.grupos_holdout.length} composiciones</dd><dt>Filas fuera de ambas particiones</dt><dd>{numero(p.filas_excluidas)}: cruce de ventanas y grupos excluido para evitar contaminación</dd></dl>
    <div className="table-wrapper" tabIndex={0} role="region" aria-label="Validación del modelo creativo"><table><caption className="visually-hidden">Modelo y referencia por canal sobre el mismo holdout</caption><thead><tr><th scope="col">Métrica</th><th scope="col">Modelo</th><th scope="col">Referencia por canal</th></tr></thead><tbody><tr><th scope="row">Pérdida logarítmica por impresión</th><td>{numero(m.holdout.log_loss,5)}</td><td>{numero(m.naive.log_loss,5)}</td></tr><tr><th scope="row">Error absoluto ponderado de CTR</th><td>{porcentaje(m.holdout.mae_tasa,2)}</td><td>{porcentaje(m.naive.mae_tasa,2)}</td></tr><tr><th scope="row">CTR observado</th><td colSpan={2}>{porcentaje(m.holdout.observado,2)}</td></tr><tr><th scope="row">CTR predicho agregado</th><td>{porcentaje(m.holdout.predicho,2)}</td><td>{porcentaje(m.naive.predicho,2)}</td></tr></tbody></table></div>
    <p>Las campañas y composiciones no cruzan la frontera. Los parámetros se mantienen ajustados exclusivamente con train; navegar o cambiar filtros no reentrena.</p><h2>Incertidumbre y límites</h2><p>{m.replicas} réplicas por grupos completos. La banda p05–p95 describe parámetros condicionados al histórico. La fracción de tasas observadas dentro de esa banda es {porcentaje(m.holdout.cobertura_tasas_observadas)}; no equivale a cobertura de un intervalo predictivo de nuevos clics.</p><ul className="model-notes">{[...m.motivos,...m.advertencias].map(a=><li key={a}>{a}</li>)}</ul><h2>Trazabilidad</h2><dl className="definition-list"><dt>Modelo</dt><dd className="checksum">{m.id} · {m.version}</dd><dt>Semilla / corte</dt><dd>{m.semilla} · {fecha(m.corte)}</dd><dt>Checksum de observaciones</dt><dd className="checksum">{m.checksum_datos}</dd></dl>
  </Drawer>;
}


function Saved({id,data,query,selectionId}:{id:string;data:CreativeCatalog;query:string;selectionId:string|null}){
  const r=useRemote<CreativeEvaluation>(`creativos/evaluaciones/${id}`);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <Loading/>;
  return <Workbench key={r.data.id} data={data} query={query} initial={r.data} selectionId={selectionId}/>;
}

function History({query}:{query:string}){
  const r=useRemote<CreativeHistory>("creativos/historial");
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data?.filas.length)return null;
  return <section className="panel creative-history"><div className="panel-header"><div><h2>Pretests guardados</h2><p>Últimas evaluaciones; conservan inputs y versión del modelo</p></div></div><div className="table-wrapper" tabIndex={0} role="region" aria-label="Historial de pretests"><table><caption className="visually-hidden">Contexto y selecciones de evaluaciones guardadas</caption><thead><tr><th scope="col">Objetivo</th><th scope="col">Contexto</th><th scope="col">Selecciones</th><th scope="col">Consultar</th></tr></thead><tbody>{r.data.filas.map(p=><tr key={p.id}><th scope="row">{p.entradas.objetivo}</th><td>{p.entradas.canal} · {p.entradas.categoria}</td><td>{p.selecciones.length? p.selecciones.map(s=>s.variante_id).join(", "):"Sin selección"}</td><td><Link className="text-link" href={`/creatividad?${query}&vista=pretest&evaluacion=${p.id}${p.selecciones[0]?`&seleccion=${p.selecciones[0].id}`:""}`}>Abrir<ArrowRight size={13}/></Link></td></tr>)}</tbody></table></div></section>;
}

export function Creatividad({query}:{query:string}){
  const r=useRemote<CreativeCatalog>("creativos/pretest"),search=useSearchParams();
  const [method,setMethod]=useState(false);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <Loading/>;
  const d=r.data,id=search.get("evaluacion"),selectionId=search.get("seleccion"),pretest=search.get("vista")==="pretest"||!!id;
  return <div className="creative-workspace"><div className="creative-viewbar"><nav aria-label="Vistas de creatividad"><Link className={`button ${pretest?"secondary":"primary"}`} aria-current={!pretest?"page":undefined} href={`/creatividad?${query}&vista=biblioteca`}>Biblioteca observada</Link><Link className={`button ${pretest?"primary":"secondary"}`} aria-current={pretest?"page":undefined} href={`/creatividad?${query}&vista=pretest`}>Preparar pretest</Link></nav><button type="button" className="button secondary" onClick={()=>setMethod(true)}><BookOpen size={15}/>Método y validación</button></div>
    {pretest?<>{id?<Saved id={id} data={d} query={query} selectionId={selectionId}/>:<Workbench data={d} query={query} selectionId={null}/>}<History key={`${id}:${selectionId}`} query={query}/></>:<BibliotecaCreativa query={query} catalogo={d}/>}
    {method&&<Method data={d} onClose={()=>setMethod(false)}/>}
  </div>;
}
