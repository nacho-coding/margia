// Transcodifica los originales de Imagegen; no altera el contenido de las fotografías.
// Sharp ya está fijado transitivamente por Next en el lockfile del frontend.
import {readFile,writeFile,mkdir} from "node:fs/promises";
import {createRequire} from "node:module";
import {fileURLToPath} from "node:url";
import {createHash} from "node:crypto";
import path from "node:path";

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const require=createRequire(path.join(root,"frontend/package.json"));
const sharp=require("sharp");
const input=JSON.parse(await readFile(path.resolve(root,process.argv[2]||"artifacts/qa/imagenes-generadas.json"),"utf8"));
const output=path.join(root,"frontend/public/assets/creatividad/fotografia-v2");
await mkdir(output,{recursive:true});
const images=[];
for(const item of input.imagenes){
  if(!/^(hogar|moda|belleza)-(espacio|marco|detalle)$/.test(item.id))throw new Error("ID de imagen no válido.");
  const bytes=await sharp(item.origen).webp({quality:83,effort:6}).toBuffer();
  const meta=await sharp(bytes).metadata();
  if(bytes.length>300000)throw new Error(`Revisar el peso de ${item.id}`);
  const target=path.join(output,`${item.id}.webp`);
  let previous;
  try{previous=await readFile(target);}catch(error){if(error.code!=="ENOENT")throw error;}
  if(previous&&!previous.equals(bytes))throw new Error(`Recurso versionado inmutable: ${item.id}. Crear otra versión para cambiarlo.`);
  if(!previous)await writeFile(target,bytes);
  images.push({id:item.id,asset:`/assets/creatividad/fotografia-v2/${item.id}.webp`,ancho:meta.width,alto:meta.height,bytes:bytes.length,sha256:createHash("sha256").update(bytes).digest("hex")});
}
if(images.length!==9||new Set(images.map(i=>i.id)).size!==9)throw new Error("Se necesitan nueve imágenes distintas.");
await writeFile(path.join(root,"backend/app/creatividad/imagenes.json"),JSON.stringify({version:"fotografia-2.0.0",origen:"Imagen sintética generada con IA durante el desarrollo",imagenes:images},null,2)+"\n");
console.log(JSON.stringify({imagenes:images.length,bytes:images.reduce((s,i)=>s+i.bytes,0),max_bytes:Math.max(...images.map(i=>i.bytes))}));
