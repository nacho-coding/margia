"use client";

import {useEffect,useRef,useState,type FormEvent} from "react";
import {useRouter} from "next/navigation";
import Link from "next/link";
import {ArrowRight,Check,FlaskConical,ImagePlus,LoaderCircle} from "lucide-react";
import {Badge,Notice} from "@/components/ui";
import {CreativeArt} from "@/components/creative-art";
import {ErrorState} from "@/components/error-state";
import {numero,porcentaje,post} from "@/services/api";
import {useRemote} from "@/services/use-remote";
import type {CreativeCatalog,CreativeEvaluation,CreativeSelection,CreativeVariant} from "@/services/creatividad";
import {AprendizajeCreativo} from "@/features/ab";

async function prepararImagenes(variantes:CreativeVariant[]){
  await Promise.all(variantes.map(async v=>{
    const imagen=new window.Image();imagen.src=v.asset;
    try{await imagen.decode();}catch{throw new Error("No se ha podido cargar una imagen del catálogo local. Reintenta la preparación.");}
  }));
}

function Selection({id,evaluationId,query}:{id:string;evaluationId:string;query:string}){
  const r=useRemote<CreativeSelection>(`creativos/selecciones/${id}`);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <p role="status">Consultando selección guardada…</p>;
  if(r.data.pretest_id!==evaluationId)return <Notice>La selección pertenece a otra evaluación. Abre el pretest correspondiente desde el historial.</Notice>;
  return <section className="creative-selection" data-testid="seleccion-creativa"><Check size={18}/><div><strong>Hipótesis creativa guardada</strong><p>{r.data.variante_id} · {r.data.motivo}</p><p className="checksum">{r.data.id}</p><p>No activa publicidad. Multiplicador de demanda: {numero(r.data.multiplicador_demanda,1)}.</p><div className="creative-selection-links"><Link className="text-link" href={`/creatividad?${query}&vista=ab&evaluacion=${evaluationId}&variante=${r.data.variante_id}`}>Contrastar selección en A/B<ArrowRight size={13}/></Link><Link className="text-link" href={`/escenarios?${query}&seleccion=${r.data.id}`}>Comparar en un escenario<ArrowRight size={13}/></Link></div></div></section>;
}

export function Workbench({data,query,initial,selectionId}:{data:CreativeCatalog;query:string;initial?:CreativeEvaluation;selectionId:string|null}){
  const router=useRouter(),defaults=initial?.entradas||data.defecto;
  const [channel,setChannel]=useState(defaults.canal),[category,setCategory]=useState(defaults.categoria),[audience,setAudience]=useState(defaults.audiencia);
  const [busy,setBusy]=useState(false),[stage,setStage]=useState(""),[selecting,setSelecting]=useState(false),[dirty,setDirty]=useState(false),[error,setError]=useState("");
  const errorRef=useRef<HTMLParagraphElement>(null),headingRef=useRef<HTMLHeadingElement>(null);
  const r=initial,ready=!!r&&!dirty;
  const platform=data.variantes.find(v=>v.canal===channel)?.plataforma;
  const available=data.canales.find(c=>c.id===channel)?.audiencias||[];
  useEffect(()=>{if(r)headingRef.current?.focus({preventScroll:true});},[r]);

  async function submit(e:FormEvent<HTMLFormElement>){
    e.preventDefault();const f=new FormData(e.currentTarget);setBusy(true);setError("");
    try{
      setStage("Preparando imágenes del catálogo local…");
      await prepararImagenes(data.variantes.filter(v=>v.categoria===category&&v.canal===channel));
      setStage("Componiendo propuestas y calculando la referencia…");
      const result=await post<CreativeEvaluation>("creativos/evaluar",{canal:channel,categoria:category,audiencia:audience,frecuencia:Number(f.get("frecuencia")),impresiones:Number(f.get("impresiones")),objetivo:String(f.get("objetivo"))});
      router.replace(`/creatividad?${query}&vista=pretest&evaluacion=${result.id}`,{scroll:false});setDirty(false);
    }catch(e){setError(e instanceof Error?e.message:"No se ha podido guardar el pretest.");requestAnimationFrame(()=>errorRef.current?.focus());}
    finally{setBusy(false);setStage("");}
  }
  async function select(variant:string){
    if(!r)return;setSelecting(true);setError("");
    try{const s=await post<CreativeSelection>("creativos/selecciones",{pretest_id:r.id,variante_id:variant});router.replace(`/creatividad?${query}&vista=pretest&evaluacion=${r.id}&seleccion=${s.id}`,{scroll:false});}
    catch(e){setError(e instanceof Error?e.message:"No se ha podido guardar la selección.");requestAnimationFrame(()=>errorRef.current?.focus());}
    finally{setSelecting(false);}
  }

  return <section className="creative-workbench" id="pretest">
    <section className="panel">
      <div className="panel-header wrap"><div><h2 id="titulo-pretest">Del brief a tres propuestas.</h2><p>Elige la plataforma y prepara una dirección visual para tu campaña.</p></div><Badge>Demo creativa</Badge></div>
      <form className="creative-form" method="post" action="/api/v1/creativos/evaluar" aria-labelledby="titulo-pretest" onSubmit={submit} onChange={()=>{setDirty(true);setError("");}}>
        <fieldset disabled={busy} className="creative-fields"><legend className="visually-hidden">Contexto de las propuestas</legend><div className="creative-form-grid">
          <div><label htmlFor="pretest-canal">Canal del pretest</label><select id="pretest-canal" name="canal" value={channel} onChange={e=>{const value=e.target.value;setChannel(value);setAudience(data.canales.find(c=>c.id===value)!.audiencias[0]);}}>{data.canales.map(c=><option key={c.id} value={c.id}>{c.nombre}</option>)}</select></div>
          <div><label htmlFor="pretest-perfil">Perfil de partida</label><select id="pretest-perfil" name="categoria" value={category} onChange={e=>setCategory(e.target.value)}>{data.perfiles.map(p=><option key={p.categoria} value={p.categoria}>{p.categoria.charAt(0).toUpperCase()+p.categoria.slice(1)} · {p.tono}</option>)}</select></div>
          <div><label htmlFor="pretest-audiencia">Audiencia del pretest</label><select id="pretest-audiencia" name="audiencia" value={audience} onChange={e=>setAudience(e.target.value)}>{available.map(a=><option key={a}>{a}</option>)}</select></div>
          <div><label htmlFor="pretest-frecuencia">Frecuencia prevista</label><input id="pretest-frecuencia" name="frecuencia" type="number" min={1} max={10} step="0.1" required defaultValue={defaults.frecuencia}/></div>
          <div><label htmlFor="pretest-impresiones">Impresiones de referencia</label><input id="pretest-impresiones" name="impresiones" type="number" min={1000} max={1000000} step={1} required defaultValue={defaults.impresiones}/></div>
          <div className="creative-objective"><label htmlFor="pretest-objetivo">Objetivo del brief (obligatorio)</label><textarea id="pretest-objetivo" name="objetivo" rows={2} minLength={10} maxLength={250} required defaultValue={defaults.objetivo}/></div>
        </div></fieldset>
        {platform&&<div className="creative-placement"><div><strong>{platform.nombre} · {platform.ubicacion}</strong><p>{platform.tratamiento}</p></div><Badge>{platform.relacion} · {platform.tipo}</Badge></div>}
        <div className="creative-form-bottom"><p>Simulación con imágenes sintéticas precreadas. La composición se adapta a la plataforma; el CTR se calcula con el modelo del contexto.</p><button type="submit" className="button primary" disabled={busy}>{busy?<><LoaderCircle size={16} className="creative-spinner"/>Preparando propuestas…</>:<>Generar propuestas de ejemplo<ImagePlus size={16}/></>}</button></div>
      </form>
    </section>
    <p className="form-error" ref={errorRef} tabIndex={-1} role={error?"alert":undefined}>{error}</p>
    {busy&&<div className="creative-preparing" role="status"><LoaderCircle className="creative-spinner" size={22}/><div><strong>{stage}</strong><p>Preparación simulada · recursos locales · sin llamada a IA en ejecución</p></div></div>}
    {dirty&&r&&<Notice>Contexto modificado. Genera las propuestas para ver las imágenes y la referencia de la nueva selección.</Notice>}
    {!ready&&!busy&&<div className="creative-ready-state"><ImagePlus size={28}/><div><h2>Tu próxima campaña empieza aquí.</h2><p>Prepara tres propuestas fotográficas para {platform?.nombre||channel}, con el formato y la jerarquía de ese placement.</p><small>Las imágenes son ejemplos sintéticos de un catálogo local. No hay generación de vídeo.</small></div></div>}
    {ready&&r&&<>
      <div className="creative-result-heading"><h2 ref={headingRef} tabIndex={-1}>Propuestas preparadas para {r.variantes[0]?.plataforma?.nombre||r.entradas.canal}</h2><Badge>{r.variantes[0]?.plataforma?.relacion||"Diseño anterior"}</Badge></div>
      <p className="creative-run-status" role="status">{r.reutilizada?"Evaluación guardada consultada.":"Propuestas preparadas y evaluación guardada."} Imágenes sintéticas precreadas; modelo {r.version}.</p>
      <div className="creative-comparison" aria-label="Tres composiciones originales">{r.variantes.map((v,i)=><article className="creative-variant" key={v.id} data-testid="variante-pretest">
        <div className="creative-variant-number">Propuesta {i+1} · {v.categoria}<span>{v.plataforma?.tipo||"Composición original"}</span></div>
        <CreativeArt variant={v} priority={i===0}/>
        <div className="creative-variant-body"><h3>{v.nombre}</h3><p>{v.composicion}</p><dl><dt>Tono</dt><dd>{v.tono}</dd><dt>CTA</dt><dd>{v.cta}</dd></dl><p className="small">Referencia histórica, sin efecto visual en el predictor</p><button type="button" className="button secondary" disabled={selecting} onClick={()=>select(v.id)}>Guardar propuesta {i+1}<ArrowRight size={14}/></button></div>
      </article>)}</div>
      {selectionId&&<Selection id={selectionId} evaluationId={r.id} query={query}/>}
      <div className="ab-entry"><p>Contrasta estas propuestas con observaciones nuevas y asignación aleatoria.</p><Link className="button secondary" href={`/creatividad?${query}&vista=ab&evaluacion=${r.id}`}>Preparar prueba A/B<FlaskConical size={15}/></Link></div>
      <AprendizajeCreativo pretest={r} query={query}/>
      <div className="creative-result-heading"><h2>Referencia del contexto evaluado</h2><Badge tone={r.estado==="bloqueado"?"warning":"neutral"}>{r.estado==="bloqueado"?"Predictor bloqueado":"Hipótesis"}</Badge></div>
      <div className="model-metrics creative-estimates"><article><small>CTR de referencia compartido</small><strong data-testid="ctr-pretest">{porcentaje(r.referencia.ctr,2)}</strong><p>p05–p95: {porcentaje(r.referencia.p05,2)} — {porcentaje(r.referencia.p95,2)}</p></article><article><small>Clics de referencia</small><strong data-testid="clics-pretest">{numero(r.referencia.clics_esperados)}</strong><p>Sobre {numero(r.entradas.impresiones)} impresiones</p></article><article><small>CVR observado de entrenamiento</small><strong>{porcentaje(r.referencia.cvr_observado,2)}</strong><p>{numero(r.referencia.cvr_conversiones)} conversiones / {numero(r.referencia.cvr_clics)} clics</p></article><article><small>Diferencia visual identificada</small><strong>Sin evidencia</strong><p>El modelo no distingue estas composiciones</p></article></div>
      <p className="creative-run-status">{r.referencia.fuente}. Bandas de parámetros por grupos; no son intervalos de nuevos clics.</p>
      <Notice><strong>Sin ganador predictivo</strong>{r.motivos.map(m=><p key={m}>{m}</p>)}</Notice>
      <section className="panel creative-brief"><div className="panel-header"><div><h2>Brief preparado por reglas</h2><p>{r.brief.metodo}</p></div><FlaskConical size={18}/></div><div className="creative-brief-body"><h3>{r.brief.objetivo}</h3><p>{r.brief.texto}</p><ul>{r.brief.reglas.map(rule=><li key={rule}>{rule}</li>)}</ul><details className="search-assumptions"><summary>Supuestos y trazabilidad</summary><ul className="model-notes">{r.advertencias.map(a=><li key={a}>{a}</li>)}</ul><p className="checksum">{r.id} · {r.modelo} · semilla {r.semilla}</p><a className="text-link" href={`/api/v1/creativos/evaluaciones/${r.id}`} target="_blank" rel="noreferrer">Consultar evaluación guardada<ArrowRight size={13}/></a></details></div></section>
    </>}
  </section>;
}
