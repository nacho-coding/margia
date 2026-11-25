import Image from "next/image";
import type {CSSProperties} from "react";
import type {CreativeVariant} from "@/services/creatividad";

export function CreativeArt({variant:v,priority=false,lazy=false}:{variant:CreativeVariant;priority?:boolean;lazy?:boolean}){
  // Las evaluaciones anteriores mantienen íntegros su recurso y composición SVG.
  if(!v.plataforma||!v.texto)return <Image className="creative-legacy" src={v.asset} alt={`AUREL ${v.categoria}: ${v.nombre}. ${v.composicion}.`} width={600} height={600} loading={lazy?"lazy":"eager"} unoptimized/>;
  const p=v.plataforma,t=v.texto;
  return <span className={`creative-art creative-art--${p.id}`} data-testid="lienzo-creativo" data-platform={p.id} data-version={v.version_presentacion} style={{"--ad-ratio":`${p.ancho} / ${p.alto}`} as CSSProperties} role="img" aria-label={`AUREL. ${t.titular} ${v.alt} ${t.cta}. Vista previa ${p.nombre}, ${p.ubicacion}, ${p.relacion}.`}>
    <Image className="creative-art-photo" src={v.asset} alt="" width={v.ancho!} height={v.alto!} loading={lazy?"lazy":"eager"} fetchPriority={priority?"high":undefined} sizes="(max-width: 760px) 90vw, (max-width: 1400px) 30vw, 380px" unoptimized/>
    <span className="creative-art-brand" aria-hidden="true">AUREL</span>
    <span className="creative-art-copy" aria-hidden="true"><span className="creative-art-kicker">{t.antetitulo}</span><strong>{t.titular}</strong><span className="creative-art-support">{t.apoyo}</span><span className="creative-art-cta">{t.cta}<span>↗</span></span></span>
    <span className="creative-art-disclosure" aria-hidden="true">Imagen sintética</span>
  </span>;
}
