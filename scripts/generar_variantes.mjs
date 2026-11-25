// Composiciones originales para el pretest. Reutilizan primitivas SVG propias.
// CC BY 4.0: MARGIA · demostración sintética. Sin servicios de generación en runtime.
import {readFile,writeFile} from "node:fs/promises";
import {fileURLToPath} from "node:url";
import path from "node:path";

const directory=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../frontend/public/assets/creatividad");
const perfiles=[
  {id:"hogar",base:1,fondo:"#E9E4D8",acento:"#6C7659",texto:"#313E2D",cta:"DESCUBRE LA COLECCIÓN",titulos:[["Objetos que", "perduran."],["Habitar", "lo esencial."],["La calma", "en el detalle."]]},
  {id:"moda",base:2,fondo:"#DDDCD1",acento:"#AA664B",texto:"#513C2E",cta:"HAZLO TUYO",titulos:[["Una historia", "que llevar."],["Esenciales", "bien elegidos."],["Hecho para", "acompañarte."]]},
  {id:"belleza",base:3,fondo:"#D6DDD3",acento:"#8B7050",texto:"#314C3A",cta:"VER SELECCIÓN",titulos:[["Tu pausa", "cotidiana."],["Un ritual", "sencillo."],["Cuidado en", "cada detalle."]]}
];
const estilos=["espacio","marco","detalle"];
for(const p of perfiles){
  const base=await readFile(path.join(directory,`aurel-${String(p.base).padStart(2,"0")}.svg`),"utf8");
  const start=base.indexOf("<ellipse");const end=base.indexOf('<path d="M42 493');
  if(start<0||end<start)throw new Error("No se encuentran las primitivas originales del producto.");
  const producto=base.slice(start,end);
  for(const [i,estilo] of estilos.entries()){
    const transform=["translate(0,-12)","translate(50,60) scale(.82)","translate(-35,-47) scale(1.15)"][i];
    const fondo=i===1?`<rect x="145" y="200" width="320" height="270" rx="2" fill="#FFF" opacity=".32"/><path d="M145 216V200H161M449 470H465V454" fill="none" stroke="${p.texto}" opacity=".55"/>`:i===2?`<circle cx="454" cy="348" r="142" fill="${p.acento}" opacity=".12"/>`:`<path d="M0 450Q320 378 600 422V600H0Z" fill="#FFF" opacity=".2"/>`;
    const [t1,t2]=p.titulos[i];
    const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600" role="img" aria-label="AUREL ${p.id}: ${t1} ${t2}"><title>${t1} ${t2} · Composición original de pretest</title><rect width="600" height="600" fill="${p.fondo}"/>${fondo}<text x="42" y="55" font-family="Georgia,serif" font-size="24" letter-spacing="6" fill="${p.texto}">AUREL</text><text x="558" y="51" text-anchor="end" font-family="sans-serif" font-size="9" letter-spacing="2" fill="${p.texto}">COLECCIÓN ${p.id.toUpperCase()}</text><path d="M42 77H558" stroke="${p.texto}" opacity=".25"/><text x="42" y="127" font-family="Georgia,serif" font-size="34" fill="${p.texto}">${t1}</text><text x="42" y="165" font-family="Georgia,serif" font-size="34" fill="${p.texto}">${t2}</text><g transform="${transform}">${producto}</g><path d="M42 493H558" stroke="${p.texto}" opacity=".25"/><text x="42" y="534" font-family="sans-serif" font-size="11" letter-spacing="1" fill="${p.texto}">${p.cta}</text><path d="M264 530H292M286 525 292 530 286 535" stroke="${p.texto}" fill="none"/><text x="558" y="570" text-anchor="end" font-family="sans-serif" font-size="8" letter-spacing="1" fill="${p.texto}">MARCA FICTICIA · ORIGINAL MARGIA</text></svg>`;
    await writeFile(path.join(directory,`pretest-${p.id}-${estilo}.svg`),svg,"utf8");
  }
}
console.log("Nueve composiciones originales de pretest guardadas localmente.");
