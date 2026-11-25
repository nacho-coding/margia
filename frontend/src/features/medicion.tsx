"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { BookOpen, ShieldAlert } from "lucide-react";
import { Badge, Drawer, Loading, ModuleLink, Notice } from "@/components/ui";
import { ErrorState } from "@/components/error-state";
import { useRemote } from "@/services/use-remote";
import { Canal, FichaModelo, MedicionModelo, Tabla, euros, fecha, numero, porcentaje } from "@/services/api";

const Chart = dynamic(() => import("@/components/chart").then(m => m.Chart), {
  ssr:false, loading:() => <div className="chart skeleton"/>,
});

function Metodologia({modelo,onClose}:{modelo:FichaModelo;onClose:()=>void}) {
  const d = modelo.diagnostico;
  return <Drawer title="Cómo se ha ajustado el MMM" onClose={onClose}>
    <Badge>Estimación observacional sintética</Badge>
    <p>Regresión regularizada con contribuciones de medios no negativas, adstock semanal y saturación Hill de pendiente fija. Controles de calendario, tendencia y promoción; sin demanda de marca como control.</p>
    <h2>Separación temporal</h2>
    <dl className="definition-list"><dt>Entrenamiento</dt><dd>{fecha(modelo.train_inicio)} — {fecha(modelo.train_fin)}</dd><dt>Evaluación final reservada</dt><dd>{fecha(modelo.holdout_inicio)} — {fecha(modelo.holdout_fin)}</dd><dt>Selección</dt><dd>Grid reducido con dos ventanas de validación anteriores a la evaluación final. Escalas aprendidas en cada entrenamiento.</dd></dl>
    <ul className="model-notes">{modelo.folds.map(f=><li key={f.train_fin}>Ajuste hasta {fecha(f.train_fin)}; validación {fecha(f.validacion_inicio)} — {fecha(f.validacion_fin)}.</li>)}</ul>
    <h2>Incertidumbre y soporte</h2><p>{modelo.incertidumbre}</p><p>Las curvas muestran un horizonte de siete días con el stock anterior a la última semana fijo. La zona sombreada indica inversión observada en entrenamiento. Los trazos discontinuos son extrapolación hipotética.</p>
    <h2>Diagnóstico y límites</h2>
    <dl className="definition-list"><dt>Autocorrelación residual · retardo 1</dt><dd>{numero(d.autocorrelacion_lag1,2)}</dd><dt>Correlación máxima entre medios</dt><dd>{numero(d.correlacion_maxima,2)} · bloqueo desde {numero(d.umbrales.max_correlacion,2)}</dd><dt>Condición de la matriz normalizada</dt><dd>{numero(d.condicion,1)} · máximo {numero(d.umbrales.max_condicion)}</dd><dt>Variación mínima de inversión</dt><dd>{porcentaje(d.variacion_minima)} · mínimo {porcentaje(d.umbrales.min_variacion)}</dd><dt>Sensibilidad del reparto</dt><dd>{numero(d.sensibilidad,2)} · máximo {numero(d.umbrales.max_sensibilidad,2)}</dd></dl>
    <p>La sensibilidad compara la masa asignada por canal entre configuraciones que quedan a un 10 % del mejor error de validación. La buena predicción conjunta no garantiza un reparto estable.</p>
    <ul className="model-notes">{modelo.advertencias.map(a=><li key={a}>{a}</li>)}</ul>
    <h2>Artefacto guardado</h2><dl className="definition-list"><dt>Versión / identificador</dt><dd>{modelo.version} / {modelo.id}</dd><dt>Snapshot</dt><dd>{modelo.snapshot}</dd><dt>Semilla</dt><dd>{modelo.semilla}</dd><dt>Tiempo de ajuste batch</dt><dd>{numero(modelo.segundos_ajuste,3)} s</dd><dt>Checksum de observaciones semanales</dt><dd className="checksum">{modelo.checksum_datos}</dd></dl>
  </Drawer>;
}

function ModeloNacional({data,query}:{data:MedicionModelo;query:string}) {
  const [channel,setChannel] = useState("meta");
  const [view,setView] = useState<"ajuste"|"descomposicion">("ajuste");
  const [method,setMethod] = useState(false);
  const {modelo,serie} = data;
  const curve = data.curvas.find(c=>c.id===channel) || data.curvas[0];
  const d = modelo.diagnostico;
  if(!data.aplicable) return <Notice>{data.motivo}</Notice>;
  const common = {
    grid:{top:48,left:62,right:18,bottom:40},
    legend:{top:10,textStyle:{fontSize:10,color:"#52645C"},itemWidth:14,itemHeight:8},
    tooltip:{trigger:"axis",valueFormatter:(v:number)=>`${numero(v)} pedidos`},
    xAxis:{type:"category",data:serie.map(s=>s.fin),axisLabel:{color:"#52645C",fontSize:10,hideOverlap:true,formatter:(v:string)=>fecha(v).slice(0,5)},axisTick:{show:false},axisLine:{lineStyle:{color:"#D5DED9"}}},
    yAxis:{type:"value",name:"Pedidos / semana",nameTextStyle:{color:"#52645C",fontSize:10},axisLabel:{color:"#52645C",fontSize:10,formatter:(v:number)=>numero(v)},splitLine:{lineStyle:{color:"#EAF0ED",type:"dashed"}}},
  };
  const option = view==="ajuste" ? {...common,legend:{...common.legend,data:["Observado","MMM","Naive anual"]},series:[
    {type:"line",name:"Límite inferior",data:serie.map(s=>s.p05),stack:"banda",symbol:"none",lineStyle:{opacity:0},areaStyle:{opacity:0},silent:true,tooltip:{show:false}},
    {type:"line",name:"Banda predictiva",data:serie.map(s=>s.ancho_banda),stack:"banda",symbol:"none",lineStyle:{opacity:0},areaStyle:{color:"#23806A",opacity:.12},silent:true,tooltip:{show:false}},
    {type:"line",name:"MMM",data:serie.map(s=>s.predicho),symbol:"none",lineStyle:{width:2,color:"#23806A"},itemStyle:{color:"#23806A"}},
    {type:"line",name:"Naive anual",data:serie.map(s=>s.naive),symbol:"none",lineStyle:{width:1.5,type:"dashed",color:"#8267A7"},itemStyle:{color:"#8267A7"}},
    {type:"line",name:"Observado",data:serie.map(s=>s.observado),symbol:"circle",symbolSize:5,lineStyle:{width:1.5,color:"#172722"},itemStyle:{color:"#172722"}},
  ]} : {...common,series:[
    {type:"bar",name:"Baseline",stack:"prediccion",data:serie.map(s=>s.baseline),itemStyle:{color:"#82918A"},barMaxWidth:30},
    {type:"bar",name:"Efectos modelados",stack:"prediccion",data:serie.map(s=>s.efectos),itemStyle:{color:"#23806A"},barMaxWidth:30},
    {type:"line",name:"Observado",data:serie.map(s=>s.observado),lineStyle:{color:"#172722",width:1.5},itemStyle:{color:"#172722"},symbolSize:4},
  ]};
  return <div className="model-workspace" data-testid="modelo-nacional">
    <div className="model-heading"><div><p className="eyebrow">MODELO DE RESPUESTA · {modelo.ambito}</p><h2>Predecir no basta para reasignar.</h2><p>{modelo.semanas} semanas · pedidos propios · {modelo.version}</p></div><button className="button secondary" type="button" onClick={()=>setMethod(true)}><BookOpen size={15}/>Metodología del MMM</button></div>
    <div className="model-status" data-testid="estado-mmm"><ShieldAlert size={19}/><div><strong>{modelo.estado==="bloqueado"?"Recomendaciones bloqueadas":"Uso limitado a lectura del modelo"}</strong><p>{modelo.motivos.length?modelo.motivos.join(" "):"Modelo observacional; necesita calibración antes de optimizar inversión."} Puedes consultar el ajuste y sus límites.</p></div><Badge tone={modelo.estado==="bloqueado"?"danger":"warning"}>{modelo.estado==="bloqueado"?"Bloqueado":"Limitado"}</Badge></div>
    <div className="model-metrics"><article><small>Error MMM · evaluación final</small><strong data-testid="wape-mmm">{porcentaje(d.holdout.wape,2)}</strong><p>WAPE · MAE {numero(d.holdout.mae)} pedidos</p></article><article><small>Error de referencia estacional</small><strong>{porcentaje(d.naive.wape,2)}</strong><p>Misma semana del año anterior</p></article><article><small>Sesgo MMM · evaluación final</small><strong>{porcentaje(d.holdout.sesgo,2)}</strong><p>Predicción menos observado</p></article><article><small>Cobertura de banda p05–p95</small><strong>{porcentaje(d.cobertura_banda_holdout)}</strong><p>De las {modelo.configuracion.holdout} semanas reservadas</p></article></div>
    <p className="period-caption model-period">Entrenamiento hasta {fecha(modelo.train_fin)} · Evaluación reservada {fecha(modelo.holdout_inicio)} — {fecha(modelo.holdout_fin)}. Estos diagnósticos no cambian con el periodo visualizado.</p>
    <div className="model-grid"><section className="panel"><div className="panel-header wrap"><div><h2>Pedidos: observado y modelado</h2><p>{data.serie.length} semanas completas del periodo · ámbito nacional</p></div><div className="segmented" aria-label="Vista del modelo"><button type="button" aria-pressed={view==="ajuste"} onClick={()=>setView("ajuste")}>Ajuste</button><button type="button" aria-pressed={view==="descomposicion"} onClick={()=>setView("descomposicion")}>Descomposición</button></div></div>
      <Chart option={option} label={view==="ajuste"?"Pedidos semanales observados, predicción MMM y referencia estacional, con banda predictiva p05 a p95. Datos en la tabla de semanas.":"Baseline y efectos modelados suman la predicción. La diferencia con el observado es el residual, disponible en la tabla de semanas."}/>
      <div className="panel-bottom-note">{view==="ajuste"?"Banda predictiva empírica p05–p95, condicional al modelo. No es un intervalo causal.":"Baseline + efectos = predicción. Predicción + residual = observado; el residual no se reparte entre canales."}</div>
      <details className="model-data"><summary>Ver datos de las semanas</summary><div className="table-wrapper" role="region" aria-label="Semanas del modelo" tabIndex={0}><table><caption className="visually-hidden">Pedidos por semana, descomposición y banda predictiva p05–p95</caption><thead><tr>{["Semana hasta","Muestra","Observado","Predicción","Baseline","Efectos","Residual","p05","p95","Naive anual"].map(h=><th scope="col" key={h}>{h}</th>)}</tr></thead><tbody>{serie.map(s=><tr key={s.fin}><th scope="row">{fecha(s.fin)}</th><td>{s.particion==="train"?"Entrenamiento":"Evaluación"}</td><td>{numero(s.observado)}</td><td>{numero(s.predicho)}</td><td>{numero(s.baseline)}</td><td>{numero(s.efectos)}</td><td>{numero(s.residual)}</td><td>{numero(s.p05)}</td><td>{numero(s.p95)}</td><td>{numero(s.naive)}</td></tr>)}</tbody></table></div></details>
    </section>
    {curve&&<section className="panel"><div className="panel-header wrap"><div><h2>Respuesta y saturación</h2><p>Término modelado · {curve.horizonte_dias} días</p></div><div className="curve-selector"><label htmlFor="canal-mmm">Canal del modelo</label><select id="canal-mmm" value={channel} onChange={e=>setChannel(e.target.value)}>{data.curvas.map(c=><option key={c.id} value={c.id}>{c.nombre}</option>)}</select></div></div>
      <Chart label={`Curva semanal de ${curve.nombre}: pedidos modelados por inversión en euros. Zona sombreada: soporte observado. Datos y retorno marginal en la tabla de curva.`} option={{
        grid:{top:40,right:22,left:62,bottom:46},tooltip:{trigger:"axis",valueFormatter:(v:number|number[])=>`${numero(Array.isArray(v)?v[1]:v,1)} pedidos`},
        xAxis:{type:"value",name:"Inversión EUR / semana",nameLocation:"middle",nameGap:31,nameTextStyle:{color:"#52645C",fontSize:10},axisLabel:{fontSize:10,color:"#52645C",hideOverlap:true,showMaxLabel:false,formatter:(v:number)=>euros(v,true)},splitLine:{show:false}},
        yAxis:{type:"value",name:"Pedidos modelados",nameTextStyle:{color:"#52645C",fontSize:10},axisLabel:{fontSize:10,color:"#52645C",formatter:(v:number)=>numero(v)},splitLine:{lineStyle:{color:"#EAF0ED",type:"dashed"}}},
        series:[
          {type:"line",data:curve.puntos.map(p=>[p.inversion,p.p05]),stack:"banda",symbol:"none",silent:true,lineStyle:{opacity:0},tooltip:{show:false}},
          {type:"line",data:curve.puntos.map(p=>[p.inversion,p.ancho_banda]),stack:"banda",symbol:"none",silent:true,lineStyle:{opacity:0},areaStyle:{color:curve.color,opacity:.12},tooltip:{show:false}},
          {type:"line",name:"Forma hipotética",data:curve.puntos.map(p=>[p.inversion,p.pedidos]),symbol:"none",lineStyle:{color:curve.color,type:"dashed",width:2},markArea:{silent:true,itemStyle:{color:"#82918A",opacity:.12},data:[[{xAxis:curve.minimo},{xAxis:curve.maximo}]]},markLine:{silent:true,symbol:"none",label:{show:false},lineStyle:{color:"#52645C",type:"dotted"},data:[{xAxis:curve.referencia}]}},
          {type:"line",name:curve.nombre,data:curve.puntos.map(p=>[p.inversion,p.extrapolado?null:p.pedidos]),symbol:"none",lineStyle:{color:curve.color,width:2.5}},
        ],
      }}/>
      <div className="panel-bottom-note">Soporte observado: {euros(curve.minimo)} — {euros(curve.maximo)} / semana. Línea vertical: gasto de la semana hasta {fecha(modelo.holdout_fin)}. Stock previo fijo.</div>
      <div className="scenario-measurement-entry"><ModuleLink secondary href={`/escenarios?${query}&canal=${curve.id}`}>Comparar este canal en escenarios</ModuleLink></div>
      <details className="model-data"><summary>Ver datos de la curva y marginal</summary><div className="table-wrapper" role="region" aria-label="Datos de la curva" tabIndex={0}><table><caption className="visually-hidden">Curva de {curve.nombre}; banda de coeficientes y derivada marginal por euro, sin identificación causal</caption><thead><tr>{["Inversión semanal","Pedidos modelados","p05","p95","Pedidos / € adicional","Soporte"].map(h=><th scope="col" key={h}>{h}</th>)}</tr></thead><tbody>{curve.puntos.map(p=><tr key={p.inversion}><th scope="row">{euros(p.inversion)}</th><td>{numero(p.pedidos)}</td><td>{numero(p.p05)}</td><td>{numero(p.p95)}</td><td>{numero(p.marginal,4)}</td><td>{p.extrapolado?"Extrapolación":"Observado en train"}</td></tr>)}</tbody></table></div></details>
    </section>}</div>
    <section className="panel model-assignment"><div className="panel-header"><div><h2>Asignación del modelo por canal</h2><p>Semanas completas seleccionadas · estimaciones condicionadas al modelo</p></div><Badge>Sin interpretación causal</Badge></div><div className="table-wrapper" role="region" aria-label="Asignación del modelo" tabIndex={0}><table><caption className="visually-hidden">Pedidos y margen asignados por el MMM. Saldo del término modelado menos inversión. No constituye contribución incremental.</caption><thead><tr>{["Canal","Pedidos asignados","Banda p05–p95","Margen asignado","Inversión","Saldo modelado","Saldo p05–p95"].map(h=><th scope="col" key={h}>{h}</th>)}</tr></thead><tbody>{data.resumen.map(r=><tr key={r.id}><th scope="row"><span className="channel-name"><i style={{background:r.color}}/>{r.nombre}</span></th><td>{numero(r.pedidos_modelados)}</td><td>{numero(r.pedidos_p05)} — {numero(r.pedidos_p95)}</td><td>{euros(r.margen_asignado)}</td><td>{euros(r.inversion)}</td><td>{euros(r.saldo_modelado)}</td><td>{euros(r.saldo_p05)} — {euros(r.saldo_p95)}</td></tr>)}</tbody></table></div><div className="panel-bottom-note">Margen asignado = término de pedidos × margen observado por pedido de cada semana. Saldo = margen asignado − inversión del canal. Bandas de coeficientes con forma fija; no representan beneficio incremental identificado ni permiten priorizar inversiones.</div></section>
    <Notice>SEM marca captura demanda y queda fuera del MMM. Su inversión y atribución se mantienen en la tabla de plataformas. La recuperación orgánica y las decisiones de recorte requieren evidencia de One Search.</Notice>
    {method&&<Metodologia modelo={modelo} onClose={()=>setMethod(false)}/>}
  </div>;
}

export function Medicion({query}:{query:string}) {
  const model = useRemote<MedicionModelo>(`modelos/mmm?${query}`);
  const platforms = useRemote<Tabla<Canal>>(`medios?${query}`);
  return <>
    {model.error?<ErrorState message={model.error} retry={model.retry}/>:model.data?<ModeloNacional data={model.data} query={query}/>:<Loading/>}
    {platforms.error?<ErrorState message={platforms.error} retry={platforms.retry}/>:platforms.data?<section className="panel"><div className="panel-header"><div><h2>Lectura de las plataformas</h2><p>{platforms.data.cobertura} · filtro de mercado aplicado</p></div><Badge>Atribución descriptiva</Badge></div><div className="table-wrapper" role="region" aria-label="Tabla de medios" tabIndex={0}><table><caption className="visually-hidden">Inversión y atribución por canal. Las conversiones entre canales no se suman.</caption><thead><tr>{["Canal","Inversión","Impresiones","Clics","Conv. atribuidas","ROAS atribuido","Incrementalidad"].map(h=><th scope="col" key={h}>{h}</th>)}</tr></thead><tbody>{platforms.data.filas.map(c=><tr key={c.id}><th scope="row"><span className="channel-name"><i style={{background:c.color}}/>{c.nombre}</span><small>{c.tipo==="captura"?"Captura de demanda":"Generación de demanda"}</small></th><td>{euros(c.inversion)}</td><td>{numero(c.impresiones)}</td><td>{numero(c.clics)}</td><td>{numero(c.conversiones)}</td><td>{c.roas_atribuido==null?"n/d":`${numero(c.roas_atribuido,2)}×`}</td><td><Badge>No identificada</Badge></td></tr>)}</tbody></table></div><div className="panel-bottom-note">Ordenado por inversión descendente · Conversiones solapadas entre plataformas · ROAS atribuido no equivale a beneficio.</div></section>:null}
    <div className="model-next"><ModuleLink secondary href={`/one-search?${query}`}>Explorar One Search</ModuleLink></div>
  </>;
}
