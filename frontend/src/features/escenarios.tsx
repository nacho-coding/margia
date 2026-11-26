"use client";

import {useEffect,useRef,useState,type FormEvent} from "react";
import Link from "next/link";
import {useRouter,useSearchParams} from "next/navigation";
import {ArrowRight,History,ShieldAlert} from "lucide-react";
import {Badge,Loading,Notice} from "@/components/ui";
import {CreativeArt} from "@/components/creative-art";
import {ErrorState} from "@/components/error-state";
import {euros,fecha,numero,post} from "@/services/api";
import {useRemote} from "@/services/use-remote";
import type {ScenarioCatalog,ScenarioDraft,ScenarioExecution,ScenarioInputs} from "@/services/escenarios";
import {ScenarioReport} from "@/features/resultado-escenario";
import {ScenarioActions,ScenarioDraftResource,ScenarioRevisions} from "@/features/gestion-escenario";
import {SavedDecision} from "@/features/decision-escenario";

function Numeric({name,label,value,min=0,max=1000000,step=.01}:{name:string;label:string;value:number;min?:number;max?:number;step?:number}){
  return <div className="scenario-field"><label htmlFor={`esc-${name}`}>{label} <span aria-hidden="true">*</span></label><input id={`esc-${name}`} name={name} type="number" required min={min} max={max} step={step} defaultValue={value}/></div>;
}

function ScenarioForm({data,query,initialChannel,onSaved,onDraft,draft}:{data:ScenarioCatalog;query:string;initialChannel:string|null;onSaved:(d:ScenarioExecution)=>void;onDraft:(d:ScenarioDraft)=>void;draft?:ScenarioDraft}){
  const d=draft?.parametros||data.defecto;
  const [stored,setStored]=useState(draft);
  const search=useSearchParams();
  const [creative,setCreative]=useState(d.seleccion_creativa_id||"");
  const [channel,setChannel]=useState(d.seleccion_creativa_id?d.canal_reinversion:data.canales.find(c=>c.canal===initialChannel)?.canal||d.canal_reinversion);
  const [busy,setBusy]=useState(false),[error,setError]=useState("");
  const errorRef=useRef<HTMLParagraphElement>(null);
  useEffect(()=>{if(error&&!busy)errorRef.current?.focus();},[error,busy]);
  const chosen=data.selecciones.find(s=>s.id===creative);
  function selectCreative(id:string){setCreative(id);const s=data.selecciones.find(s=>s.id===id);if(s)setChannel(s.canal);}
  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();setError("");
    if(search.get("mercado")){setError("La comparación es nacional. Selecciona «Todos los mercados» para calcularla.");return;}
    const f=new FormData(event.currentTarget);
    if(Number(f.get("coste_produccion"))>0&&!creative){setError("Selecciona una propuesta guardada o deja su coste de producción en cero.");return;}
    if(chosen&&channel!==chosen.canal){setError("La propuesta seleccionada y el canal de reinversión deben coincidir.");return;}
    setBusy(true);
    try{
      const parametros:ScenarioInputs={...d,nombre:String(f.get("nombre")),
        recorte_pct:Number(f.get("recorte_pct")),reinversion_pct:Number(f.get("reinversion_pct")),canal_reinversion:channel,
        seleccion_creativa_id:creative||null,coste_produccion:Number(f.get("coste_produccion")),coste_experimento:Number(f.get("coste_experimento")),
        cuota_plataforma:Number(f.get("cuota_plataforma")),otros_costes:Number(f.get("otros_costes")),plataforma_comun:f.has("plataforma_comun"),
        presupuesto_total:Number(f.get("presupuesto_total")),recorte_max_pct:Number(f.get("recorte_max_pct")),riesgo_max_pct:Number(f.get("riesgo_max_pct")),
        semilla:Number(f.get("semilla")),limites:data.canales.map(c=>({canal:c.canal,minimo:Number(f.get(`min-${c.canal}`)),maximo:Number(f.get(`max-${c.canal}`))}))};
      const saveOnly=(event.nativeEvent as SubmitEvent).submitter?.getAttribute("value")==="guardar";
      if(saveOnly||stored){
        const s=stored?await post<ScenarioDraft>(`escenarios/${stored.id}`,{revision:stored.revision,parametros},"PATCH"):await post<ScenarioDraft>("escenarios",parametros);
        setStored(s);
        if(saveOnly){onDraft(s);return;}
        onSaved(await post<ScenarioExecution>(`escenarios/${s.id}/ejecutar`,{revision:s.revision}));
      }else onSaved(await post<ScenarioExecution>("escenarios/ejecutar",parametros));
    }catch(e){setError(e instanceof Error?e.message:"No se ha podido comparar las alternativas.");}
    finally{setBusy(false);}
  }
  return <div className="scenario-design"><section className="panel"><div className="panel-header"><div><h2 id="scenario-form-title">{draft?"Editar borrador":"Preparar comparación"}</h2><p>Base compartida, ahorro y reinversión. Los campos con * son obligatorios.</p></div></div>
    <form className="scenario-form" method="post" action="/api/v1/escenarios/ejecutar" aria-labelledby="scenario-form-title" onSubmit={submit} onChange={()=>setError("")}>
      <fieldset disabled={busy} className="scenario-fields-reset"><legend className="visually-hidden">Parámetros de la comparación</legend>
        <div className="scenario-field"><label htmlFor="esc-nombre">Nombre de la comparación *</label><input id="esc-nombre" name="nombre" required minLength={3} maxLength={100} defaultValue={d.nombre}/></div>
        <fieldset className="scenario-group"><legend>Intervención</legend><div className="scenario-fields"><Numeric name="recorte_pct" label="Recorte de SEM marca (%)" value={d.recorte_pct} max={100}/><Numeric name="reinversion_pct" label="Ahorro que reinvertir (%)" value={d.reinversion_pct} max={100}/></div>
          <div className="scenario-field"><label htmlFor="esc-canal">Canal de reinversión *</label><select id="esc-canal" name="canal_reinversion" required value={channel} onChange={e=>setChannel(e.target.value)}>{data.canales.map(c=><option key={c.canal} value={c.canal}>{c.nombre}</option>)}</select></div>
          <p className="small">A conserva el ahorro. B destina la fracción indicada al canal elegido; el resto se conserva. La búsqueda también considera mantener.</p>
        </fieldset>
        <fieldset className="scenario-group"><legend>Creatividad y producción</legend><div className="scenario-field"><label htmlFor="esc-creativa">Propuesta guardada</label><select id="esc-creativa" name="seleccion_creativa_id" value={creative} onChange={e=>selectCreative(e.target.value)}><option value="">Sin propuesta nueva</option>{data.selecciones.map(s=><option key={s.id} value={s.id}>{s.canal} · {s.nombre} · {s.id.slice(-6)}</option>)}</select></div>
          <Numeric name="coste_produccion" label="Producción pendiente para B (€)" value={d.coste_produccion}/><p className="small">El coste se imputa una vez al lanzar la propuesta seleccionada en su canal. Aprender CTR mantiene el multiplicador económico en 1.</p>
        </fieldset>
        <details className="scenario-advanced"><summary>Costes del periodo y semilla</summary><p className="small">Importes para el mismo horizonte. Introduce solo costes pendientes; los experimentos ya realizados no se vuelven a cobrar.</p><div className="scenario-fields"><Numeric name="coste_experimento" label="Experimento pendiente por alternativa (€)" value={d.coste_experimento}/><Numeric name="cuota_plataforma" label="Cuota de plataforma del periodo (€)" value={d.cuota_plataforma}/><Numeric name="otros_costes" label="Otros costes incrementales (€)" value={d.otros_costes}/><Numeric name="semilla" label="Semilla" value={d.semilla} max={2147483647} step={1}/></div><label className="scenario-check"><input type="checkbox" name="plataforma_comun" defaultChecked={d.plataforma_comun}/><span>La cuota ya se paga en la base y en las alternativas</span></label></details>
        <details className="scenario-advanced"><summary>Restricciones de búsqueda y límites por canal</summary><div className="scenario-fields"><Numeric name="presupuesto_total" label="Techo total de medios (€)" value={d.presupuesto_total} max={10000000}/><Numeric name="recorte_max_pct" label="Recorte máximo permitido (%)" value={d.recorte_max_pct} max={100}/><Numeric name="riesgo_max_pct" label="Probabilidad máxima de pérdida (%)" value={d.riesgo_max_pct} max={100}/></div><p className="small">Se puede conservar la inversión actual aunque salga del soporte. Cualquier cambio debe respetar el soporte observado en cada semana. El techo se refiere a medios; producción, prueba y plataforma figuran aparte.</p>
          <div className="table-wrapper scenario-table scenario-limits" tabIndex={0} role="region" aria-label="Límites de inversión por canal"><table><caption className="visually-hidden">Inversión de referencia y límites para los 28 días</caption><thead><tr><th scope="col">Canal</th><th scope="col">Referencia</th><th scope="col">Mínimo (€)</th><th scope="col">Máximo (€)</th></tr></thead><tbody>{data.canales.map(c=>{const l=d.limites.find(l=>l.canal===c.canal)!;return <tr key={c.canal}><th scope="row">{c.nombre}{c.actual_fuera_soporte&&<small>Actual fuera del soporte de cambios</small>}</th><td>{euros(c.actual)}</td><td><label className="visually-hidden" htmlFor={`esc-min-${c.canal}`}>Mínimo de {c.nombre} (€)</label><input id={`esc-min-${c.canal}`} name={`min-${c.canal}`} type="number" required min={c.minimo} max={c.maximo} step="0.01" defaultValue={l.minimo}/></td><td><label className="visually-hidden" htmlFor={`esc-max-${c.canal}`}>Máximo de {c.nombre} (€)</label><input id={`esc-max-${c.canal}`} name={`max-${c.canal}`} type="number" required min={c.minimo} max={c.maximo} step="0.01" defaultValue={l.maximo}/></td></tr>;})}</tbody></table></div>
        </details>
      </fieldset>
      <div className="form-actions"><button type="submit" name="accion" value="comparar" className="button primary" disabled={busy}>{busy?"Guardando y preparando resultado…":"Comparar y buscar alternativa"}<ArrowRight size={15}/></button><button type="submit" name="accion" value="guardar" className="button secondary" disabled={busy}>Guardar borrador</button></div>
      {busy&&<p role="status">Calculando las alternativas con las mismas réplicas y verificando las restricciones…</p>}<p ref={errorRef} className="form-error" tabIndex={-1} role={error?"alert":undefined}>{error}</p>
    </form></section>
    <aside className="scenario-sidebar"><section className="panel scenario-reference"><div className="panel-header"><div><h2>Base compartida</h2><p>Proyección nacional · {fecha(data.inicio)} — {fecha(data.fin)}</p></div></div><div className="scenario-panel-body"><strong>{numero(data.proyeccion.pedidos)} pedidos</strong><p>{data.proyeccion.metodo}.</p><dl className="definition-list"><dt>Inversión de referencia</dt><dd>{euros(data.referencia.inversion)}</dd><dt>Pedidos observados</dt><dd>{numero(data.referencia.pedidos)}</dd><dt>Periodo observado</dt><dd>{fecha(data.referencia.periodo.inicio)} — {fecha(data.referencia.periodo.fin)}</dd></dl><p className="small">El ticket y el margen por pedido se fijan con esta referencia. Es una proyección condicionada, con incertidumbre compartida.</p></div></section>
      {chosen?<section className="panel scenario-creative"><div className="panel-header"><div><h2>Propuesta para B</h2><p>{chosen.nombre} · {chosen.canal}</p></div></div><CreativeArt variant={chosen.variante} priority/><div className="scenario-panel-body"><Link className="text-link" href={`/creatividad?${query}&vista=pretest&evaluacion=${chosen.pretest}&seleccion=${chosen.id}`}>Consultar pretest y aprendizaje<ArrowRight size={13}/></Link></div></section>:<section className="panel scenario-reference"><div className="scenario-panel-body"><h2>Conservar las creatividades actuales</h2><p>También puedes partir de una propuesta guardada en el pretest y comparar su coste de producción.</p><Link className="text-link" href={`/creatividad?${query}&vista=pretest`}>Preparar una propuesta<ArrowRight size={13}/></Link></div></section>}
    </aside>
  </div>;
}

function SavedExecution({id,query}:{id:string;query:string}){
  const r=useRemote<ScenarioExecution>(`escenarios/ejecuciones/${id}`);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <Loading/>;
  return <ScenarioReport data={r.data} query={query}/>;
}

function DraftEditor({draft,query,onSaved,onDraft}:{draft:ScenarioDraft;query:string;onSaved:(d:ScenarioExecution)=>void;onDraft:(d:ScenarioDraft)=>void}){
  const source=new URLSearchParams({...draft.parametros.seleccion_creativa_id?{seleccion:draft.parametros.seleccion_creativa_id}:{},...draft.parametros.simulacion_search_id?{simulacion:draft.parametros.simulacion_search_id}:{}});
  const r=useRemote<ScenarioCatalog>(`escenarios?${source}`);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <Loading/>;
  return <ScenarioForm key={`${draft.id}:${draft.revision}`} data={r.data} query={query} initialChannel={null} draft={draft} onSaved={onSaved} onDraft={onDraft}/>;
}

export function Escenarios({query}:{query:string}){
  const search=useSearchParams(),router=useRouter();
  const selection=search.get("seleccion"),simulation=search.get("simulacion"),eid=search.get("ejecucion"),channel=search.get("canal"),sid=search.get("escenario"),did=search.get("decision");
  const source=new URLSearchParams({...(selection?{seleccion:selection}:{}),...(simulation?{simulacion:simulation}:{})}).toString();
  const r=useRemote<ScenarioCatalog>(`escenarios${source?`?${source}`:""}`);
  const [created,setCreated]=useState<ScenarioExecution|null>(null);
  if(r.error&&!eid&&!did&&!sid)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data&&!eid&&!did&&!sid)return <Loading/>;
  const d=r.data;
  function saved(e:ScenarioExecution){setCreated(e);r.retry();router.replace(`/escenarios?${query}&ejecucion=${e.id}`,{scroll:false});}
  function draftSaved(s:ScenarioDraft){r.retry();router.replace(`/escenarios?${query}&escenario=${s.id}`,{scroll:false});}
  return <div className="scenario-workspace">
    {eid?<>{created?.id===eid?<ScenarioReport data={created} query={query}/>:<SavedExecution key={eid} id={eid} query={query}/>}</>:did?<SavedDecision id={did} query={query}/>:sid?<ScenarioDraftResource key={sid} id={sid}>{(s,retry)=><><div className="scenario-report-heading"><div><p className="eyebrow">ESCENARIO CONSERVADO</p><h2>{s.nombre}</h2><p role="status">{s.estado==="archivado"?"Archivado":s.editable?"Borrador guardado":"Configuración de solo lectura"} · revisión {s.revision}</p></div><Link className="button secondary" href={`/escenarios?${query}`}>Preparar otra comparación<ArrowRight size={14}/></Link></div><ScenarioActions id={s.id} query={query} onChanged={retry}/>{s.editable&&s.estado!=="archivado"?<DraftEditor draft={s} query={query} onSaved={saved} onDraft={s=>{draftSaved(s);retry();}}/>:<Notice>Consulta las comparaciones y entradas conservadas o duplica este escenario para preparar un borrador nuevo.</Notice>}<ScenarioRevisions data={s} query={query}/></>}</ScenarioDraftResource>:d?<>
      <div className="scenario-status"><ShieldAlert size={20}/><div><strong>{d.modelos.mmm.optimizable?"Comparación con restricciones y evidencia":"La reinversión conserva su carácter de hipótesis"}</strong><p>{d.modelos.mmm.motivos.join(" ")} La búsqueda automática respeta las dependencias del modelo.</p><Link className="text-link" href={`/medicion?${query}`}>Revisar diagnóstico de medición<ArrowRight size={13}/></Link></div><Badge tone="warning">{d.modelos.mmm.estado==="bloqueado"?"MMM bloqueado":"Uso limitado"}</Badge></div>
      {search.get("mercado")&&<Notice>El laboratorio trabaja a nivel nacional. Selecciona todos los mercados para calcular una comparación nueva.</Notice>}
      {d.origen_search&&<Notice>Partida desde una evaluación Search guardada. Se recuperan sus parámetros y se recalcula con la evidencia vigente para el horizonte proyectado.<p className="checksum">{d.origen_search.id}</p><a className="text-link" href={`/api/v1/busqueda/simulaciones/${d.origen_search.id}`} target="_blank" rel="noreferrer">Consultar evaluación de origen<ArrowRight size={13}/></a></Notice>}
      <p className="period-caption">Horizonte fijo de {d.defecto.horizonte_dias} días · nacional · los filtros de lectura no alteran el protocolo de la comparación.</p>
      <ScenarioForm key={`${source}:${channel||""}`} data={d} query={query} initialChannel={channel} onSaved={saved} onDraft={draftSaved}/>
    </>:null}
    {d&&d.escenarios.length>0&&<section className="panel scenario-history"><div className="panel-header"><div><h2>Escenarios y borradores</h2><p>Últimos 50 escenarios del snapshot activo. Archivar conserva el historial.</p></div></div><div className="table-wrapper scenario-table" tabIndex={0} role="region" aria-label="Escenarios y borradores guardados"><table><caption className="visually-hidden">Escenarios, estado y revisión actual</caption><thead><tr><th scope="col">Escenario</th><th scope="col">Estado</th><th scope="col">Revisión</th><th scope="col">Consultar</th></tr></thead><tbody>{d.escenarios.map(s=><tr key={s.id}><th scope="row">{s.nombre}</th><td>{s.estado==="archivado"?"Archivado":s.editable?"Borrador editable":"Configuración conservada"}</td><td>{s.revision}</td><td><Link className="text-link" href={`/escenarios?${query}&escenario=${s.id}`}>Ver escenario<ArrowRight size={13}/></Link></td></tr>)}</tbody></table></div></section>}
    {d&&d.filas.length>0&&<section className="panel scenario-history"><div className="panel-header"><div><h2>Comparaciones guardadas</h2><p>Las lecturas recuperan resultados; no ejecutan de nuevo el cálculo.</p></div><History size={17}/></div><div className="table-wrapper scenario-table" tabIndex={0} role="region" aria-label="Historial de comparaciones"><table><caption className="visually-hidden">Últimas ejecuciones de escenarios</caption><thead><tr><th scope="col">Comparación</th><th scope="col">Guardada</th><th scope="col">Lectura de la búsqueda</th><th scope="col">Consultar</th></tr></thead><tbody>{d.filas.map(f=><tr key={f.id}><th scope="row">{f.nombre}</th><td>{fecha(f.creado.slice(0,10))}</td><td>{f.recomendacion}</td><td><Link className="text-link" href={`/escenarios?${query}&ejecucion=${f.id}`}>Abrir<ArrowRight size={13}/></Link></td></tr>)}</tbody></table></div></section>}
  </div>;
}
