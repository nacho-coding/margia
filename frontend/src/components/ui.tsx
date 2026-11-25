"use client";
import { ArrowRight, ChevronLeft, ChevronRight, Info, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useId, useRef } from "react";

export function Badge({children, tone="neutral"}:{children:React.ReactNode; tone?:string}) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
export function ModuleLink({href, children, secondary=false}:{href:string; children:React.ReactNode; secondary?:boolean}) {
  return <Link className={`button ${secondary?"secondary":"primary"}`} href={href}>{children}<ArrowRight size={15}/></Link>;
}
export function Notice({children}:{children:React.ReactNode}) {
  return <div className="notice"><Info size={16}/><div>{children}</div></div>;
}
export function Pagination({page, pages, total, onPage}:{page:number; pages:number; total:number; onPage:(v:number)=>void}) {
  return <div className="pagination"><span>{total} registros · Página {page} de {pages}</span><div>
    <button className="icon-button" disabled={page<=1} onClick={()=>onPage(page-1)} aria-label="Página anterior"><ChevronLeft size={16}/></button>
    <button className="icon-button" disabled={page>=pages} onClick={()=>onPage(page+1)} aria-label="Página siguiente"><ChevronRight size={16}/></button>
  </div></div>;
}
export function Drawer({title, children, onClose}:{title:string; children:React.ReactNode; onClose:()=>void}) {
  const dialog=useRef<HTMLDialogElement>(null);
  const titleId=useId();
  useEffect(()=>{const el=dialog.current; el?.showModal(); return ()=>el?.close();},[]);
  return <dialog ref={dialog} className="drawer" aria-labelledby={titleId} {...{closedby:"any"}} onClose={onClose}>
    <div className="drawer-header"><h1 id={titleId}>{title}</h1><button type="button" autoFocus className="icon-button" onClick={()=>dialog.current?.close()} aria-label="Cerrar detalle"><X size={20}/></button></div>
    <div className="drawer-body">{children}</div>
  </dialog>;
}
export function Loading() {return <div className="loading" aria-busy="true"><div className="skeleton loading-title"/><div className="loading-grid">{[1,2,3,4,5].map(i=><div className="skeleton" key={i}/>)}</div><div className="skeleton loading-chart"/><span>Consultando el mundo sintético…</span><progress aria-label="Cargando datos"/></div>;}
