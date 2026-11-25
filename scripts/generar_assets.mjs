// Diseños vectoriales originales de MARGIA. Sin imágenes ni marcas de terceros.
// Licencia de los SVG generados: Creative Commons Attribution 4.0 International.
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";
const directory=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../frontend/public/assets/creatividad");
await mkdir(directory,{recursive:true});
const palettes=[
  ["#E9E4D8","#6C7659","#313E2D"],["#DDDCD1","#AA664B","#513C2E"],["#D6DDD3","#D1AE80","#314C3A"],
  ["#E7DCD0","#865B43","#4D3D32"],["#E3E4DB","#A9B8A2","#2D463C"],["#DDD6C8","#8C654A","#453A2C"],
  ["#D2DCD8","#637F73","#233C33"],["#E8DDCF","#B18D6F","#5F4937"],["#DDD8DA","#9B6D6E","#51373F"],
  ["#D9DFD3","#7C8C63","#384631"],["#E8E0D4","#A58357","#50412D"],["#DFDDD7","#90856D","#403C30"],
];
const content=[
  ["Objetos que perduran.","El arte de vivir despacio.","HOGAR"],
  ["Una pausa cotidiana.","Haz espacio para lo esencial.","HOGAR"],
  ["Menos. Pero mejor.","Una selección hecha para durar.","MODA"],
  ["Tu próximo ritual.","Bienestar en las pequeñas cosas.","BELLEZA"],
  ["Habitar el momento.","Texturas que se sienten en casa.","HOGAR"],
  ["Lo llevas contigo.","Esenciales para cada historia.","MODA"],
  ["La calma tiene forma.","Diseño para tus días.","HOGAR"],
  ["Hecho para quedarte.","La belleza de lo sencillo.","HOGAR"],
  ["Cuidar empieza aquí.","Redescubre tus pequeños rituales.","BELLEZA"],
  ["Una nueva mirada.","Tus esenciales de temporada.","MODA"],
  ["El tiempo, para ti.","Momentos que importan.","HOGAR"],
  ["Naturalmente tuyo.","Cada día, algo extraordinario.","BELLEZA"],
];
function object(i,p){
  const [,c,d]=p;
  if(i%3===0)return `<ellipse cx="330" cy="442" rx="136" ry="15" fill="${d}" opacity=".11"/><path d="M218 280Q198 440 255 442H365Q406 424 389 280Z" fill="${c}"/><ellipse cx="304" cy="281" rx="86" ry="21" fill="${d}" opacity=".5"/><ellipse cx="304" cy="284" rx="70" ry="13" fill="${d}" opacity=".6"/><path d="M270 282Q245 346 270 429" stroke="#FFF" stroke-width="3" fill="none" opacity=".16"/><path d="M265 280Q257 226 283 197M302 278Q330 223 352 211M324 272Q340 246 383 248" stroke="${d}" stroke-width="3" fill="none"/><path d="M283 211Q244 175 261 158Q297 157 283 211M320 242Q352 178 373 192Q382 225 320 242M350 250Q383 223 404 247Q389 276 350 250" fill="${d}" opacity=".8"/><rect x="107" y="405" width="103" height="28" rx="4" fill="#D8C8AC" transform="rotate(-5 107 405)"/><rect x="115" y="390" width="100" height="19" rx="3" fill="#F2EEE4" transform="rotate(3 115 390)"/>`;
  if(i%3===1)return `<ellipse cx="305" cy="440" rx="156" ry="16" fill="${d}" opacity=".12"/><path d="M177 292Q154 273 165 250L209 203 252 223H351L394 203 437 250Q448 272 427 292L392 276 382 435H221L213 276Z" fill="${c}"/><path d="M252 223Q301 278 351 223" fill="none" stroke="${d}" stroke-width="4" opacity=".5"/><path d="M255 274 243 420M350 272 360 421" fill="none" stroke="#FFF" stroke-width="2" opacity=".23"/><path d="M222 418Q302 429 382 418" fill="none" stroke="${d}" opacity=".2"/><path d="M201 303 216 410M398 303 385 410" stroke="${d}" stroke-width="1" opacity=".25"/><rect x="291" y="240" width="24" height="20" rx="2" fill="#EDE7DA"/><text x="303" y="253" text-anchor="middle" font-family="Georgia,serif" font-size="8" fill="${d}">A</text>`;
  return `<ellipse cx="315" cy="445" rx="145" ry="13" fill="${d}" opacity=".12"/><rect x="322" y="253" width="104" height="189" rx="3" fill="${c}"/><path d="M322 253 347 239H449V429L426 442V253Z" fill="${d}" opacity=".4"/><rect x="202" y="312" width="91" height="129" rx="15" fill="${c}"/><rect x="222" y="270" width="52" height="53" rx="5" fill="${d}"/><rect x="229" y="252" width="38" height="22" rx="3" fill="#D0C4A9"/><rect x="214" y="347" width="67" height="67" rx="1" fill="#EDE7DA"/><text x="247" y="369" text-anchor="middle" font-size="13" letter-spacing="2" font-family="Georgia,serif" fill="${d}">AUREL</text><path d="M231 382H263" stroke="${d}" stroke-width=".6"/><text x="247" y="397" text-anchor="middle" font-size="7" letter-spacing="1" font-family="sans-serif" fill="${d}">ESENCIAL</text><text x="374" y="302" text-anchor="middle" font-size="15" letter-spacing="2" font-family="Georgia,serif" fill="#F7F1E6">AUREL</text><text x="374" y="404" text-anchor="middle" font-size="8" letter-spacing="1" font-family="sans-serif" fill="#F7F1E6">CUIDADO DIARIO</text>`;
}
for(let i=0;i<12;i++){
  const p=palettes[i],[title,subtitle,category]=content[i];
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600" role="img" aria-label="AUREL: ${title}"><title>${title} · Diseño original para una marca ficticia</title><rect width="600" height="600" fill="${p[0]}"/><path d="M0 450Q320 378 600 422V600H0Z" fill="#FFFFFF" opacity=".14"/><text x="42" y="54" font-family="Georgia,serif" font-size="24" letter-spacing="6" fill="${p[2]}">AUREL</text><text x="558" y="50" text-anchor="end" font-family="sans-serif" font-size="9" letter-spacing="2" fill="${p[2]}">COLECCIÓN ${["HOGAR","MODA","BELLEZA"][i%3]}</text><path d="M42 76H558" stroke="${p[2]}" opacity=".25"/><text x="42" y="133" font-family="Georgia,serif" font-size="32" fill="${p[2]}">${title}</text><text x="44" y="159" font-family="sans-serif" font-size="12" letter-spacing=".2" fill="${p[2]}" opacity=".85">${subtitle}</text>${object(i,p)}<path d="M42 493H558" stroke="${p[2]}" opacity=".25"/><text x="42" y="532" font-family="sans-serif" font-size="11" letter-spacing="1" fill="${p[2]}">${["DESCUBRE LA COLECCIÓN","HAZLO TUYO","VER SELECCIÓN"][i%3]}</text><path d="M242 528H270M264 523 270 528 264 533" stroke="${p[2]}" fill="none"/><text x="558" y="559" text-anchor="end" font-family="sans-serif" font-size="8" letter-spacing="1" fill="${p[2]}" opacity=".65">MARCA FICTICIA · DISEÑO ORIGINAL MARGIA</text></svg>`;
  await writeFile(path.join(directory,`aurel-${String(i+1).padStart(2,"0")}.svg`),svg,"utf8");
}
console.log("12 composiciones SVG originales generadas; sin dependencias remotas.");
