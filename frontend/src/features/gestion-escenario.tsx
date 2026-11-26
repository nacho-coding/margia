"use client";

import {useEffect,useId,useRef,useState,type FormEvent} from "react";
import Link from "next/link";
import {useRouter} from "next/navigation";
import {Archive,ArrowRight,Copy} from "lucide-react";
import {Badge,Loading} from "@/components/ui";
import {ErrorState} from "@/components/error-state";
import {fecha,post} from "@/services/api";
import {useRemote} from "@/services/use-remote";
import type {ScenarioDraft} from "@/services/escenarios";

function ScenarioActionDialog({data,action,onClose,onDone}:{data:ScenarioDraft;action:"duplicar"|"archivar";onClose:()=>void;onDone:(s:ScenarioDraft)=>void}){
  const dialog=useRef<HTMLDialogElement>(null),safeAction=useRef<HTMLButtonElement>(null),errorRef=useRef<HTMLParagraphElement>(null),title=useId();
  const [busy,setBusy]=useState(false),[error,setError]=useState("");
  useEffect(()=>{if(error&&!busy)errorRef.current?.focus();},[error,busy]);
  useEffect(()=>{const el=dialog.current;if(safeAction.current)safeAction.current.autofocus=true;el?.showModal();return()=>el?.close();},[]);
  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();setError("");setBusy(true);
    const f=new FormData(event.currentTarget);
    try{const s=await post<ScenarioDraft>(`escenarios/${data.id}/${action}`,action==="duplicar"?{nombre:String(f.get("nombre"))}:{revision:data.revision,motivo:String(f.get("motivo"))});onDone(s);dialog.current?.close();}
    catch(e){setError(e instanceof Error?e.message:"No se ha podido guardar el cambio.");}
    finally{setBusy(false);}
  }
  return <dialog ref={dialog} className="scenario-dialog" aria-labelledby={title} onClose={onClose} onCancel={e=>{if(busy)e.preventDefault();}}>
    <h1 id={title}>{action==="duplicar"?"Duplicar escenario":"Archivar escenario"}</h1>
    <p>{action==="duplicar"?"La copia empieza en revisión 1 y conserva los parámetros. Sus nuevas ejecuciones tendrán identidad propia.":"Se conservarán sus revisiones, comparaciones y decisiones. Para continuar después, podrás crear una copia."}</p>
    <p className="small">{data.nombre} · revisión {data.revision}</p>
    <form className="scenario-form" action={`/api/v1/escenarios/${data.id}/${action}`} method="post" aria-labelledby={title} onSubmit={submit} onInput={()=>setError("")}>
      {action==="duplicar"?<div className="scenario-field"><label htmlFor={`${title}-nombre`}>Nombre de la copia *</label><input id={`${title}-nombre`} name="nombre" required minLength={3} maxLength={100} defaultValue={`Copia de ${data.nombre}`.slice(0,100)} disabled={busy}/></div>:<div className="scenario-field"><label htmlFor={`${title}-motivo`}>Motivo del archivo *</label><textarea id={`${title}-motivo`} name="motivo" required minLength={10} maxLength={1000} rows={3} disabled={busy} aria-describedby={`${title}-ayuda`}/><p id={`${title}-ayuda`} className="small">Entre 10 y 1.000 caracteres. El motivo quedará en el historial.</p></div>}
      <div className="form-actions"><button type="button" ref={safeAction} disabled={busy} className="button secondary" onClick={()=>dialog.current?.close()}>Conservar sin cambios</button><button type="submit" className={`button ${action==="archivar"?"danger":"primary"}`} disabled={busy}>{busy?"Guardando…":action==="archivar"?"Archivar con motivo":"Crear copia"}</button></div>
      <p role={error?"alert":"status"} tabIndex={-1} ref={errorRef} className="form-error">{error|| (busy?"Guardando el cambio en el historial…":"")}</p>
    </form>
  </dialog>;
}

export function ScenarioActions({id,query,onChanged}:{id:string;query:string;onChanged?:()=>void}){
  const r=useRemote<ScenarioDraft>(`escenarios/${id}`),router=useRouter();
  const [action,setAction]=useState<"duplicar"|"archivar"|null>(null);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <p role="status" className="small">Consultando revisiones del escenario…</p>;
  const s=r.data;
  function done(d:ScenarioDraft){if(action==="duplicar")router.push(`/escenarios?${query}&escenario=${d.id}`);else{r.retry();onChanged?.();}}
  return <div className="scenario-management"><div><Badge tone={s.estado==="archivado"?"warning":"neutral"}>{s.estado==="archivado"?"Archivado":s.editable?"Borrador editable":"Configuración conservada"}</Badge><span className="small">Revisión actual {s.revision}</span></div><div className="scenario-management-actions"><Link className="text-link" href={`/escenarios?${query}&escenario=${id}`}>Ver revisiones<ArrowRight size={13}/></Link><button type="button" className="button secondary" onClick={()=>setAction("duplicar")}><Copy size={15}/>Duplicar</button>{s.estado!=="archivado"&&<button type="button" className="button secondary" onClick={()=>setAction("archivar")}><Archive size={15}/>Archivar</button>}</div>{action&&<ScenarioActionDialog data={s} action={action} onClose={()=>setAction(null)} onDone={done}/>}</div>;
}

export function ScenarioRevisions({data,query}:{data:ScenarioDraft;query:string}){
  return <section className="panel scenario-revisions"><div className="panel-header"><div><h2>Revisiones y comparaciones</h2><p>La edición conserva las entradas y los resultados de cada revisión anterior.</p></div></div><div className="scenario-panel-body">
    {data.ejecuciones.length?<ul className="scenario-execution-list">{data.ejecuciones.map(e=><li key={e.id}><Link className="text-link" href={`/escenarios?${query}&ejecucion=${e.id}`}>Revisión {e.revision} · {e.nombre}<ArrowRight size={13}/></Link><small>{fecha(e.creado.slice(0,10))}</small></li>)}</ul>:<p>Este borrador aún no se ha ejecutado. Guardarlo conserva parámetros, sin calcular un resultado.</p>}
    <details><summary>Consultar entradas por revisión ({data.revisiones.length})</summary>{data.revisiones.map(r=><details key={r.revision} className="scenario-revision-input"><summary>Revisión {r.revision} · {r.parametros.nombre} · {fecha(r.creado.slice(0,10))}</summary><pre>{JSON.stringify(r.parametros,null,2)}</pre></details>)}</details>
    <details><summary>Consultar registro temporal ({data.eventos.length})</summary><ol className="scenario-event-list">{data.eventos.map((e,i)=><li key={i}><strong>{e.tipo} · revisión {e.revision}</strong><time dateTime={e.creado}>{new Date(e.creado).toLocaleString("es-ES",{timeZone:"Europe/Madrid"})}</time><p>{e.motivo}</p></li>)}</ol></details>
  </div></section>;
}

export function ScenarioDraftResource({id,children}:{id:string;children:(d:ScenarioDraft,retry:()=>void)=>React.ReactNode}){
  const r=useRemote<ScenarioDraft>(`escenarios/${id}`);
  return r.error?<ErrorState message={r.error} retry={r.retry}/>:r.data?children(r.data,r.retry):<Loading/>;
}
