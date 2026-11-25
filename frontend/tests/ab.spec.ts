import {expect,test,type APIRequestContext} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import {mkdir,readFile} from "node:fs/promises";
import path from "node:path";
import type {ABDetail} from "../src/services/ab";

const percent=(v:number)=>new Intl.NumberFormat("es-ES",{style:"percent",minimumFractionDigits:1,maximumFractionDigits:1}).format(v);
const number=(v:number)=>new Intl.NumberFormat("es-ES",{maximumFractionDigits:0}).format(v);

async function pretest(request:APIRequestContext,label:string){
  const p=await request.post("/api/v1/creativos/evaluar",{data:{objetivo:`QA A/B ${label} ${Date.now()}`}});
  expect(p.ok()).toBeTruthy();return p.json();
}

test("A/B: selección → protocolo → observaciones → contraste → aprendizaje versionado",async({page,request})=>{
  const errors:string[]=[];page.on("pageerror",e=>errors.push(e.message));
  const original=await (await request.get("/api/v1/contexto")).json();
  await page.goto("/creatividad?vista=pretest");
  await page.getByLabel("Objetivo del brief (obligatorio)",{exact:true}).fill(`QA A/B integrado ${Date.now()}`);
  await page.getByRole("button",{name:"Generar propuestas de ejemplo",exact:true}).click();
  await page.getByRole("button",{name:"Guardar propuesta 2",exact:true}).click();
  await page.getByRole("link",{name:"Contrastar selección en A/B",exact:true}).click();
  await expect(page.getByRole("heading",{name:"Diseñar una prueba creativa",exact:true})).toBeVisible();
  await page.getByLabel("Nombre de la prueba (obligatorio)",{exact:true}).fill(`QA aprendizaje A/B ${Date.now()}`);
  await page.getByRole("checkbox",{name:"Una escena cotidiana",exact:true}).check();
  await page.getByRole("button",{name:"Guardar diseño y calcular MDE",exact:true}).click();
  await expect(page).toHaveURL(/prueba=ab-/);
  const id=new URL(page.url()).searchParams.get("prueba")!;
  const uri="/api/v1/creativos/pruebas/"+id;
  const d:ABDetail=await (await request.get(uri)).json();
  expect(d.estado).toBe("disenado");expect(d.observaciones).toEqual([]);
  await expect(page.locator(".ab-report .model-metrics article").filter({hasText:"MDE relativo aproximado"}).locator("strong")).toHaveText(percent(d.protocolo.plan.mde_relativo));
  await page.getByRole("button",{name:"Ejecutar prueba sintética",exact:true}).click();
  await expect(page.getByRole("region",{name:"Observaciones diarias A/B",exact:true}).locator("tbody tr")).toHaveCount(42);
  await page.getByRole("button",{name:"Evaluar resultados",exact:true}).click();
  await expect(page.locator(".ab-interval canvas")).toHaveCount(1);
  const r:ABDetail=await (await request.get(uri)).json();
  expect(r.protocolo.evaluacion!.compatible).toBeTruthy();
  const rows=page.getByRole("region",{name:"Denominadores y tasas A/B",exact:true}).locator("tbody tr");
  for(let i=0;i<r.protocolo.evaluacion!.filas.length;i++)await expect(rows.nth(i).locator("td").first()).toHaveText(number(r.protocolo.evaluacion!.filas[i].impresiones));
  await expect(page.getByRole("region",{name:"Contrastes de CTR",exact:true}).locator("tbody tr")).toHaveCount(2);
  await page.getByRole("button",{name:"Guardar aprendizaje de CTR",exact:true}).click();
  await expect(page.getByText("Aprendizaje versionado guardado",{exact:true})).toBeVisible();
  const accepted:ABDetail=await (await request.get(uri)).json();
  const model=accepted.protocolo.actualizacion!.modelo;
  await page.reload();await expect(page.locator(".ab-saved")).toContainText(model);
  await page.getByLabel("Periodo global").selectOption("90");
  await expect(page).toHaveURL(new RegExp(`dias=90.*prueba=${id}`));
  await page.getByRole("link",{name:"Consultar el pretest y su aprendizaje",exact:true}).click();
  await expect(page.getByTestId("aprendizaje-creativo")).toContainText(model);
  await page.reload();await expect(page.getByTestId("aprendizaje-creativo")).toContainText("no hay efecto económico identificado");
  expect((await (await request.get("/api/v1/contexto")).json()).checksum).toBe(original.checksum);
  expect(errors).toEqual([]);
});

test("A/B: validación, error recuperable, abstención por muestra y asignaciones CSV",async({page,request})=>{
  const p=await pretest(request,"insuficiente");let broken=true;
  await page.route("**/api/v1/creativos/pruebas/disenar",route=>broken?route.fulfill({status:503,contentType:"application/json",body:JSON.stringify({detail:"No se ha podido guardar el protocolo."})}):route.continue());
  await page.goto(`/creatividad?vista=ab&evaluacion=${p.id}`);
  await page.getByLabel("Impresiones por brazo",{exact:true}).fill("0");
  await page.getByRole("button",{name:"Guardar diseño y calcular MDE",exact:true}).click();
  expect(await page.getByLabel("Impresiones por brazo",{exact:true}).evaluate((el:HTMLInputElement)=>el.validity.rangeUnderflow)).toBeTruthy();
  await page.getByLabel("Impresiones por brazo",{exact:true}).fill("500");
  await page.getByRole("button",{name:"Guardar diseño y calcular MDE",exact:true}).click();
  await expect(page.locator(".form-error")).toContainText("No se ha podido guardar");
  await expect(page.locator(".form-error")).toBeFocused();
  await expect(page.getByLabel("Impresiones por brazo",{exact:true})).toHaveValue("500");
  broken=false;await page.getByRole("button",{name:"Guardar diseño y calcular MDE",exact:true}).click();
  await page.getByRole("button",{name:"Ejecutar prueba sintética",exact:true}).click();
  await page.getByRole("button",{name:"Evaluar resultados",exact:true}).click();
  await expect(page.getByText("Conteos insuficientes",{exact:false})).toBeVisible();
  await expect(page.getByRole("button",{name:"Guardar aprendizaje de CTR",exact:true})).toHaveCount(0);
  const downloading=page.waitForEvent("download");
  await page.getByRole("link",{name:"Exportar asignaciones CSV",exact:true}).click();
  const download=await downloading;
  const csv=await readFile((await download.path())!,"utf8");
  expect(csv.trim().split("\n")).toHaveLength(1001);
  expect(csv).toContain("oportunidad_sintetica;brazo;probabilidad");
});

test("A/B: revisión visual y accesibilidad del diseño y resultado en cuatro tamaños",async({page,request})=>{
  test.setTimeout(180_000);
  const dir=path.resolve("../artifacts/qa");await mkdir(dir,{recursive:true});
  const p=await pretest(request,"visual");
  await page.goto(`/creatividad?vista=ab&evaluacion=${p.id}`);
  await expect(page.getByRole("heading",{name:"Diseñar una prueba creativa",exact:true})).toBeVisible();
  await expect(page.locator(".ab-preview img")).toHaveCount(1);
  const sizes=[{width:1440,height:900},{width:1920,height:1080},{width:1280,height:720},{width:390,height:844}];
  async function capture(label:string){for(const size of sizes){
    await page.setViewportSize(size);await page.evaluate(()=>document.fonts.ready);
    await expect.poll(()=>page.locator(".ab-workspace img").evaluateAll(imgs=>imgs.every(el=>(el as HTMLImageElement).complete&&(el as HTMLImageElement).naturalWidth>0))).toBeTruthy();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth)).toBeFalsy();
    await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(dir,`ab-${label}-${size.width}.png`),fullPage:true});
    const result=await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze();
    expect(result.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
  }}
  await capture("diseno");
  const design=await request.post("/api/v1/creativos/pruebas/disenar",{data:{pretest_id:p.id,control:p.variantes[0].id,tratamientos:[p.variantes[2].id],nombre:`QA visual resultado A/B ${Date.now()}`}});
  expect(design.ok()).toBeTruthy();const d=await design.json();
  expect((await request.post(`/api/v1/creativos/pruebas/${d.id}/ejecutar`,{data:{}})).ok()).toBeTruthy();
  expect((await request.post(`/api/v1/creativos/pruebas/${d.id}/evaluar`,{data:{}})).ok()).toBeTruthy();
  await page.goto(`/creatividad?vista=ab&prueba=${d.id}&evaluacion=${p.id}`);
  await expect(page.locator(".ab-interval canvas")).toHaveCount(1);
  await capture("resultado");
});
