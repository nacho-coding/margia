"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import dynamic from "next/dynamic";
import { ArrowRight, FlaskConical, Plus, ShieldCheck } from "lucide-react";
import { Badge, Loading, ModuleLink, Notice } from "@/components/ui";
import { ErrorState } from "@/components/error-state";
import { euros, fecha, numero, porcentaje, post } from "@/services/api";
import { useRemote } from "@/services/use-remote";
import type { GeoCatalog, GeoDetail, GeoInformation } from "@/services/geo";

const Chart=dynamic(()=>import("@/components/chart").then(m=>m.Chart),{ssr:false,loading:()=> <div className="chart skeleton"/>});
const estados:Record<string,string>={disenado:"Diseñado",simulado:"Simulado",evaluado:"Evaluado",aceptado:"Evidencia actualizada",historico:"Histórico de arranque"};

function Information({data}:{data:GeoInformation}){
  return <section className="panel geo-information" aria-labelledby="titulo-informacion"><div className="panel-header wrap"><div><h2 id="titulo-informacion">¿Cuánto vale aprender?</h2><p>Comparación con la mejor acción disponible</p></div><Badge>Estimación de información</Badge></div>
    <div className="geo-info-body"><div className="model-metrics"><article><small>Valor sin información</small><strong>{euros(data.ev_sin_informacion)}</strong><p>Mejor de mantener o recortar</p></article><article><small>EVPI · cota superior</small><strong>{euros(data.evpi)}</strong><p>Información perfecta</p></article><article><small>EVSI · este diseño</small><strong data-testid="evsi">{euros(data.evsi)}</strong><p>Información de una muestra</p></article><article><small>Valor neto de experimentar</small><strong data-testid="valor-informacion">{euros(data.valor_neto)}</strong><p>EVSI menos coste y demora</p></article></div>
      <p className="geo-costs">Coste de prueba: <strong>{euros(data.coste_experimento)}</strong> · Coste de oportunidad: <strong>{euros(data.coste_oportunidad_prueba)}</strong> · Pérdida esperada durante la prueba: {euros(data.perdida_esperada_prueba)} (incluida en la oportunidad).</p>
      <Notice><strong>{data.recomendacion}</strong>{data.motivos.map(m=><p key={m}>{m}</p>)}</Notice>
      <details className="search-assumptions"><summary>Horizonte, alternativas y supuestos de información</summary><p>{data.horizonte}.</p><p>{data.metodo}</p><ul className="model-notes">{data.advertencias.map(a=><li key={a}>{a}</li>)}</ul></details>
    </div></section>;
}

function Design({data,onDesigned}:{data:GeoCatalog;onDesigned:(d:GeoDetail)=>void}){
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const errorRef=useRef<HTMLParagraphElement>(null);
  async function submit(e:FormEvent<HTMLFormElement>){
    e.preventDefault();const form=new FormData(e.currentTarget);setError("");
    const markets=form.getAll("mercados").map(String);
    if(markets.length<8||markets.length%2){setError("Selecciona entre 8 y 24 mercados, en número par.");requestAnimationFrame(()=>errorRef.current?.focus());return;}
    setBusy(true);
    try{
      const inputs={...data.defecto, nombre:String(form.get("nombre")),objetivo:String(form.get("objetivo")),
        mercados:markets, recorte_pct:Number(form.get("recorte_pct")),dias:Number(form.get("dias")),pre_dias:Number(form.get("pre_dias")),
        coste:Number(form.get("coste")),cuota_plataforma:Number(form.get("cuota_plataforma")),limite_perdida_pct:Number(form.get("limite_perdida_pct")),semilla:Number(form.get("semilla"))};
      onDesigned(await post<GeoDetail>("experimentos/disenar",inputs));
    }catch(e){setError(e instanceof Error?e.message:"No se ha podido guardar el diseño.");requestAnimationFrame(()=>errorRef.current?.focus());}
    finally{setBusy(false);}
  }
  return <div className="geo-design-grid"><section className="panel"><div className="panel-header"><div><h2 id="titulo-diseno">Diseñar una prueba geográfica</h2><p>Protocolo congelado antes de observar el resultado</p></div><FlaskConical size={18}/></div>
    <form className="geo-form" action="/api/v1/experimentos/disenar" method="post" aria-labelledby="titulo-diseno" onSubmit={submit} onChange={()=>setError("")}>
      <label htmlFor="geo-nombre">Nombre de la prueba (obligatorio)</label><input id="geo-nombre" name="nombre" required minLength={3} maxLength={100} defaultValue={data.defecto.nombre}/>
      <label htmlFor="geo-objetivo">Hipótesis y objetivo (obligatorio)</label><textarea id="geo-objetivo" name="objetivo" required minLength={10} maxLength={500} defaultValue={data.defecto.objetivo}/>
      <div className="geo-fields"><div><label htmlFor="geo-recorte">Recorte de SEM marca (%)</label><input id="geo-recorte" name="recorte_pct" type="number" min={0} max={100} step={1} required defaultValue={data.defecto.recorte_pct}/></div><div><label htmlFor="geo-riesgo">Límite de pérdida de pedidos (%)</label><input id="geo-riesgo" name="limite_perdida_pct" type="number" min={0.1} max={20} step={.1} required defaultValue={data.defecto.limite_perdida_pct}/></div></div>
      <fieldset className="geo-radios"><legend>Duración de la prueba</legend>{[14,28,42,56].map(n=><label key={n}><input type="radio" name="dias" value={n} defaultChecked={n===data.defecto.dias}/><span>{n} días</span></label>)}</fieldset>
      <fieldset className="geo-radios"><legend>Preperiodo para emparejar</legend>{[28,56,84].map(n=><label key={n}><input type="radio" name="pre_dias" value={n} defaultChecked={n===data.defecto.pre_dias}/><span>{n} días</span></label>)}</fieldset>
      <div className="geo-fields"><div><label htmlFor="geo-coste">Coste de prueba (€)</label><input id="geo-coste" name="coste" type="number" min={0} max={1000000} step="0.01" required defaultValue={data.defecto.coste}/></div><div><label htmlFor="geo-cuota">Cuota incremental / 28 días (€)</label><input id="geo-cuota" name="cuota_plataforma" type="number" min={0} max={1000000} step="0.01" required defaultValue={data.defecto.cuota_plataforma}/></div></div>
      <label htmlFor="geo-semilla">Semilla de asignación y ejecución</label><input id="geo-semilla" name="semilla" type="number" min={0} max={2147483647} step={1} required defaultValue={data.defecto.semilla}/>
      <details className="geo-markets"><summary>Seleccionar mercados de la prueba</summary><p id="geo-mercados-ayuda">Selecciona entre 8 y 24 mercados, en número par. Una muestra parcial no sustituirá el modelo nacional.</p><fieldset aria-describedby="geo-mercados-ayuda"><legend>Mercados elegibles</legend>{data.mercados.map(m=><label key={m.id}><input type="checkbox" name="mercados" value={m.id} defaultChecked/><span>{m.nombre}</span></label>)}</fieldset></details>
      <p className="small">KPI primario: pedidos propios. Fechas posteriores al corte solo en la simulación. No hay parada anticipada ni activación de publicidad.</p>
      <button type="submit" className="button primary" disabled={busy}>{busy?"Diseñando y guardando…":"Guardar diseño y calcular valor"}<ArrowRight size={15}/></button>
      <p className="form-error" role={error?"alert":undefined} ref={errorRef} tabIndex={-1}>{error}</p>
    </form></section>
    <aside className="geo-intro"><Badge>EXPERIMENTACIÓN GEO</Badge><h2>Antes de escalar,<br/> poner a prueba.</h2><p>Reducir marca puede ahorrar inversión y perder pedidos. Diseña una comparación que permita medir ambas cosas.</p><ol><li><span>01</span><div><h3>Emparejar y aleatorizar</h3><p>Volumen, tendencia y variabilidad del preperiodo. Un tratamiento y un control por par.</p></div></li><li><span>02</span><div><h3>Valorar la información</h3><p>Comparar el aprendizaje posible con el coste de experimentar y esperar.</p></div></li><li><span>03</span><div><h3>Ejecutar, evaluar y aprender</h3><p>Nuevas observaciones sintéticas. Actualización explícita si los controles lo permiten.</p></div></li></ol><div className="geo-source"><ShieldCheck size={18}/><p>Snapshot de {fecha(data.corte)}<br/>El negocio observado se conserva.<br/><span className="checksum">{data.modelo}</span></p></div></aside>
  </div>;
}

function Run({id,query,catalog,onChange}:{id:string;query:string;catalog:GeoCatalog;onChange:(d:GeoDetail)=>void}){
  const remote=useRemote<GeoDetail>(`experimentos/${id}`);
  const [saved,setSaved]=useState<GeoDetail|null>(null);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const errorRef=useRef<HTMLParagraphElement>(null);
  const statusRef=useRef<HTMLHeadingElement>(null);
  const d=saved||remote.data;
  useEffect(()=>{if(d)statusRef.current?.focus({preventScroll:true});},[d]);
  async function action(step:string){
    setBusy(true);setError("");
    try{const result=await post<GeoDetail>(`experimentos/${id}/${step}`,{});setSaved(result);onChange(result);requestAnimationFrame(()=>statusRef.current?.focus({preventScroll:true}));}
    catch(e){setError(e instanceof Error?e.message:"No se ha podido completar la acción.");requestAnimationFrame(()=>errorRef.current?.focus());}
    finally{setBusy(false);}
  }
  if(remote.error)return <ErrorState message={remote.error} retry={remote.retry}/>;
  if(!d)return <Loading/>;
  const p=d.protocolo;const plan=p.plan;const r=p.evaluacion;
  const name=(mid:string)=>catalog.mercados.find(m=>m.id===mid)?.nombre||mid;
  return <div className="geo-run" aria-busy={busy}>
    <section className="panel geo-protocol"><div><Badge tone={d.estado==="aceptado"?"positive":"neutral"}>{estados[d.estado]||d.estado}</Badge><h2 ref={statusRef} tabIndex={-1} data-testid="estado-geo">{p.entradas?.nombre||"Histórico experimental de arranque"}</h2><p>{d.origen}</p><p>Pre: {fecha(d.inicio_pre)} — {fecha(d.fin_pre)} · Post simulado: {fecha(d.inicio_post)} — {fecha(d.fin)} · Recorte {porcentaje(d.recorte)}</p></div>
      <div className="geo-action">{d.estado==="disenado"?<button type="button" className="button primary" disabled={busy} onClick={()=>action("ejecutar")}>Ejecutar en universo sintético<ArrowRight size={15}/></button>:d.estado==="simulado"?<button type="button" className="button primary" disabled={busy} onClick={()=>action("evaluar")}>Evaluar resultado<ArrowRight size={15}/></button>:d.estado==="evaluado"&&r?.compatible?<button type="button" className="button primary" disabled={busy} onClick={()=>action("aceptar")}>Aceptar y actualizar evidencia<ArrowRight size={15}/></button>:d.estado==="aceptado"?<ModuleLink href={`/one-search?${query}&hipotesis=${p.hipotesis}#simulador`}>Volver a One Search</ModuleLink>:null}</div>
    </section><p className="form-error" role={error?"alert":undefined} ref={errorRef} tabIndex={-1}>{error}</p><p className="geo-status" role="status">{busy?"Procesando y guardando el resultado…":d.tipo==="historico_search"?"Histórico de arranque consultado; observaciones persistidas, sin ejecución nueva.":d.estado==="aceptado"?"Evidencia actualizada. Las evaluaciones anteriores conservan su versión.":d.estado==="evaluado"?"Evaluación guardada. Revisa los controles antes de actualizar.":d.estado==="simulado"?"Observaciones nuevas guardadas; pendientes de evaluación.":"Protocolo guardado. Todavía no hay observaciones posteriores al corte."}</p>
    {p.actualizacion&&<Notice>{p.actualizacion.metodo}.</Notice>}{plan&&<><div className="model-metrics geo-design-metrics"><article><small>Pares aleatorizados</small><strong>{numero(plan.pares)}</strong><p>Probabilidad {porcentaje(d.asignaciones[0]?.probabilidad)} por brazo</p></article><article><small>MDE aproximado</small><strong>{porcentaje(plan.mde_relativo)}</strong><p>{numero(plan.mde_pedidos)} pedidos · potencia objetivo {porcentaje(plan.potencia_objetivo,0)}</p></article><article><small>Ahorro tratado previsto</small><strong>{euros(plan.ahorro_tratado)}</strong><p>Solo mercados de tratamiento</p></article><article><small>Límite de pérdida</small><strong>{numero(p.entradas?.limite_perdida_pct)} %</strong><p>Preespecificado; controla actualización</p></article></div>
      <p className="geo-precheck">Placebo pre: {numero(plan.placebo.efecto)} pedidos (IC 95 % {numero(plan.placebo.ic95[0])} — {numero(plan.placebo.ic95[1])}). Máxima diferencia de tendencia entre parejas: {porcentaje(plan.max_diferencia_tendencia)}. MDE orientativo, sin garantía de potencia real.</p></>}
    {plan?.potencia_insuficiente&&<Notice>Potencia insuficiente frente al efecto de referencia: {numero(plan.efecto_previo_pedidos)} pedidos esperados según la evidencia anterior, por debajo del MDE de {numero(plan.mde_pedidos)}. El test puede no detectar ese efecto con la potencia objetivo. También se asume ausencia de spillover entre mercados.</Notice>}{p.informacion&&<Information data={p.informacion}/>}
    {r&&<section className="panel geo-evaluation" aria-labelledby="titulo-efecto"><div className="panel-header wrap"><div><h2 id="titulo-efecto">Efecto sobre los pedidos propios</h2><p>Unidad de inferencia: par de mercados · {r.numero_pares} pares</p></div><Badge tone={r.compatible?"neutral":"warning"}>{r.compatible?"Compatible para actualizar":"Abstención"}</Badge></div><div className="geo-effect"><strong data-testid="efecto-geo">{numero(r.efecto)} pedidos</strong><p>IC 95 %: {numero(r.ic95[0])} — {numero(r.ic95[1])} · Cambio relativo: {porcentaje(r.efecto_relativo)}</p><p>Efecto por euro ahorrado: {numero(r.tasa,4)} pedidos / €{r.tasa_ic95&&` · IC 95 % ${numero(r.tasa_ic95[0],4)} — ${numero(r.tasa_ic95[1],4)}`}</p></div>
      <Chart className="geo-interval" label="Intervalo del efecto total sobre pedidos tratados: el punto es la estimación y la línea su IC 95 %, con referencia cero." option={{grid:{left:65,right:25,top:15,bottom:38},tooltip:{trigger:"item",renderMode:"richText",formatter:(v:{value:number[]})=>`${numero(v.value[0])} pedidos`},xAxis:{type:"value",name:"Pedidos",nameLocation:"middle",nameGap:25,axisLabel:{color:"#52645C",fontSize:10,formatter:(v:number)=>numero(v)},splitLine:{lineStyle:{color:"#EAF0ED"}}},yAxis:{type:"value",min:-1,max:1,show:false},series:[{type:"line",data:[[r.ic95[0],0],[r.ic95[1],0]],symbol:"rect",symbolSize:[3,16],lineStyle:{width:3,color:"#4279B0"},itemStyle:{color:"#4279B0"},markLine:{symbol:"none",label:{show:false},data:[{xAxis:0}],lineStyle:{color:"#82918A",type:"dashed"}}},{type:"line",data:[[r.efecto,0]],symbol:"circle",symbolSize:11,itemStyle:{color:"#176B57"}}]}}/>
      <div className="geo-evaluation-grid"><div><Chart label="Comparación pre equivalente, post observado y contrafactual estimado de pedidos por par tratado. Valores e intervalo total en la tabla inferior." option={{grid:{left:65,right:25,top:80,bottom:50},legend:{top:8,data:["Pre equivalente","Post observado","Contrafactual estimado"],textStyle:{fontSize:10,color:"#52645C"}},tooltip:{trigger:"axis",valueFormatter:(v:number)=>`${numero(v)} pedidos`},xAxis:{type:"category",data:r.pares.map((_,i)=>String(i+1)),name:"Par",nameLocation:"middle",nameGap:28,axisLabel:{color:"#52645C"}},yAxis:{type:"value",name:"Pedidos",axisLabel:{color:"#52645C",formatter:(v:number)=>numero(v)},splitLine:{lineStyle:{color:"#EAF0ED"}}},series:[{name:"Pre equivalente",type:"bar",data:r.pares.map(v=>v.pre_tratamiento_equivalente),itemStyle:{color:"#82918A"}},{name:"Post observado",type:"bar",data:r.pares.map(v=>v.post_tratamiento),itemStyle:{color:"#23806A"}},{name:"Contrafactual estimado",type:"line",data:r.pares.map(v=>v.contrafactual_estimado),lineStyle:{color:"#4279B0",type:"dashed"},itemStyle:{color:"#4279B0"}}]}}/></div><div className="geo-guardrails"><h3>Controles para aprender</h3><Notice><strong>{r.recomendacion}</strong>{r.motivos.map(m=><p key={m}>{m}</p>)}</Notice><p>El resultado puede ser nulo o negativo. Aceptarlo sustituye la evidencia en esta intensidad; no aprueba un recorte ni activa publicidad.</p>{p.actualizacion&&<p>Modelo guardado: <span className="checksum">{p.actualizacion.modelo}</span></p>}</div></div>
      <details className="model-data"><summary>Ver resultados por par y método</summary><div className="table-wrapper" tabIndex={0} role="region" aria-label="Resultados geo por par"><table><caption className="visually-hidden">Control, tratamiento y contrafactual estimado; pedidos pre normalizados al horizonte post</caption><thead><tr><th scope="col">Par</th><th scope="col">Tratamiento / control</th><th scope="col">Pre T / C equivalente</th><th scope="col">Post T / C</th><th scope="col">Contrafactual T</th><th scope="col">Cambio pedidos</th><th scope="col">Ahorro</th></tr></thead><tbody>{r.pares.map(v=><tr key={v.par}><th scope="row">{v.par}</th><td>{name(v.tratamiento)} / {name(v.control)}</td><td>{numero(v.pre_tratamiento_equivalente)} / {numero(v.pre_control_equivalente)}</td><td>{numero(v.post_tratamiento)} / {numero(v.post_control)}</td><td>{numero(v.contrafactual_estimado)}</td><td>{numero(v.delta_pedidos)}</td><td>{euros(v.ahorro)}</td></tr>)}</tbody></table></div><p>{r.metodo}</p><ul className="model-notes">{r.advertencias.map(a=><li key={a}>{a}</li>)}</ul></details>
    </section>}
    <section className="panel geo-audit"><details open={!r}><summary>Asignaciones, observaciones y protocolo</summary><p>{plan?.metodo}</p><p>KPI: pedidos propios · Semilla {d.semilla} · {d.snapshot}</p><div className="table-wrapper" tabIndex={0} role="region" aria-label="Asignaciones y observaciones geo"><table><caption className="visually-hidden">Asignación por mercado y observaciones disponibles; un post vacío todavía no se ha ejecutado</caption><thead><tr><th scope="col">Par</th><th scope="col">Mercado</th><th scope="col">Brazo</th><th scope="col">Pre pedidos</th><th scope="col">Tendencia pre</th><th scope="col">Post pedidos</th></tr></thead><tbody>{d.asignaciones.map(a=>{const pre=d.observaciones.find(o=>o.mercado===a.mercado&&o.periodo==="pre");const post=d.observaciones.find(o=>o.mercado===a.mercado&&o.periodo==="post");const prePlan=plan?.asignaciones.find(v=>v.mercado===a.mercado);return <tr key={a.mercado}><th scope="row">{a.par}</th><td>{name(a.mercado)}</td><td>{a.brazo==="tratamiento"?"Tratamiento":"Control"}</td><td>{numero(pre?.pedidos??prePlan?.pre_pedidos)}</td><td>{porcentaje(prePlan?.tendencia)}</td><td>{numero(post?.pedidos)}</td></tr>;})}</tbody></table></div><ul className="model-notes">{p.supuestos?.map(s=><li key={s}>{s}</li>)}</ul><p className="checksum">{d.id} · modelo previo: {p.modelo_previo||"Fixture de arranque"}</p>{p.eventos?.map(e=><p key={e.estado}>{estados[e.estado]} · {new Date(e.fecha).toLocaleString("es-ES",{timeZone:"Europe/Madrid"})} · {e.motivo}</p>)}<a className="text-link" href={`/api/v1/experimentos/${d.id}`} target="_blank" rel="noreferrer">Consultar protocolo completo<ArrowRight size={14}/></a></details></section>
  </div>;
}

export function Experimentos({query}:{query:string}){
  const remote=useRemote<GeoCatalog>("experimentos");
  const [updates,setUpdates]=useState<Record<string,string>>({});
  const search=useSearchParams();const router=useRouter();
  const id=search.get("experimento");
  function select(eid:string|null){router.push(`/experimentos?${query}${eid?`&experimento=${eid}`:""}`,{scroll:false});remote.retry();}
  if(remote.error)return <ErrorState message={remote.error} retry={remote.retry}/>;
  if(!remote.data)return <Loading/>;
  const data=remote.data;
  return <div className="geo-workspace"><div className="geo-toolbar"><div><Badge>Pedidos propios · SEM marca</Badge><p>El diseño tiene sus propios mercados y calendario. Los filtros globales se conservan para volver al negocio.</p></div>{id&&<button type="button" className="button secondary" onClick={()=>select(null)}><Plus size={15}/>Nuevo diseño</button>}</div>
    {id?<Run key={id} id={id} query={query} catalog={data} onChange={d=>setUpdates(v=>({...v,[d.id]:d.estado}))}/>:<Design data={data} onDesigned={d=>select(d.id)}/>}
    <section className="panel geo-history"><div className="panel-header"><div><h2>Historial experimental</h2><p>Nuevas pruebas y fixtures de arranque, identificadas por su origen</p></div></div><div className="table-wrapper" tabIndex={0} role="region" aria-label="Historial de experimentos"><table><caption className="visually-hidden">Pruebas guardadas con estado y calendario simulado</caption><thead><tr><th scope="col">Prueba</th><th scope="col">Evidencia</th><th scope="col">Recorte</th><th scope="col">Post</th><th scope="col">Estado</th><th scope="col">Consultar</th></tr></thead><tbody>{data.filas.map(e=><tr key={e.id}><th scope="row">{e.nombre}</th><td>{e.tipo==="historico_search"?"Fixture de arranque":"Nueva prueba sintética"}</td><td>{porcentaje(e.recorte)}</td><td>{fecha(e.inicio)} — {fecha(e.fin)}</td><td><Badge>{estados[updates[e.id]||e.estado]||e.estado}</Badge></td><td><button type="button" className="text-link" aria-label={`Abrir ${e.nombre} ${e.id}`} onClick={()=>select(e.id)}>Abrir<ArrowRight size={13}/></button></td></tr>)}</tbody></table></div></section>
  </div>;
}
