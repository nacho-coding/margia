"use client";

import {useEffect,useRef,useState,type FormEvent} from "react";
import Link from "next/link";
import {useRouter} from "next/navigation";
import dynamic from "next/dynamic";
import {ArrowRight,Check,FlaskConical,Plus} from "lucide-react";
import {Badge,Loading,Notice} from "@/components/ui";
import {CreativeArt} from "@/components/creative-art";
import {ErrorState} from "@/components/error-state";
import {euros,fecha,numero,porcentaje,post} from "@/services/api";
import {useRemote} from "@/services/use-remote";
import type {CreativeEvaluation,CreativeVariant} from "@/services/creatividad";
import type {ABCatalog,ABDetail,ABModel} from "@/services/ab";

const Chart=dynamic(()=>import("@/components/chart").then(m=>m.Chart),{ssr:false,loading:()=> <div className="chart skeleton"/>});
const states:Record<string,string>={disenado:"Diseñado",simulado:"Simulado",evaluado:"Evaluado",aceptado:"Aprendizaje guardado"};
const band=(v:[number,number]|null,decimals=2)=>v?`${porcentaje(v[0],decimals)} — ${porcentaje(v[1],decimals)}`:"n/d";

function Design({catalog,p,query,preferred}:{catalog:ABCatalog;p:CreativeEvaluation;query:string;preferred:string|null}){
  const router=useRouter(),variants=p.variantes;
  const initialControl=variants.find(v=>v.id!==preferred)?.id||variants[0].id;
  const [control,setControl]=useState(initialControl);
  const [selected,setSelected]=useState([preferred&&preferred!==initialControl?preferred:variants.find(v=>v.id!==initialControl)!.id]);
  const [busy,setBusy]=useState(false),[error,setError]=useState("");
  const errorRef=useRef<HTMLParagraphElement>(null);
  function changeControl(id:string){setControl(id);setSelected(prev=>{const next=prev.filter(v=>v!==id);return next.length?next:[variants.find(v=>v.id!==id)!.id];});}
  async function submit(e:FormEvent<HTMLFormElement>){
    e.preventDefault();setError("");
    if(!selected.length){setError("Elige al menos una propuesta distinta del control.");requestAnimationFrame(()=>errorRef.current?.focus());return;}
    const f=new FormData(e.currentTarget);setBusy(true);
    try{
      const d=await post<ABDetail>("creativos/pruebas/disenar",{...catalog.defecto,pretest_id:p.id,control,tratamientos:variants.filter(v=>selected.includes(v.id)).map(v=>v.id),
        nombre:String(f.get("nombre")),hipotesis:String(f.get("hipotesis")),impresiones_por_brazo:Number(f.get("impresiones_por_brazo")),dias:Number(f.get("dias")),
        presupuesto_por_brazo:Number(f.get("presupuesto_por_brazo")),coste_produccion:Number(f.get("coste_produccion")),semilla:Number(f.get("semilla"))});
      router.replace(`/creatividad?${query}&vista=ab&prueba=${d.id}&evaluacion=${p.id}`,{scroll:false});
    }catch(e){setError(e instanceof Error?e.message:"No se ha podido guardar el protocolo.");requestAnimationFrame(()=>errorRef.current?.focus());}
    finally{setBusy(false);}
  }
  const preview=variants.find(v=>selected.includes(v.id))||variants[0];
  return <div className="ab-design-grid"><section className="panel"><div className="panel-header"><div><h2 id="titulo-ab">Diseñar una prueba creativa</h2><p>Fija la comparación antes de observar los resultados.</p></div><FlaskConical size={18}/></div>
    <form className="ab-form" method="post" action="/api/v1/creativos/pruebas/disenar" aria-labelledby="titulo-ab" onSubmit={submit} onChange={()=>setError("")}>
      <fieldset disabled={busy} className="ab-fields-reset"><legend className="visually-hidden">Protocolo creativo</legend>
        <label htmlFor="ab-nombre">Nombre de la prueba (obligatorio)</label><input id="ab-nombre" name="nombre" required minLength={3} maxLength={100} defaultValue={catalog.defecto.nombre}/>
        <label htmlFor="ab-hipotesis">Hipótesis (obligatoria)</label><textarea id="ab-hipotesis" name="hipotesis" rows={2} required minLength={10} maxLength={350} defaultValue={catalog.defecto.hipotesis}/>
        <fieldset className="ab-options"><legend>Propuesta de control</legend>{variants.map((v,i)=><label key={v.id}><input type="radio" name="control" value={v.id} checked={control===v.id} onChange={()=>changeControl(v.id)}/><span>Propuesta {i+1} · {v.nombre}</span></label>)}</fieldset>
        <fieldset className="ab-options" aria-describedby="ab-comparaciones-ayuda"><legend>Propuestas que contrastar</legend>{variants.filter(v=>v.id!==control).map(v=><label key={v.id}><input type="checkbox" name="tratamientos" value={v.id} checked={selected.includes(v.id)} onChange={e=>setSelected(prev=>e.target.checked?[...prev,v.id]:prev.filter(id=>id!==v.id))}/><span>{v.nombre}</span></label>)}</fieldset>
        <p id="ab-comparaciones-ayuda" className="small">Elige una o las dos. Con tres brazos se corrige la multiplicidad de los contrastes frente al control.</p>
        <div className="ab-fields"><div><label htmlFor="ab-impresiones">Impresiones por brazo</label><input id="ab-impresiones" name="impresiones_por_brazo" type="number" min={500} max={200000} step={1} required defaultValue={catalog.defecto.impresiones_por_brazo}/></div><div><label htmlFor="ab-presupuesto">Presupuesto por brazo (€)</label><input id="ab-presupuesto" name="presupuesto_por_brazo" type="number" min={0} max={1000000} step="0.01" required defaultValue={catalog.defecto.presupuesto_por_brazo}/></div></div>
        <fieldset className="ab-options ab-duration"><legend>Duración simulada</legend>{[7,14,28].map(n=><label key={n}><input type="radio" name="dias" value={n} defaultChecked={n===catalog.defecto.dias}/><span>{n} días</span></label>)}</fieldset>
        <div className="ab-fields"><div><label htmlFor="ab-produccion">Producción total (€)</label><input id="ab-produccion" name="coste_produccion" type="number" min={0} max={1000000} step="0.01" required defaultValue={catalog.defecto.coste_produccion}/></div><div><label htmlFor="ab-semilla">Semilla de la prueba</label><input id="ab-semilla" name="semilla" type="number" min={0} max={2147483647} step={1} required defaultValue={catalog.defecto.semilla}/></div></div>
      </fieldset>
      <p className="small">KPI primario: CTR. Una oportunidad sintética recibe una sola propuesta. Exposición y presupuesto iguales dentro de cada fecha; sin parada anticipada.</p>
      <button type="submit" className="button primary" disabled={busy}>{busy?"Guardando protocolo…":"Guardar diseño y calcular MDE"}<ArrowRight size={15}/></button>
      <p ref={errorRef} tabIndex={-1} className="form-error" role={error?"alert":undefined}>{error}</p>
    </form></section>
    <aside className="panel ab-preview"><div className="panel-header"><div><h2>Propuesta a contrastar</h2><p>{preview.plataforma?.nombre||p.entradas.canal} · {p.entradas.audiencia}</p></div></div><CreativeArt variant={preview} priority/><div className="ab-preview-copy"><p>{p.entradas.objetivo}</p><p>Frecuencia: {numero(p.entradas.frecuencia,1)} · {p.entradas.categoria}</p><p className="checksum">{p.id}</p><Link className="text-link" href={`/creatividad?${query}&vista=pretest&evaluacion=${p.id}`}>Consultar el pretest<ArrowRight size={13}/></Link></div></aside>
  </div>;
}

function LoadDesign({catalog,id,query,preferred}:{catalog:ABCatalog;id:string;query:string;preferred:string|null}){
  const r=useRemote<CreativeEvaluation>(`creativos/evaluaciones/${id}`);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <Loading/>;
  return <Design key={r.data.id} catalog={catalog} p={r.data} query={query} preferred={preferred}/>;
}

function Report({data,query,onUpdated}:{data:ABDetail;query:string;onUpdated:()=>void}){
  const [updated,setUpdated]=useState<ABDetail|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState("");
  const headingRef=useRef<HTMLHeadingElement>(null),errorRef=useRef<HTMLParagraphElement>(null);
  const d=updated||data,p=d.protocolo,r=p.evaluacion;
  const name=(id:string)=>p.variantes.find(v=>v.id===id)?.nombre||id;
  useEffect(()=>{headingRef.current?.focus({preventScroll:true});},[d.estado]);
  async function action(step:string){
    setBusy(true);setError("");
    try{setUpdated(await post<ABDetail>(`creativos/pruebas/${d.id}/${step}`,{}));onUpdated();}
    catch(e){setError(e instanceof Error?e.message:"No se ha podido completar la acción.");requestAnimationFrame(()=>errorRef.current?.focus());}
    finally{setBusy(false);}
  }
  return <div className="ab-report"><section className="panel ab-protocol">
    <div className="panel-header wrap"><div><h2 ref={headingRef} tabIndex={-1}>{p.entradas.nombre}</h2><p>{p.entradas.hipotesis}</p></div><Badge>{states[d.estado]||d.estado}</Badge></div>
    <ol className="ab-steps" aria-label="Estado de la prueba">{Object.entries(states).map(([state,label])=><li key={state} aria-current={d.estado===state?"step":undefined}>{label}</li>)}</ol>
    <div className="ab-protocol-body"><p>{p.contexto.canal} · {p.contexto.categoria} · {p.contexto.audiencia} · frecuencia {numero(p.contexto.frecuencia,1)}</p><p>Calendario simulado: {fecha(d.inicio)} — {fecha(d.fin)}. Las observaciones se crean al ejecutar la rama; las ventas del negocio se conservan.</p>
      <div className="model-metrics"><article><small>Impresiones por brazo</small><strong>{numero(p.plan.impresiones_por_brazo)}</strong><p>{numero(p.plan.brazos)} brazos · {porcentaje(p.plan.probabilidad,1)} de asignación</p></article><article><small>MDE relativo aproximado</small><strong>{porcentaje(p.plan.mde_relativo,1)}</strong><p>CTR de partida {porcentaje(p.plan.ctr_referencia,2)} · potencia objetivo {porcentaje(p.plan.potencia_objetivo)}</p></article><article><small>Coste total de la prueba</small><strong data-testid="coste-ab">{euros(p.plan.coste_total)}</strong><p>Medios {euros(p.plan.coste_medios)} + producción {euros(p.plan.coste_produccion)}</p></article></div>
      <div className="ab-actions">{d.estado==="disenado"&&<button type="button" className="button primary" disabled={busy} onClick={()=>action("ejecutar")}>{busy?"Ejecutando…":"Ejecutar prueba sintética"}<ArrowRight size={15}/></button>}{d.estado==="simulado"&&<button type="button" className="button primary" disabled={busy} onClick={()=>action("evaluar")}>{busy?"Evaluando…":"Evaluar resultados"}<ArrowRight size={15}/></button>}{d.estado==="evaluado"&&r?.compatible&&<button type="button" className="button primary" disabled={busy} onClick={()=>action("aceptar")}>{busy?"Guardando…":"Guardar aprendizaje de CTR"}<Check size={15}/></button>}<Link className="button secondary" href={`/creatividad?${query}&vista=ab&evaluacion=${p.entradas.pretest_id}`}>Preparar otra prueba<Plus size={14}/></Link></div>
      {busy&&<p role="status">Procesando la acción y guardando su resultado…</p>}<p className="form-error" ref={errorRef} tabIndex={-1} role={error?"alert":undefined}>{error}</p>
      <details className="search-assumptions"><summary>Protocolo, costes y supuestos</summary><p>{p.plan.kpi}. {p.plan.unidad}. {p.plan.asignacion}.</p><ul className="model-notes">{p.plan.advertencias.map(a=><li key={a}>{a}</li>)}</ul><p className="checksum">{d.id} · {p.version} · semilla {d.semilla} · {d.snapshot}</p><p>Modelo previo: <span className="checksum">{p.modelo_previo||"Sin aprendizaje A/B previo en este contexto"}</span></p></details>
    </div></section>
    {r&&<section className="panel ab-evaluation"><div className="panel-header wrap"><div><h2>Resultado de la prueba</h2><p>CTR primario · CVR secundario observado entre clics</p></div><Badge tone={r.compatible?"neutral":"warning"}>{r.compatible?"Aprendizaje de CTR disponible":"Evidencia insuficiente"}</Badge></div>
      <div className="ab-protocol-body"><Notice><strong>{r.recomendacion}</strong>{r.motivos.map(m=><p key={m}>{m}</p>)}<p>Una diferencia de CTR no demuestra más pedidos ni beneficio. El multiplicador de demanda permanece en {numero(r.multiplicador_demanda,1)}.</p></Notice>
        <div className="table-wrapper" tabIndex={0} role="region" aria-label="Denominadores y tasas A/B"><table><caption className="visually-hidden">Resultados por propuesta con denominadores e intervalos Wilson</caption><thead><tr><th scope="col">Propuesta</th><th scope="col">Impresiones</th><th scope="col">Clics</th><th scope="col">CTR / IC 95 %</th><th scope="col">Conversiones</th><th scope="col">CVR / IC 95 %</th><th scope="col">Medios</th></tr></thead><tbody>{r.filas.map(f=><tr key={f.id}><th scope="row">{name(f.id)}{f.id===p.entradas.control&&<span className="ab-control-label">Control</span>}</th><td>{numero(f.impresiones)}</td><td>{numero(f.clics)}</td><td>{porcentaje(f.ctr,2)}<small>{band(f.ic95_ctr)}</small></td><td>{numero(f.conversiones)}</td><td>{porcentaje(f.cvr,2)}<small>{band(f.ic95_cvr)}</small></td><td>{euros(f.gasto)}</td></tr>)}</tbody></table></div>
        <h3>Contrastes previstos frente al control</h3><p className="small">IC familiar nominal 95 % aproximado. {p.plan.comparaciones>1?"Dos contrastes con Bonferroni; no se contrasta tratamiento contra tratamiento.":"Una comparación preespecificada."}</p>
        <Chart className="ab-interval" label="Diferencias de CTR frente al control e intervalos Newcombe-Wilson; referencia cero. Valores completos en la tabla siguiente." option={{grid:{left:100,right:28,top:28,bottom:45},tooltip:{trigger:"item",renderMode:"richText",formatter:(v:{value:number[]})=>`${numero(v.value[0]*100,3)} puntos porcentuales`},xAxis:{type:"value",name:"Diferencia de CTR (p. p.)",nameLocation:"middle",nameGap:29,axisLabel:{fontSize:10,color:"#52645C",formatter:(v:number)=>numero(v*100,2)},splitLine:{lineStyle:{color:"#EAF0ED"}}},yAxis:{type:"category",data:r.contrastes.map((_,i)=>`Contraste ${i+1}`),axisLabel:{color:"#52645C",fontSize:10}},series:r.contrastes.flatMap((c,i)=>[{type:"line",data:[[c.ic95_familiar[0],i],[c.ic95_familiar[1],i]],symbol:"rect",symbolSize:[3,16],lineStyle:{color:"#4279B0",width:3},itemStyle:{color:"#4279B0"},markLine:i===0?{symbol:"none",label:{show:false},data:[{xAxis:0}],lineStyle:{type:"dashed",color:"#82918A"}}:undefined},{type:"line",data:[[c.diferencia,i]],symbol:"circle",symbolSize:10,itemStyle:{color:"#176B57"}}])}}/>
        <div className="table-wrapper" tabIndex={0} role="region" aria-label="Contrastes de CTR"><table><caption className="visually-hidden">Diferencia e intervalo de los contrastes previstos</caption><thead><tr><th scope="col">Contraste</th><th scope="col">Propuesta</th><th scope="col">Diferencia (p. p.)</th><th scope="col">IC familiar (p. p.)</th><th scope="col">Lectura</th></tr></thead><tbody>{r.contrastes.map((c,i)=><tr key={c.variante}><th scope="row">{i+1}</th><td>{name(c.variante)}</td><td>{numero(c.diferencia*100,3)}</td><td>{numero(c.ic95_familiar[0]*100,3)} — {numero(c.ic95_familiar[1]*100,3)}</td><td>{c.lectura}</td></tr>)}</tbody></table></div>
        <p className="small">{r.metodo} CVR describe a quienes hicieron clic; no es un contraste causal sobre una audiencia fija ni se traduce a pedidos únicos.</p>
        {p.actualizacion&&<div className="ab-saved" role="status"><Check size={18}/><div><strong>Aprendizaje versionado guardado</strong><p>{p.actualizacion.metodo}</p><p className="checksum">{p.actualizacion.modelo}</p><Link className="text-link" href={`/creatividad?${query}&vista=pretest&evaluacion=${p.entradas.pretest_id}`}>Consultar el pretest y su aprendizaje<ArrowRight size={13}/></Link></div></div>}
      </div></section>}
    {d.observaciones.length>0&&<section className="panel ab-observations"><div className="panel-header wrap"><div><h2>Observaciones y asignaciones</h2><p>Una oportunidad, un brazo; presupuesto y exposición reconciliados por fecha</p></div><a className="text-link" href={`/api/v1/creativos/pruebas/${d.id}/asignaciones.csv`}>Exportar asignaciones CSV<ArrowRight size={13}/></a></div><div className="table-wrapper" tabIndex={0} role="region" aria-label="Observaciones diarias A/B"><table><caption className="visually-hidden">Conteos de cada propuesta por fecha simulada</caption><thead><tr><th scope="col">Fecha simulada</th><th scope="col">Propuesta</th><th scope="col">Impresiones</th><th scope="col">Clics</th><th scope="col">Conversiones</th></tr></thead><tbody>{d.observaciones.map(o=><tr key={`${o.fecha}:${o.brazo}`}><th scope="row">{fecha(o.fecha)}</th><td>{name(o.brazo)}</td><td>{numero(o.impresiones)}</td><td>{numero(o.clics)}</td><td>{numero(o.conversiones)}</td></tr>)}</tbody></table></div></section>}
  </div>;
}

function SavedReport({id,query,onUpdated}:{id:string;query:string;onUpdated:()=>void}){
  const r=useRemote<ABDetail>(`creativos/pruebas/${id}`);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <Loading/>;
  return <Report key={id} data={r.data} query={query} onUpdated={onUpdated}/>;
}

export function ABWorkspace({query,pretestId,trialId,preferred}:{query:string;pretestId:string|null;trialId:string|null;preferred:string|null}){
  const r=useRemote<ABCatalog>("creativos/pruebas");
  const [chosen,setChosen]=useState(pretestId||"");
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <Loading/>;
  const d=r.data,id=chosen||d.pretests[0]?.id||"";
  return <div className="ab-workspace">{trialId?<SavedReport id={trialId} query={query} onUpdated={r.retry}/>:<>
    <Notice>La prueba crea observaciones sintéticas nuevas con asignación aleatoria. Congela contexto y recursos del pretest; no activa publicidad ni altera ventas.</Notice>
    {id?<><div className="ab-source"><label htmlFor="ab-pretest">Pretest de partida</label><select id="ab-pretest" name="pretest" value={id} onChange={e=>setChosen(e.target.value)}>{!d.pretests.some(p=>p.id===id)&&<option value={id}>Pretest seleccionado</option>}{d.pretests.map(p=><option value={p.id} key={p.id}>{p.entradas.canal} · {p.entradas.categoria} · {p.entradas.objetivo}</option>)}</select></div><LoadDesign key={id} catalog={d} id={id} query={query} preferred={preferred}/></>:<div className="panel ab-empty"><h2>Prepara primero una hipótesis creativa</h2><p>Guarda un pretest con las propuestas que quieras contrastar.</p><Link className="button primary" href={`/creatividad?${query}&vista=pretest`}>Preparar pretest<ArrowRight size={14}/></Link></div>}
  </>}
    {d.filas.length>0&&<section className="panel ab-history"><div className="panel-header"><div><h2>Pruebas creativas guardadas</h2><p>Protocolos, observaciones y versiones conservados</p></div></div><div className="table-wrapper" tabIndex={0} role="region" aria-label="Historial A/B"><table><caption className="visually-hidden">Historial de pruebas A/B</caption><thead><tr><th scope="col">Prueba</th><th scope="col">Contexto</th><th scope="col">Estado</th><th scope="col">Consultar</th></tr></thead><tbody>{d.filas.map(f=><tr key={f.id}><th scope="row">{f.nombre}</th><td>{f.contexto.canal} · {f.contexto.categoria}</td><td>{states[f.estado]||f.estado}</td><td><Link className="text-link" href={`/creatividad?${query}&vista=ab&prueba=${f.id}&evaluacion=${f.pretest}`}>Abrir<ArrowRight size={13}/></Link></td></tr>)}</tbody></table></div></section>}
  </div>;
}

export function AprendizajeCreativo({pretest,query}:{pretest:CreativeEvaluation;query:string}){
  const r=useRemote<{pretest:string;modelo:ABModel|null}>(`creativos/aprendizaje/${pretest.id}`);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data?.modelo)return null;
  const m=r.data.modelo,name=(id:string)=>pretest.variantes.find((v:CreativeVariant)=>v.id===id)?.nombre||id;
  return <section className="panel ab-learning" data-testid="aprendizaje-creativo"><div className="panel-header wrap"><div><h2>Aprendizaje A/B de este contexto</h2><p>Referencia experimental separada del pretest histórico</p></div><Badge>Evidencia sintética</Badge></div><div className="ab-protocol-body"><p>Canal, audiencia, frecuencia y recursos coinciden con la prueba. Las variantes que no participaron conservan su referencia histórica.</p><div className="table-wrapper" tabIndex={0} role="region" aria-label="CTR aprendido por propuesta"><table><caption className="visually-hidden">Predicción actualizada de CTR con posterior Jeffreys</caption><thead><tr><th scope="col">Propuesta</th><th scope="col">CTR actualizado</th><th scope="col">p05–p95 de parámetros</th></tr></thead><tbody>{m.estimaciones.map(f=><tr key={f.id}><th scope="row">{name(f.id)}</th><td>{porcentaje(f.ctr_modelo,2)}</td><td>{porcentaje(f.p05,2)} — {porcentaje(f.p95,2)}</td></tr>)}</tbody></table></div><p className="small">{m.incertidumbre} El multiplicador de demanda permanece en {numero(m.multiplicador_demanda,1)}: no hay efecto económico identificado.</p><p className="checksum">{m.id} · {m.version}</p><Link className="text-link" href={`/creatividad?${query}&vista=ab&prueba=${m.experimento}&evaluacion=${m.pretest}`}>Consultar la prueba y sus contrastes<ArrowRight size={13}/></Link></div></section>;
}
