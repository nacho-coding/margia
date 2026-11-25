"use client";
import { useEffect, useRef } from "react";
import { X } from "lucide-react";

export function NavigationDrawer({children,onClose}:{children:React.ReactNode;onClose:()=>void}) {
  const dialog=useRef<HTMLDialogElement>(null);
  const scroller=useRef<HTMLDivElement>(null);
  const sheet=useRef<HTMLDivElement>(null);
  useEffect(()=>{
    const el=dialog.current, scroll=scroller.current, panel=sheet.current;
    if(!el||!scroll||!panel)return;
    let reachedOpen=false;
    el.showModal();
    // Fallback para scroll-initial-target: se establece antes de animar.
    scroll.scrollTo({left:scroll.clientWidth,behavior:"instant"});
    const frame=requestAnimationFrame(()=>requestAnimationFrame(()=>scroll.scrollTo({left:0,behavior:"auto"})));
    const observer=new IntersectionObserver(entries=>{
      const entry=entries.at(-1); if(!entry)return;
      if(entry.intersectionRatio>=.99)reachedOpen=true;
      if(reachedOpen&&entry.intersectionRatio===0)el.close();
    },{root:el,threshold:[0,.99,1]});
    observer.observe(panel);
    return ()=>{cancelAnimationFrame(frame);observer.disconnect();el.close();};
  },[]);
  return <dialog className="navigation-dialog" ref={dialog} onClose={onClose} aria-label="Navegación"><div ref={scroller} className="navigation-scroller" onClick={event=>{if(!sheet.current?.contains(event.target as Node))dialog.current?.close();}}><div className="navigation-sheet" ref={sheet}><div className="mobile-nav-heading"><strong>MARGIA</strong><button type="button" className="icon-button" autoFocus aria-label="Cerrar navegación" onClick={()=>dialog.current?.close()}><X size={22}/></button></div><nav aria-label="Principal">{children}</nav><p className="mobile-synthetic">Datos 100 % sintéticos · Entorno local</p></div></div></dialog>;
}
