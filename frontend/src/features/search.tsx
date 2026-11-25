"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useSearchParams } from "next/navigation";
import dynamic from "next/dynamic";
import { ArrowRight, BookOpen, Search } from "lucide-react";
import { Badge, Drawer, Loading, ModuleLink, Notice } from "@/components/ui";
import { ErrorState } from "@/components/error-state";
import { useRemote } from "@/services/use-remote";
import { api, euros, fecha, numero, porcentaje, post, type Radar, type SearchEvidence, type SearchSimulation } from "@/services/api";

const Chart=dynamic(()=>import("@/components/chart").then(m=>m.Chart),{ssr:false,loading:()=> <div className="chart skeleton"/>});

export function SearchRadar({query}:{query:string}) {
  const r=useRemote<Radar>(`oportunidades?${query}`);
  return <section className="search-opportunity" data-testid="radar-marca">
    {r.error?<ErrorState message={r.error} retry={r.retry}/>:!r.data?<p>Consultando oportunidades de marca…</p>:r.data.filas.map(f=><div key={f.id}>
      <div className="card-eyebrow"><Search size={15}/> RADAR ECONÓMICO <Badge>{f.estado}</Badge></div>
      <h2>{f.titulo}</h2><p>Recorte del {numero(f.recorte_pct)} % · marca completa · {r.data!.periodo.dias} días</p>
      <div className="radar-value"><strong data-testid="impacto-radar">{euros(f.impacto)}</strong><span>Contribución incremental neta estimada</span></div>
      <p className="radar-band">p05–p95: {euros(f.banda.p05)} — {euros(f.banda.p95)}<br/>Riesgo de pérdida: {porcentaje(f.banda.probabilidad_perdida)} · Coste incremental: {euros(f.coste)}</p>
      <p>{f.recomendacion}</p><div className="opportunity-bottom"><small>Estimación experimental sintética · prioridad {f.prioridad}</small><ModuleLink href={f.url}>Explorar One Search</ModuleLink></div>
      <details className="radar-method"><summary>Cómo se prioriza</summary><p>{r.data!.criterio}</p>{f.motivos.map(m=><p key={m}>{m}</p>)}</details>
    </div>)}
  </section>;
}

type Historico={id:string;origen:string;asignaciones:{mercado:string;par:string;brazo:string}[];observaciones:{mercado:string;periodo:string;pedidos:number;gasto:number;presupuesto:number}[]};

function EvidenceDetail({data,onClose}:{data:SearchEvidence;onClose:()=>void}) {
  const [historical,setHistorical]=useState<Historico|null>(null);
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);
  const m=data.modelo;
  async function load(id:string) {
    setBusy(true);setError("");
    try{setHistorical(await api<Historico>(`busqueda/historicos/${id}`));}
    catch(e){setError(e instanceof Error?e.message:"No se ha podido consultar el histórico.");}
    finally{setBusy(false);}
  }
  return <Drawer title="Evidencia experimental de marca" onClose={onClose}>
    <Badge>{m.origen||"Históricos sintéticos de arranque"}</Badge>
    <p>{m.experimentos} experimentos, {m.pares} pares de mercados y {m.replicas} réplicas de parámetros. {m.experimento_actual?"Estimación sustituida por una prueba geográfica aceptada; las versiones anteriores se conservan.":"Son datos de arranque identificados; no son ejecuciones nuevas."}</p>
    {m.experimento_actual&&<ModuleLink secondary href={`/experimentos?experimento=${m.experimento_actual}`}>Consultar experimento aceptado</ModuleLink>}
    <h2>Qué se estima</h2><p>{m.metodo}</p><p>La tasa de recuperación SEO/directo no está identificada. El resultado estima cambio total de pedidos propios por euro ahorrado.</p>
    <h2>Intensidades observadas</h2><div className="table-wrapper" tabIndex={0} role="region" aria-label="Efectos históricos por recorte"><table><caption className="visually-hidden">Cambio de pedidos por euro ahorrado y banda empírica</caption><thead><tr><th scope="col">Recorte</th><th scope="col">Pedidos / €</th><th scope="col">p05</th><th scope="col">p95</th></tr></thead><tbody>{m.intervalos.map(i=><tr key={i.recorte}><th scope="row">{porcentaje(i.recorte)}</th><td>{numero(i.tasa,4)}</td><td>{numero(i.p05,4)}</td><td>{numero(i.p95,4)}</td></tr>)}</tbody></table></div>
    <p>{m.experimento_actual?"Placebo del preperiodo, total tratado":"Placebo sin recorte, por unidad tratada"}: {numero(m.placebo.efecto,1)} pedidos; IC 95 % {numero(m.placebo.ic95[0],1)} — {numero(m.placebo.ic95[1],1)}.</p>
    <h2>Estratos y límites</h2><ul className="model-notes">{m.estratos.map(s=><li key={s.id}>{s.id}: {s.pares} pares. {s.pooling}.</li>)}{m.advertencias.map(a=><li key={a}>{a}</li>)}</ul>
    <h2>Históricos consultables</h2><p>Pre y post de 28 días; periodos no solapados, pares congelados y asignación aleatoria dentro de par.</p>
    <div className="historical-list">{m.historicos.map(h=><button type="button" className="historical-button" key={h.id} onClick={()=>load(h.id)} disabled={busy}><span>{fecha(h.inicio_post)} — {fecha(h.fin)}</span><span>Recorte {porcentaje(h.recorte)}<ArrowRight size={13}/></span></button>)}</div>
    {busy&&<p role="status">Consultando observaciones guardadas…</p>}{error&&<p role="alert">{error}</p>}
    {historical&&<><h2>Observaciones del histórico</h2><p>{historical.origen}</p><p className="checksum">{historical.id}</p><div className="table-wrapper" tabIndex={0} role="region" aria-label="Observaciones del experimento"><table><caption className="visually-hidden">Mercados asignados y pedidos observados por periodo</caption><thead><tr><th scope="col">Mercado</th><th scope="col">Brazo / par</th><th scope="col">Periodo</th><th scope="col">Pedidos</th><th scope="col">Gasto</th></tr></thead><tbody>{historical.observaciones.map(o=>{const a=historical.asignaciones.find(a=>a.mercado===o.mercado);return <tr key={o.mercado+o.periodo}><th scope="row">{o.mercado}</th><td>{a?.brazo} / {a?.par}</td><td>{o.periodo}</td><td>{numero(o.pedidos)}</td><td>{euros(o.gasto)}</td></tr>;})}</tbody></table></div></>}
    <h2>Trazabilidad</h2><dl className="definition-list"><dt>Modelo / hipótesis</dt><dd>{m.id} / {m.hipotesis}</dd><dt>Semilla</dt><dd>{m.semilla}</dd><dt>Checksum de observaciones</dt><dd className="checksum">{m.checksum_datos}</dd></dl>
  </Drawer>;
}

function Simulator({data,query,hypothesis}:{data:SearchEvidence;query:string;hypothesis:string|null}) {
  const [cut,setCut]=useState(String(data.defecto.recorte_pct));
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const [dirty,setDirty]=useState(false);
  const [result,setResult]=useState<SearchSimulation|null>(null);
  const errorRef=useRef<HTMLParagraphElement>(null);
  const headingRef=useRef<HTMLHeadingElement>(null);
  useEffect(()=>{
    if(hypothesis===data.modelo.hipotesis&&window.location.hash==="#simulador"){
      headingRef.current?.focus({preventScroll:true});
      headingRef.current?.scrollIntoView({block:"start"});
    }
  },[hypothesis,data.modelo.hipotesis]);
  async function submit(e:FormEvent<HTMLFormElement>) {
    e.preventDefault();const form=new FormData(e.currentTarget);
    setBusy(true);setError("");
    try {
      setResult(await post<SearchSimulation>(`busqueda/simular?${query}`,{
        recorte_pct:Number(form.get("recorte_pct")),cuota_plataforma:Number(form.get("cuota_plataforma")),
        coste_experimento:Number(form.get("coste_experimento")),plataforma_comun:form.has("plataforma_comun"),
        hipotesis:hypothesis||data.modelo.hipotesis,
      }));setDirty(false);
    } catch(e) {setError(e instanceof Error?e.message:"No se ha podido calcular la evaluación.");requestAnimationFrame(()=>errorRef.current?.focus());}
    finally {setBusy(false);}
  }
  const r=result?.resultado;
  return <section className="panel search-simulator" id="simulador"><div className="panel-header wrap"><div><h2 ref={headingRef} tabIndex={-1} id="titulo-simulador">¿Qué cambia al reducir SEM marca?</h2><p>Marca completa · contrafactual del periodo · {data.periodo.dias} días</p></div><Badge>Estimación experimental sintética</Badge></div>
    <div className="search-workbench"><form aria-labelledby="titulo-simulador" action={`/api/v1/busqueda/simular?${query}`} method="post" onSubmit={submit} onChange={()=>{setDirty(true);setError("");}}>
      <fieldset><legend>Intervención y costes</legend><label htmlFor="recorte-search">Recorte de SEM marca (%)</label><p id="soporte-search">Soporte experimental: {data.soporte_pct.map(p=>`${numero(p)} %`).join(", ")}. Fuera de ese rango se calcula una hipótesis.</p>
        <input id="recorte-search" name="recorte_pct" type="number" min="0" max="100" step="1" required value={cut} onChange={e=>setCut(e.target.value)} aria-describedby="soporte-search"/>
        <label className="visually-hidden" htmlFor="recorte-slider">Ajustar recorte con deslizador</label><input id="recorte-slider" name="recorte_slider" type="range" min="0" max="100" step="5" value={cut||0} onChange={e=>setCut(e.target.value)}/>
        <label htmlFor="cuota-search">Cuota de plataforma del periodo (€)</label><input id="cuota-search" name="cuota_plataforma" type="number" min="0" max="1000000" step="0.01" required defaultValue={data.defecto.cuota_plataforma}/>
        <div className="checkbox-field"><input id="cuota-comun-search" name="plataforma_comun" type="checkbox" defaultChecked={data.defecto.plataforma_comun}/><label htmlFor="cuota-comun-search">La cuota ya se paga en ambas opciones</label></div>
        <label htmlFor="experimento-search">Coste de experimento imputado (€)</label><input id="experimento-search" name="coste_experimento" type="number" min="0" max="1000000" step="0.01" required defaultValue={data.defecto.coste_experimento}/>
      </fieldset><button type="submit" className="button primary" disabled={busy}>{busy?"Calculando y guardando…":"Calcular recorte"}<ArrowRight size={14}/></button>
      <p className="form-error" ref={errorRef} tabIndex={-1} role={error?"alert":undefined}>{error}</p>
      <p className="small">La cuota común se imputa en base y alternativa; se cancela en la comparación. No se activa publicidad.</p>
    </form><div className="search-result">
      {!r?<div className="search-result-intro"><Badge>Evidencia disponible</Badge><h3>Una hipótesis con dinero, pedidos y riesgo.</h3><p>Calcula el recorte para comparar ahorro, cambio de margen y costes sobre el mismo negocio. La evaluación quedará guardada con su versión.</p><p>La recuperación orgánica no se identifica; el cálculo utiliza el cambio experimental total de pedidos por euro.</p></div>:<>
        <p role="status" className="small">Evaluación guardada{result!.reutilizada?" · resultado reproducible reutilizado":""}.</p><div className="scenario-search-entry"><ModuleLink secondary href={`/escenarios?${query}&simulacion=${result!.id}`}>Comparar ahorro y reinversión</ModuleLink></div>
        {dirty&&<Notice>Parámetros modificados. El resultado corresponde al último cálculo; pulsa «Calcular recorte» para actualizarlo.</Notice>}
        <div className="search-result-heading"><h3>Resultado del recorte del {numero(r.entradas.recorte_pct)} %</h3><Badge tone={r.estado==="evaluado"?"neutral":"warning"}>{r.estado==="evaluado"?"Evaluado":r.estado==="bloqueado"?"Bloqueado":"Hipótesis"}</Badge></div>
        <div className="search-result-kpis"><article><small>Ahorro de medios</small><strong>{euros(r.ahorro)}</strong></article><article><small>Cambio de margen</small><strong>{euros(r.cambio_margen)}</strong></article><article><small>Costes incrementales</small><strong>{euros(r.costes_incrementales)}</strong></article><article className="search-net"><small>Contribución incremental neta</small><strong data-testid="delta-search">{euros(r.delta)}</strong></article></div>
        <p className="search-risk">Banda p05–p95: <strong>{euros(r.banda.p05)} — {euros(r.banda.p95)}</strong><br/>Probabilidad de pérdida: <strong>{porcentaje(r.banda.probabilidad_perdida)}</strong> · {r.banda.replicas} réplicas</p>
        <Notice>{r.recomendacion}{r.motivos.map(m=><p key={m}>{m}</p>)}</Notice>
        <Chart label="Desglose del cambio de contribución en euros: ahorro de medios, cambio de margen, costes y neto. Valores en la tabla de resultados." option={{grid:{left:65,right:15,top:24,bottom:64},tooltip:{trigger:"axis",renderMode:"richText",formatter:(items:{dataIndex:number}[])=>{const p=r.desglose[items[0].dataIndex];return `${p.nombre}\n${euros(p.importe)}`;}},xAxis:{type:"category",data:r.desglose.map(p=>p.nombre),axisLabel:{fontSize:10,color:"#52645C",interval:0,formatter:(v:string,i:number)=>["Ahorro","Margen","Costes","Neto"][i]||v},axisTick:{show:false}},yAxis:{type:"value",name:"EUR",axisLabel:{fontSize:10,color:"#52645C",formatter:(v:number)=>euros(v,true)},splitLine:{lineStyle:{color:"#EAF0ED"}}},series:[{type:"bar",stack:"saldo",stackStrategy:"all",data:r.desglose.map(p=>p.offset),itemStyle:{color:"transparent"},silent:true,tooltip:{show:false}},{type:"bar",stack:"saldo",stackStrategy:"all",data:r.desglose.map(p=>({value:p.altura,itemStyle:{color:p.favorable?"#23806A":"#B53C42"}})),barMaxWidth:42}]}}/>
        <div className="table-wrapper" tabIndex={0} role="region" aria-label="Comparación económica Search"><table><caption className="visually-hidden">Base y alternativa sobre el mismo periodo</caption><thead><tr><th scope="col">Magnitud</th><th scope="col">Base</th><th scope="col">Alternativa</th></tr></thead><tbody>{(["pedidos","inversion","margen","plataforma","experimento","contribucion"] as const).map(k=><tr key={k}><th scope="row">{{pedidos:"Pedidos propios",inversion:"Inversión total",margen:"Margen bruto",plataforma:"Plataforma",experimento:"Experimento",contribucion:"Contribución neta"}[k]}</th><td>{k==="pedidos"?numero(r.base[k]):euros(r.base[k])}</td><td>{k==="pedidos"?numero(r.alternativa[k]):euros(r.alternativa[k])}</td></tr>)}</tbody></table></div>
        <p className="search-break-even">Cambio estimado: {numero(r.delta_pedidos)} pedidos (p05–p95: {numero(r.banda.delta_pedidos_p05)} — {numero(r.banda.delta_pedidos_p95)}). Equilibrio: pérdida máxima asumible de {numero(r.perdida_maxima_pedidos)} pedidos. Un valor negativo exige ganar pedidos para cubrir costes.</p>
        <details className="search-assumptions"><summary>Supuestos y trazabilidad del cálculo</summary><ul className="model-notes">{r.advertencias.map(a=><li key={a}>{a}</li>)}</ul><p>Versión {r.version} · semilla {r.semilla} · {r.modelo}</p><p className="checksum">{result!.id}</p><a className="text-link" href={`/api/v1/busqueda/simulaciones/${result!.id}`} target="_blank" rel="noreferrer">Consultar evaluación guardada<ArrowRight size={13}/></a></details>
      </>}
      <div className="geo-search-link"><ModuleLink secondary href={`/experimentos?${query}&hipotesis=${data.modelo.hipotesis}`}>Diseñar experimento geográfico</ModuleLink><p>Congela la hipótesis y compara el valor de aprender antes de ejecutar.</p></div>
    </div></div>
  </section>;
}

export function SearchAnalysis({query}:{query:string}) {
  const r=useRemote<SearchEvidence>(`busqueda/evidencia?${query}`);
  const search=useSearchParams();
  const [method,setMethod]=useState(false);
  if(r.error)return <ErrorState message={r.error} retry={r.retry}/>;
  if(!r.data)return <Loading/>;
  const d=r.data;
  return <div className="search-analysis"><div className="search-evidence-heading"><div><Badge>{d.modelo.origen||"Históricos sintéticos de arranque"}</Badge><h2>Evidencia de marca, con límites explícitos.</h2><p>{d.modelo.experimentos} experimentos de la estimación vigente · {d.modelo.pares} pares · modelo {d.modelo.version}</p></div><button type="button" className="button secondary" onClick={()=>setMethod(true)}><BookOpen size={15}/>Revisar evidencia de marca</button></div>
    <Simulator data={d} query={query} hypothesis={search.get("hipotesis")}/>
    <section className="panel search-history"><div className="panel-header"><div><h2>Presencia orgánica y pagada</h2><p>Clics observados · cobertura de búsqueda de hasta 28 días</p></div><Badge>Descriptivo</Badge></div><Chart label="Clics SEO y SEM por día. Esta correlación no identifica recuperación. Datos disponibles en la tabla de clics." option={{grid:{left:60,right:18,top:42,bottom:32},legend:{top:8,data:["SEO","SEM"],textStyle:{color:"#52645C",fontSize:11}},tooltip:{trigger:"axis",valueFormatter:(v:number)=>`${numero(v)} clics`},xAxis:{type:"category",data:d.serie.map(s=>s.fecha),axisLabel:{fontSize:10,color:"#52645C",hideOverlap:true,formatter:(v:string)=>fecha(v).slice(0,5)},axisTick:{show:false}},yAxis:{type:"value",name:"Clics",axisLabel:{fontSize:10,color:"#52645C",formatter:(v:number)=>numero(v)},splitLine:{lineStyle:{color:"#EAF0ED"}}},series:[{name:"SEO",type:"line",symbol:"none",data:d.serie.map(s=>s.seo),lineStyle:{color:"#23806A"},itemStyle:{color:"#23806A"}},{name:"SEM",type:"line",symbol:"none",data:d.serie.map(s=>s.sem),lineStyle:{color:"#4279B0",type:"dashed"},itemStyle:{color:"#4279B0"}}]}}/>
      <details className="model-data"><summary>Ver datos de clics</summary><div className="table-wrapper" tabIndex={0} role="region" aria-label="Clics SEO y SEM"><table><caption className="visually-hidden">Serie descriptiva de clics; no son pedidos</caption><thead><tr><th scope="col">Fecha</th><th scope="col">Clics SEO</th><th scope="col">Clics SEM</th></tr></thead><tbody>{d.serie.map(s=><tr key={s.fecha}><th scope="row">{fecha(s.fecha)}</th><td>{numero(s.seo)}</td><td>{numero(s.sem)}</td></tr>)}</tbody></table></div></details></section>
    {method&&<EvidenceDetail data={d} onClose={()=>setMethod(false)}/>}
  </div>;
}
