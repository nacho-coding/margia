"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { Activity, ArrowDownToLine, ArrowUpRight, BookOpen, ChartNoAxesCombined, Check, ChevronDown, ChevronsLeft, Database, FlaskConical, LayoutDashboard, Menu, PanelLeftOpen, Search, Settings2, ShieldCheck, Sparkles, X } from "lucide-react";
import { Contexto, fecha } from "@/services/api";
import { useRemote } from "@/services/use-remote";
import { ErrorState } from "@/components/error-state";
import { NavigationDrawer } from "@/components/navigation-drawer";
import { Badge, Drawer, Loading } from "@/components/ui";
import { Centro, OneSearch, FiabilidadView, Ajustes } from "@/features/views";
import { Creatividad } from "@/features/creatividad";
import { Medicion } from "@/features/medicion";
import { Experimentos } from "@/features/experimentos";
import { Escenarios } from "@/features/escenarios";

const groups = [
  {label:"DECIDIR",items:[{path:"/",label:"Centro de decisiones",icon:LayoutDashboard},{path:"/escenarios",label:"Escenarios",icon:ChartNoAxesCombined}]},
  {label:"COMPRENDER",items:[{path:"/medicion",label:"Medición de medios",icon:Activity},{path:"/one-search",label:"One Search",icon:Search},{path:"/creatividad",label:"Inteligencia creativa",icon:Sparkles}]},
  {label:"EXPERIMENTAR",items:[{path:"/experimentos",label:"Laboratorio",icon:FlaskConical}]},
  {label:"GOBERNAR",items:[{path:"/fiabilidad",label:"Fiabilidad del dato",icon:ShieldCheck},{path:"/ajustes",label:"Configuración",icon:Settings2}]},
];
const descriptions:Record<string,{title:string;subtitle:string;eyebrow:string}> = {
  "/":{title:"Centro de decisiones",subtitle:"Una visión compartida del negocio. La evidencia, antes de actuar.",eyebrow:"PERSPECTIVA ECONÓMICA"},
  "/medicion":{title:"Medición de medios",subtitle:"Pedidos propios, respuesta estimada y atribución. Cada lectura con sus límites.",eyebrow:"COMPRENDER EL RENDIMIENTO"},
  "/one-search":{title:"Una búsqueda. Una visión.",subtitle:"SEO y SEM en el mismo contexto comercial, sin duplicar inversión.",eyebrow:"ONE SEARCH"},
  "/creatividad":{title:"La creatividad, con contexto",subtitle:"Histórico, contexto y propuestas. Cada estimación, con su alcance.",eyebrow:"INTELIGENCIA CREATIVA"},
  "/experimentos":{title:"Laboratorio de experimentos",subtitle:"La siguiente decisión empieza por una hipótesis contrastable.",eyebrow:"APRENDER ANTES DE ESCALAR"},
  "/escenarios":{title:"Laboratorio de escenarios",subtitle:"Comparar el valor económico de mantener, ahorrar y reinvertir.",eyebrow:"DECIDIR CON PERSPECTIVA"},
  "/fiabilidad":{title:"La confianza se comprueba",subtitle:"Cobertura, integridad y límites del universo sintético.",eyebrow:"FIABILIDAD DEL DATO"},
  "/ajustes":{title:"Configuración de la demo",subtitle:"Un mundo reproducible, con estado persistente y un restablecimiento explícito.",eyebrow:"CONTEXTO Y TRAZABILIDAD"},
};

export function Workspace() {
  const path=usePathname();
  const search=useSearchParams();
  const router=useRouter();
  const [collapsed,setCollapsed]=useState(false);
  const [mobileOpen,setMobileOpen]=useState(false);
  const [method,setMethod]=useState(false);
  const resource=useRemote<Contexto>("contexto");
  const ctx=resource.data;
  const days=[28,56,90,365].includes(Number(search.get("dias")))?Number(search.get("dias")):28;
  const market=search.get("mercado")||"";
  const query=new URLSearchParams({dias:String(days),...(market?{mercado:market}:{})}).toString();
  const item=groups.flatMap(g=>g.items).find(i=>i.path===path);
  const description=descriptions[path]||{title:"Página no encontrada",subtitle:"Vuelve al centro de decisiones para continuar.",eyebrow:"MARGIA"};
  const href=(route:string)=>`${route}?${query}`;
  const filter=(name:string,value:string)=>{
    const next=new URLSearchParams(query); if(value) next.set(name,value); else next.delete(name);
    if(path==="/one-search"&&search.get("hipotesis"))next.set("hipotesis",search.get("hipotesis")!);
    if(path==="/experimentos"&&search.get("experimento"))next.set("experimento",search.get("experimento")!);
    if(path==="/creatividad")for(const key of ["vista","evaluacion","seleccion","prueba","variante"])if(search.get(key))next.set(key,search.get(key)!);
    if(path==="/escenarios")for(const key of ["ejecucion","seleccion","simulacion","canal"])if(search.get(key))next.set(key,search.get(key)!);
    router.replace(`${path}?${next.toString()}`,{scroll:false});
  };
  return <div className={`workspace ${collapsed?"collapsed":""} ${mobileOpen?"mobile-open":""}`}>
    <a className="skip-link" href="#contenido">Saltar al contenido</a>
    {mobileOpen&&<NavigationDrawer onClose={()=>setMobileOpen(false)}>{groups.map(group=><div className="nav-group" key={group.label}><p>{group.label}</p>{group.items.map(link=><Link className={`nav-item ${link.path===path?"active":""}`} href={href(link.path)} aria-label={link.label} key={link.path} onClick={()=>setMobileOpen(false)} aria-current={link.path===path?"page":undefined}><link.icon size={18}/><span>{link.label}</span></Link>)}</div>)}</NavigationDrawer>}
    <aside className="sidebar" aria-label="Navegación principal">
      <Link className="brand" href={href("/")} aria-label="MARGIA · Inicio"><svg viewBox="0 0 36 38" aria-hidden="true"><path d="M3 32V5l15 15L33 5v27M3 5l15 27L33 5"/></svg><span>MARGIA<small>DECISION INTELLIGENCE</small></span></Link>
      <div className="workspace-label"><span className="aurel-avatar">A</span><div>AUREL Retail<small>Espacio de demostración</small></div><ChevronDown size={13} aria-hidden="true"/></div>
      <nav>{groups.map(group=><div className="nav-group" key={group.label}><p>{group.label}</p>{group.items.map(link=><Link title={collapsed?link.label:undefined} className={`nav-item ${link.path===path?"active":""}`} href={href(link.path)} aria-label={link.label} key={link.path} onClick={()=>setMobileOpen(false)} aria-current={link.path===path?"page":undefined}><link.icon size={18}/><span>{link.label}</span>{link.path===path&&<i/>}</Link>)}</div>)}</nav>
      <div className="sidebar-bottom"><div className="local-status"><span/><div>Entorno local<small>Datos 100 % sintéticos</small></div><ShieldCheck size={17}/></div><button className="collapse-control" onClick={()=>setCollapsed(!collapsed)} aria-label={collapsed?"Expandir navegación":"Contraer navegación"}>{collapsed?<PanelLeftOpen size={17}/>:<ChevronsLeft size={17}/>}<span>Contraer navegación</span></button></div>
    </aside>
    <div className="main-shell">
      <header className="topbar"><div className="breadcrumb"><button type="button" className="icon-button mobile-toggle" onClick={()=>setMobileOpen(true)} aria-label="Abrir navegación" aria-expanded={mobileOpen}><Menu size={20}/></button><span>Espacio de trabajo</span><span className="slash">/</span><strong>{item?.label||"MARGIA"}</strong></div><div className="topbar-right"><span className="synthetic"><span/>Datos sintéticos</span><button className="icon-button" title="Metodología y alcance" aria-label="Abrir metodología y alcance" onClick={()=>setMethod(true)}><BookOpen size={18}/></button><span className="topbar-divider"/><div className="profile"><span>AR</span><div>Vista de dirección<small>AUREL Retail</small></div></div></div></header>
      <main id="contenido" tabIndex={-1}>
        <div className="page-heading"><div><p className="eyebrow">{description.eyebrow}</p><h1>{description.title}</h1><p className="subtitle">{description.subtitle}</p></div>{path==="/"&&<a className="button secondary export-button" href={`/api/v1/exportar/negocio.csv?${query}`}><ArrowDownToLine size={16}/>Exportar negocio</a>}</div>
        <section className="filterbar" aria-label="Filtros globales"><div className="filters"><label htmlFor="periodo-global"><span>Periodo</span><select id="periodo-global" name="dias" aria-label="Periodo global" value={days} onChange={e=>filter("dias",e.target.value)}>{[28,56,90,365].map(n=><option value={n} key={n}>Últimos {n} días</option>)}</select></label><label htmlFor="mercado-global"><span>Mercado</span><select id="mercado-global" name="mercado" aria-label="Mercado global" value={market} onChange={e=>filter("mercado",e.target.value)}><option value="">Todos los mercados</option>{ctx?.mercados.map(m=><option key={m.id} value={m.id}>{m.nombre}</option>)}</select></label>{(days!==28||market)&&<button className="filter-reset" onClick={()=>router.replace(path,{scroll:false})}><X size={13}/>Restablecer filtros</button>}</div><div className="snapshot-label"><Database size={13}/><span>Corte {ctx?fecha(ctx.corte):"…"}</span><Badge>Snapshot fijo</Badge></div></section>
        {resource.error?<ErrorState message={resource.error} retry={resource.retry}/>:!ctx?<Loading/>:<>
          {path==="/"?<Centro query={query} ctx={ctx}/>:path==="/medicion"?<Medicion query={query}/>:path==="/one-search"?<OneSearch key={query} query={query}/>:path==="/creatividad"?<Creatividad key={query} query={query}/>:path==="/fiabilidad"?<FiabilidadView ctx={ctx}/>:path==="/ajustes"?<Ajustes ctx={ctx}/>:path==="/experimentos"?<Experimentos query={query}/>:path==="/escenarios"?<Escenarios query={query}/>:<div className="error-state"><h2>Esta ruta no existe</h2><Link className="button primary" href={href("/")}>Volver al centro</Link></div>}
        </>}
        <footer className="page-footer"><span><span className="footer-mark">M</span>MARGIA <span className="muted">/</span> Cada decisión tiene un valor.</span><span>Demo sintética · {ctx?.version||"Inicializando"} <Check size={12}/></span></footer>
      </main>
    </div>
    {method&&<Drawer title="Metodología y alcance" onClose={()=>setMethod(false)}><Badge>Demo con datos sintéticos</Badge><h3>Una sola verdad económica</h3><p>Los pedidos y las ventas se generan una sola vez en el negocio propio. Las conversiones atribuidas por plataforma pueden solaparse y se presentan por separado.</p><h3>Qué se puede comprobar ahora</h3><p>Inversión, margen, contribución tras marketing, cobertura y reconciliación. El MMM nacional, One Search y el laboratorio geográfico muestran estimaciones, incertidumbre y límites. El pretest creativo y las pruebas A/B conservan hipótesis y aprendizaje de CTR. Escenarios compara base, ahorro y reinversión con costes e incertidumbre; la búsqueda respeta los bloqueos de evidencia.</p><h3>Cómo leer la contribución</h3><p>Margen bruto menos inversión en medios, incluido CRM. Antes de costes de plataforma, producción creativa y experimentación. El comparador de escenarios imputa esos costes explícitamente.</p><h3>Trazabilidad</h3><dl className="definition-list"><dt>Fecha de corte</dt><dd>{ctx&&fecha(ctx.corte)}</dd><dt>Semilla raíz</dt><dd>{ctx?.semilla}</dd><dt>Generador</dt><dd>{ctx?.version}</dd></dl><p className="small muted">El corte es independiente del reloj. Aprobar una decisión en esta POC nunca activará publicidad.</p><a className="text-link" href="/api/openapi.json" target="_blank" rel="noreferrer">Consultar contrato de API<ArrowUpRight size={14}/></a></Drawer>}
  </div>;
}
