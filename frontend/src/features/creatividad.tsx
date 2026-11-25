"use client";

import {useEffect,useRef,useState,type FormEvent} from "react";
import {useRouter,useSearchParams} from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import {ArrowRight,BookOpen,Check,FlaskConical} from "lucide-react";
import {Badge,Drawer,Loading,Notice} from "@/components/ui";
import {ErrorState} from "@/components/error-state";
import {fecha,numero,porcentaje,post} from "@/services/api";
import {useRemote} from "@/services/use-remote";
import type {CreativeCatalog,CreativeEvaluation,CreativeHistory,CreativeSelection} from "@/services/creatividad";
import {BibliotecaCreativa} from "@/features/views";

function Method({data,onClose}:{data:CreativeCatalog;onClose:()=>void}){
  const m=data.modelo,p=m.particiones;
  return <Drawer title="Modelo creativo: método y validación" onClose={onClose}><Badge tone={m.estado==="bloqueado"?"warning":"neutral"}>{m.estado==="bloqueado"?"Predictor bloqueado":"Estimación limitada"}</Badge><h2>Qué se aprende del histórico</h2><p>{m.metodo}</p><p>El modelo usa conteos de clics y su denominador de impresiones. La categoría, el tono y el CTA forman un paquete observado; su asociación no identifica el efecto de cambiar un atributo.</p>
    <h2>Validación con grupos y fechas separados</h2><dl className="definition-list"><dt>Entrenamiento</dt><dd>{fecha(p.train_inicio)} — {fecha(p.train_fin)} · {numero(p.filas_train)} filas · {p.grupos_train.length} composiciones</dd><dt>Holdout reservado</dt><dd>{fecha(p.holdout_inicio)} — {fecha(p.holdout_fin)} · {numero(p.filas_holdout)} filas · {p.grupos_holdout.length} composiciones</dd><dt>Filas fuera de ambas particiones</dt><dd>{numero(p.filas_excluidas)}: cruce de ventanas y grupos excluido para evitar contaminación</dd></dl>
    <div className="table-wrapper" tabIndex={0} role="region" aria-label="Validación del modelo creativo"><table><caption className="visually-hidden">Modelo y referencia por canal sobre el mismo holdout</caption><thead><tr><th scope="col">Métrica</th><th scope="col">Modelo</th><th scope="col">Referencia por canal</th></tr></thead><tbody><tr><th scope="row">Pérdida logarítmica por impresión</th><td>{numero(m.holdout.log_loss,5)}</td><td>{numero(m.naive.log_loss,5)}</td></tr><tr><th scope="row">Error absoluto ponderado de CTR</th><td>{porcentaje(m.holdout.mae_tasa,2)}</td><td>{porcentaje(m.naive.mae_tasa,2)}</td></tr><tr><th scope="row">CTR observado</th><td colSpan={2}>{porcentaje(m.holdout.observado,2)}</td></tr><tr><th scope="row">CTR predicho agregado</th><td>{porcentaje(m.holdout.predicho,2)}</td><td>{porcentaje(m.naive.predicho,2)}</td></tr></tbody></table></div>
    <p>Las campañas y composiciones no cruzan la frontera. Los parámetros se mantienen ajustados exclusivamente con train; navegar o cambiar filtros no reentrena.</p><h2>Incertidumbre y límites</h2><p>{m.replicas} réplicas por grupos completos. La banda p05–p95 describe parámetros condicionados al histórico. La fracción de tasas observadas dentro de esa banda es {porcentaje(m.holdout.cobertura_tasas_observadas)}; no equivale a cobertura de un intervalo predictivo de nuevos clics.</p><ul className="model-notes">{[...m.motivos,...m.advertencias].map(a=><li key={a}>{a}</li>)}</ul><h2>Trazabilidad</h2><dl className="definition-list"><dt>Modelo</dt><dd className="checksum">{m.id} · {m.version}</dd><dt>Semilla / corte</dt><dd>{m.semilla} · {fecha(m.corte)}</dd><dt>Checksum de observaciones</dt><dd className="checksum">{m.checksum_datos}</dd></dl>
  </Drawer>;
}

function Selection({id,evaluationId}:{id:string;evaluationId:string}){
  const r=useRemote<CreativeSelection>(`creativos/selecciones/${id}`);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <p role="status">Consultando selección guardada…</p>;
  if(r.data.pretest_id!==evaluationId)return <Notice>La selección pertenece a otra evaluación. Abre el pretest correspondiente desde el historial.</Notice>;
  return <section className="creative-selection" data-testid="seleccion-creativa"><Check size={18}/><div><strong>Hipótesis creativa guardada</strong><p>{r.data.variante_id} · {r.data.motivo}</p><p className="checksum">{r.data.id}</p><p>No activa publicidad. Multiplicador de demanda: {numero(r.data.multiplicador_demanda,1)}.</p></div></section>;
}

function Workbench({data,query,initial,selectionId}:{data:CreativeCatalog;query:string;initial?:CreativeEvaluation;selectionId:string|null}){
  const router=useRouter();
  const defaults=initial?.entradas||data.defecto;
  const [channel,setChannel]=useState(defaults.canal),[category,setCategory]=useState(defaults.categoria),[audience,setAudience]=useState(defaults.audiencia);
  const [busy,setBusy]=useState(false),[selecting,setSelecting]=useState(false),[dirty,setDirty]=useState(false),[error,setError]=useState("");
  const errorRef=useRef<HTMLParagraphElement>(null),headingRef=useRef<HTMLHeadingElement>(null);
  const r=initial;
  useEffect(()=>{if(r)headingRef.current?.focus({preventScroll:true});},[r]);
  const available=data.canales.find(c=>c.id===channel)?.audiencias||[];
  async function submit(e:FormEvent<HTMLFormElement>){
    e.preventDefault();const f=new FormData(e.currentTarget);setBusy(true);setError("");
    try{const result=await post<CreativeEvaluation>("creativos/evaluar",{canal:channel,categoria:category,audiencia:audience,frecuencia:Number(f.get("frecuencia")),impresiones:Number(f.get("impresiones")),objetivo:String(f.get("objetivo"))});
      router.replace(`/creatividad?${query}&vista=pretest&evaluacion=${result.id}`,{scroll:false});setDirty(false);
    }catch(e){setError(e instanceof Error?e.message:"No se ha podido guardar el pretest.");requestAnimationFrame(()=>errorRef.current?.focus());}
    finally{setBusy(false);}
  }
  async function select(variant:string){
    if(!r)return;setSelecting(true);setError("");
    try{const s=await post<CreativeSelection>("creativos/selecciones",{pretest_id:r.id,variante_id:variant});router.replace(`/creatividad?${query}&vista=pretest&evaluacion=${r.id}&seleccion=${s.id}`,{scroll:false});}
    catch(e){setError(e instanceof Error?e.message:"No se ha podido guardar la selección.");requestAnimationFrame(()=>errorRef.current?.focus());}
    finally{setSelecting(false);}
  }
  const variants=r?.variantes||data.variantes.filter(v=>v.categoria===category);
  return <section className="creative-workbench" id="pretest"><section className="panel"><div className="panel-header wrap"><div><h2 id="titulo-pretest">Tres composiciones. Una hipótesis contrastable.</h2><p>{data.alcance}</p></div><Badge>Pretest estadístico</Badge></div><form className="creative-form" method="post" action="/api/v1/creativos/evaluar" aria-labelledby="titulo-pretest" onSubmit={submit} onChange={()=>{setDirty(true);setError("");}}>
      <div className="creative-form-grid"><div><label htmlFor="pretest-canal">Canal del pretest</label><select id="pretest-canal" name="canal" value={channel} onChange={e=>{const value=e.target.value;setChannel(value);setAudience(data.canales.find(c=>c.id===value)!.audiencias[0]);}}>{data.canales.map(c=><option key={c.id} value={c.id}>{c.nombre}</option>)}</select></div><div><label htmlFor="pretest-perfil">Perfil de partida</label><select id="pretest-perfil" name="categoria" value={category} onChange={e=>setCategory(e.target.value)}>{data.perfiles.map(p=><option key={p.categoria} value={p.categoria}>{p.categoria.charAt(0).toUpperCase()+p.categoria.slice(1)} · {p.tono}</option>)}</select></div><div><label htmlFor="pretest-audiencia">Audiencia del pretest</label><select id="pretest-audiencia" name="audiencia" value={audience} onChange={e=>setAudience(e.target.value)}>{available.map(a=><option key={a}>{a}</option>)}</select></div><div><label htmlFor="pretest-frecuencia">Frecuencia prevista</label><input id="pretest-frecuencia" name="frecuencia" type="number" min={1} max={10} step="0.1" required defaultValue={defaults.frecuencia}/></div><div><label htmlFor="pretest-impresiones">Impresiones de referencia</label><input id="pretest-impresiones" name="impresiones" type="number" min={1000} max={1000000} step={1} required defaultValue={defaults.impresiones}/></div><div className="creative-objective"><label htmlFor="pretest-objetivo">Objetivo del brief (obligatorio)</label><textarea id="pretest-objetivo" name="objetivo" rows={2} minLength={10} maxLength={250} required defaultValue={defaults.objetivo}/></div></div>
      <div className="creative-form-bottom"><p>Activos locales precreados. El formulario guarda el brief y calcula la referencia del contexto. CTA y tono se mantienen dentro de su paquete observado.</p><button type="submit" className="button primary" disabled={busy}>{busy?"Calculando y guardando…":"Evaluar tres composiciones"}<ArrowRight size={15}/></button></div>
    </form></section><p className="form-error" ref={errorRef} tabIndex={-1} role={error?"alert":undefined}>{error}</p>
    {r&&<><p className="creative-run-status" role="status">Evaluación guardada. Modelo {r.version}; consulta de una estimación persistida.</p>{dirty&&<Notice>Parámetros modificados. Los resultados e imágenes corresponden al último contexto evaluado.</Notice>}<div className="creative-result-heading"><h2 ref={headingRef} tabIndex={-1}>Referencia del contexto evaluado</h2><Badge tone={r.estado==="bloqueado"?"warning":"neutral"}>{r.estado==="bloqueado"?"Predictor bloqueado":"Hipótesis"}</Badge></div><div className="model-metrics creative-estimates"><article><small>CTR de referencia compartido</small><strong data-testid="ctr-pretest">{porcentaje(r.referencia.ctr,2)}</strong><p>p05–p95: {porcentaje(r.referencia.p05,2)} — {porcentaje(r.referencia.p95,2)}</p></article><article><small>Clics de referencia</small><strong data-testid="clics-pretest">{numero(r.referencia.clics_esperados)}</strong><p>Sobre {numero(r.entradas.impresiones)} impresiones</p></article><article><small>CVR observado de entrenamiento</small><strong>{porcentaje(r.referencia.cvr_observado,2)}</strong><p>{numero(r.referencia.cvr_conversiones)} conversiones / {numero(r.referencia.cvr_clics)} clics</p></article><article><small>Diferencia visual identificada</small><strong>Sin evidencia</strong><p>El modelo no distingue estas composiciones</p></article></div><p className="creative-run-status">{r.referencia.fuente}. Bandas de parámetros por grupos; no son intervalos de nuevos clics.</p><Notice><strong>Sin ganador predictivo</strong>{r.motivos.map(m=><p key={m}>{m}</p>)}</Notice></>}
    {!r&&<p className="creative-run-status">Estas son las composiciones disponibles para el perfil. Evalúa el contexto para calcular CTR, bandas y un brief guardado.</p>}
    <div className="creative-comparison" aria-label="Tres composiciones originales">{variants.map((v,i)=><article className="creative-variant" key={v.id} data-testid="variante-pretest"><div className="creative-variant-number">Propuesta {i+1} · {v.categoria}</div><Image src={v.asset} alt={`AUREL ${v.categoria}: ${v.nombre}. ${v.composicion}.`} width={600} height={600} loading="eager" unoptimized/><div className="creative-variant-body"><h3>{v.nombre}</h3><p>{v.composicion}</p><dl><dt>Tono</dt><dd>{v.tono}</dd><dt>CTA</dt><dd>{v.cta}</dd></dl><p className="small">Composición precreada · efecto diferencial pendiente de prueba</p>{r&&<button type="button" className="button secondary" disabled={selecting} onClick={()=>select(v.id)}>Guardar propuesta {i+1}<ArrowRight size={14}/></button>}</div></article>)}</div>
    {selectionId&&r&&<Selection id={selectionId} evaluationId={r.id}/>}
    {r&&<section className="panel creative-brief"><div className="panel-header"><div><h2>Brief preparado por reglas</h2><p>{r.brief.metodo}</p></div><FlaskConical size={18}/></div><div className="creative-brief-body"><h3>{r.brief.objetivo}</h3><p>{r.brief.texto}</p><ul>{r.brief.reglas.map(rule=><li key={rule}>{rule}</li>)}</ul><details className="search-assumptions"><summary>Supuestos y trazabilidad</summary><ul className="model-notes">{r.advertencias.map(a=><li key={a}>{a}</li>)}</ul><p className="checksum">{r.id} · {r.modelo} · semilla {r.semilla}</p><a className="text-link" href={`/api/v1/creativos/evaluaciones/${r.id}`} target="_blank" rel="noreferrer">Consultar evaluación guardada<ArrowRight size={13}/></a></details></div></section>}
  </section>;
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
