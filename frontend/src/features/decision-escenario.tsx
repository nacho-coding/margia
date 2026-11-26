"use client";

import {useEffect,useRef,useState,type FormEvent} from "react";
import Link from "next/link";
import {useRouter} from "next/navigation";
import {ArrowRight,Download,ShieldCheck} from "lucide-react";
import {Badge,Loading,Notice} from "@/components/ui";
import {ErrorState} from "@/components/error-state";
import {euros,fecha,porcentaje,post} from "@/services/api";
import {useRemote} from "@/services/use-remote";
import type {ScenarioDecision,ScenarioDecisionContext,ScenarioPlanId} from "@/services/escenarios";

export function ScenarioExports({id}:{id:string}){
  return <div className="scenario-exports" aria-label="Exportar comparación guardada"><a className="button secondary" href={`/api/v1/escenarios/ejecuciones/${id}/exportar?formato=csv`} download><Download size={15}/>Descargar CSV</a><a className="button secondary" href={`/api/v1/escenarios/ejecuciones/${id}/exportar?formato=md`} download><Download size={15}/>Descargar Markdown</a></div>;
}

function DecisionRecord({data,query}:{data:ScenarioDecision;query:string}){
  const heading=useRef<HTMLHeadingElement>(null),e=data.evidencia;
  useEffect(()=>{heading.current?.focus({preventScroll:true});},[data.id]);
  return <section className="panel scenario-decision-record" data-testid="decision-guardada"><div className="panel-header"><div><p className="eyebrow">DECISIÓN SIMULADA REGISTRADA</p><h2 ref={heading} tabIndex={-1}>{data.estado==="aprobado"?"Aprobación registrada":"Rechazo registrado"}</h2><p>{e.nombre_plan} · revisión {e.revision}</p></div><ShieldCheck size={20}/></div><div className="scenario-panel-body"><Badge tone={data.estado==="aprobado"?"positive":"neutral"}>{data.estado==="aprobado"?"Aprobado":"Rechazado"}</Badge><p className="scenario-decision-reason">{data.motivo}</p><p className="small">Fecha de sistema: <time dateTime={data.creado}>{new Date(data.creado).toLocaleString("es-ES",{timeZone:"Europe/Madrid"})}</time>. La fecha del registro se distingue del periodo proyectado.</p>
    <dl className="definition-list"><dt>Horizonte nacional</dt><dd>{fecha(e.periodo.inicio)} — {fecha(e.periodo.fin)}</dd><dt>Contribución neta puntual del plan</dt><dd>{euros(e.metricas?.contribucion)}</dd><dt>Δ esperado / p05–p95</dt><dd>{euros(e.banda?.media)} · {euros(e.banda?.p05)} — {euros(e.banda?.p95)}</dd><dt>Probabilidad de pérdida</dt><dd>{porcentaje(e.banda?.probabilidad_perdida)}</dd><dt>Guardrails al registrar</dt><dd>{e.guardrails.aprobable?"Plan elegible en el momento del registro":e.guardrails.motivos.join(" ")}</dd><dt>Snapshot / semilla</dt><dd className="checksum">{data.snapshot} · {e.semilla}</dd><dt>Motor / Search / MMM</dt><dd className="checksum">{e.version} · {e.modelos.search.id} · {e.modelos.mmm.id}</dd><dt>Decisión / ejecución</dt><dd className="checksum">{data.id} · {data.ejecucion}</dd></dl>
    <Notice>Este registro es terminal y conserva su evidencia. No activa publicidad ni modifica pedidos, inversiones o decisiones anteriores.</Notice><div className="form-actions"><Link className="text-link" href={`/escenarios?${query}&decision=${data.id}`}>Abrir decisión por su ID<ArrowRight size={13}/></Link><Link className="text-link" href={`/escenarios?${query}&ejecucion=${data.ejecucion}`}>Consultar comparación<ArrowRight size={13}/></Link></div><ScenarioExports id={data.ejecucion}/>
  </div></section>;
}

export function SavedDecision({id,query}:{id:string;query:string}){
  const r=useRemote<ScenarioDecision>(`decisiones/${id}`);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  return r.data?<DecisionRecord data={r.data} query={query}/>:<Loading/>;
}

export function ScenarioDecisionPanel({id,query}:{id:string;query:string}){
  const r=useRemote<ScenarioDecisionContext>(`escenarios/ejecuciones/${id}/decision`),router=useRouter();
  const [plan,setPlan]=useState<ScenarioPlanId>("base"),[estado,setEstado]=useState("aprobado"),[saved,setSaved]=useState<ScenarioDecision|null>(null);
  const [busy,setBusy]=useState(false),[error,setError]=useState("");
  const errorRef=useRef<HTMLParagraphElement>(null);
  useEffect(()=>{if(error&&!busy)errorRef.current?.focus();},[error,busy]);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <p role="status" className="small">Comprobando la evidencia disponible para decidir…</p>;
  const d=r.data,record=saved||d.decision,selected=d.planes.find(p=>p.id===plan)!;
  if(record)return <DecisionRecord data={record} query={query}/>;
  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();const f=new FormData(event.currentTarget);setBusy(true);setError("");
    try{const decision=await post<ScenarioDecision>(`escenarios/ejecuciones/${id}/decision`,{plan,estado,motivo:String(f.get("motivo"))});setSaved(decision);router.replace(`/escenarios?${query}&ejecucion=${id}&decision=${decision.id}`,{scroll:false});}
    catch(e){setError(e instanceof Error?e.message:"No se ha podido registrar la decisión.");}
    finally{setBusy(false);}
  }
  return <section className="panel scenario-decision"><div className="panel-header"><div><h2 id="decision-title">Registrar una decisión</h2><p>Antes de aprobar se comprueban la evidencia vigente, la revisión, los límites y el riesgo.</p></div><Badge>Simulada</Badge></div><form className="scenario-form" action={`/api/v1/escenarios/ejecuciones/${id}/decision`} method="post" aria-labelledby="decision-title" onSubmit={submit} onInput={()=>setError("")}>
    <fieldset disabled={busy} className="scenario-fields-reset"><legend className="visually-hidden">Plan, resolución y motivo</legend><fieldset className="scenario-radio-group"><legend>Plan sobre el que decidir *</legend><div className="scenario-radio-options">{d.planes.map(p=><label key={p.id}><input type="radio" name="plan" value={p.id} required checked={plan===p.id} onChange={()=>setPlan(p.id)}/><span>{p.nombre}<small>{p.aprobable?"Elegible para aprobación simulada":"Aprobación bloqueada"}</small></span></label>)}</div></fieldset>
    {!selected.aprobable&&<div className="scenario-decision-block" role="status"><strong>La aprobación de este plan está bloqueada</strong><ul>{selected.motivos.map(m=><li key={m}>{m}</li>)}</ul><p>Puedes registrar un rechazo con motivo o preparar otra comparación.</p></div>}
    <fieldset className="scenario-radio-group"><legend>Resolución *</legend><div className="scenario-radio-options">{[["aprobado","Aprobar de forma simulada"],["rechazado","Rechazar el plan"]].map(([value,label])=><label key={value}><input type="radio" name="estado" value={value} checked={estado===value} onChange={()=>setEstado(value)} required/><span>{label}</span></label>)}</div></fieldset>
    <div className="scenario-field"><label htmlFor="decision-motivo">Motivo de la decisión *</label><textarea id="decision-motivo" name="motivo" required minLength={10} maxLength={1000} rows={4} aria-describedby="decision-ayuda"/><p id="decision-ayuda" className="small">Entre 10 y 1.000 caracteres. Indica por qué actúas o te abstienes; se conservará con el plan y su evidencia.</p></div></fieldset>
    <Notice>{d.alcance}</Notice><button type="submit" className="button primary" disabled={busy}>{busy?"Registrando decisión…":"Registrar decisión"}<ArrowRight size={15}/></button><p className="form-error" role={error?"alert":"status"} ref={errorRef} tabIndex={-1}>{error||(busy?"Revalidando y guardando la decisión…":"")}</p>
  </form></section>;
}
