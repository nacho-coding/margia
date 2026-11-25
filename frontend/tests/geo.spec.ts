import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const money=(v:number)=>new Intl.NumberFormat("es-ES",{style:"currency",currency:"EUR",maximumFractionDigits:0}).format(v);

test("geo: Search → diseño → ejecución → evaluación → evidencia versionada",async({page,request})=>{
  test.setTimeout(150_000);
  const errors:string[]=[];page.on("pageerror",e=>errors.push(e.message));
  const before=await (await request.get("/api/v1/contexto")).json();
  const saved=await (await request.post("/api/v1/busqueda/simular",{data:{recorte_pct:50}})).json();
  await page.goto("/one-search");
  await page.getByRole("link",{name:"Diseñar experimento geográfico",exact:true}).click();
  await page.getByLabel("Nombre de la prueba (obligatorio)",{exact:true}).fill(`QA recorrido geo ${Date.now()}`);
  await page.getByLabel("Coste de prueba (€)",{exact:true}).fill("100000");
  await page.getByRole("button",{name:"Guardar diseño y calcular valor",exact:true}).click();
  await expect(page).toHaveURL(/experimento=geo-/);
  const id=new URL(page.url()).searchParams.get("experimento")!;
  const uri="/api/v1/experimentos/"+id;
  let detail=await (await request.get(uri)).json();
  expect(detail.observaciones).toEqual([]);
  await expect(page.getByTestId("evsi")).toHaveText(money(detail.protocolo.informacion.evsi));
  await expect(page.getByTestId("valor-informacion")).toHaveText(money(detail.protocolo.informacion.valor_neto));
  await expect(page.getByText("La prueba no compensa frente a la mejor acción actual",{exact:true})).toBeVisible();
  await page.getByRole("button",{name:"Ejecutar en universo sintético",exact:true}).click();
  await expect(page.getByRole("button",{name:"Evaluar resultado",exact:true})).toBeVisible();
  await page.getByRole("button",{name:"Evaluar resultado",exact:true}).click();
  await expect(page.getByTestId("efecto-geo")).toBeVisible();
  await expect(page.getByRole("button",{name:"Aceptar y actualizar evidencia",exact:true})).toBeVisible();
  detail=await (await request.get(uri)).json();
  expect(detail.protocolo.evaluacion.numero_pares).toBe(12);
  expect(detail.observaciones).toHaveLength(48);
  await expect(page.locator("canvas")).toHaveCount(2);
  const dir=path.resolve("../artifacts/qa");await mkdir(dir,{recursive:true});
  for(const size of [{width:1440,height:900},{width:1920,height:1080},{width:1280,height:720},{width:390,height:844}]){
    await page.setViewportSize(size);await page.evaluate(()=>document.fonts.ready);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth)).toBeFalsy();
    await page.screenshot({path:path.join(dir,`geo-evaluado-${size.width}.png`),fullPage:true});
    const axe=await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze();
    expect(axe.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
  }
  await page.setViewportSize({width:1440,height:900});
  await page.getByRole("button",{name:"Aceptar y actualizar evidencia",exact:true}).click();
  await expect(page.getByRole("status")).toContainText("Evidencia actualizada");
  await page.reload();
  await expect(page.getByRole("link",{name:"Volver a One Search",exact:true})).toBeVisible();
  await page.getByRole("link",{name:"Volver a One Search",exact:true}).click();
  await expect(page.getByText("Experimento geográfico aceptado",{exact:true})).toBeVisible();
  const model=await (await request.get("/api/v1/busqueda/evidencia")).json();
  const accepted=await (await request.get(uri)).json();
  expect(model.modelo.id).toBe(accepted.protocolo.actualizacion.modelo);
  if(saved.resultado.version==="search-1.0.0")expect(model.modelo.id).not.toBe(saved.resultado.modelo);
  const old=await (await request.get("/api/v1/busqueda/simulaciones/"+saved.id)).json();
  expect(old.resultado).toEqual(saved.resultado);
  expect((await (await request.get("/api/v1/contexto")).json()).checksum).toBe(before.checksum);
  expect(errors).toEqual([]);
});

test("geo: tratamiento nulo conserva evidencia y muestra abstención",async({page,request})=>{
  const before=await (await request.get("/api/v1/busqueda/evidencia")).json();
  await page.goto("/experimentos");
  await page.getByLabel("Nombre de la prueba (obligatorio)",{exact:true}).fill(`QA nulo ${Date.now()}`);
  await page.getByLabel("Recorte de SEM marca (%)",{exact:true}).fill("0");
  await page.getByRole("button",{name:"Guardar diseño y calcular valor",exact:true}).click();
  await page.getByRole("button",{name:"Ejecutar en universo sintético",exact:true}).click();
  await page.getByRole("button",{name:"Evaluar resultado",exact:true}).click();
  await expect(page.getByTestId("efecto-geo")).toBeVisible();
  await expect(page.getByText("Tratamiento nulo:",{exact:false})).toBeVisible();
  await expect(page.getByRole("button",{name:"Aceptar y actualizar evidencia",exact:true})).toHaveCount(0);
  expect((await (await request.get("/api/v1/busqueda/evidencia")).json()).modelo.id).toBe(before.modelo.id);
});

test("geo: restricciones nativas, error recuperable, selección y contexto",async({page})=>{
  let broken=true;
  await page.route("**/api/v1/experimentos/disenar",r=>broken?r.fulfill({status:503,contentType:"application/json",body:JSON.stringify({detail:"No se ha podido guardar el diseño."})}):r.continue());
  await page.goto("/experimentos?dias=56&mercado=m01");
  await page.getByLabel("Recorte de SEM marca (%)",{exact:true}).fill("101");
  await page.getByRole("button",{name:"Guardar diseño y calcular valor",exact:true}).click();
  expect(await page.getByLabel("Recorte de SEM marca (%)",{exact:true}).evaluate((el:HTMLInputElement)=>el.validity.rangeOverflow)).toBeTruthy();
  await page.getByLabel("Recorte de SEM marca (%)",{exact:true}).fill("25");
  await page.getByRole("button",{name:"Guardar diseño y calcular valor",exact:true}).click();
  await expect(page.locator(".form-error")).toContainText("No se ha podido guardar");
  await expect(page.locator(".form-error")).toBeFocused();
  await expect(page.getByLabel("Recorte de SEM marca (%)",{exact:true})).toHaveValue("25");
  broken=false;
  await page.getByRole("button",{name:"Guardar diseño y calcular valor",exact:true}).click();
  await expect(page).toHaveURL(/mercado=m01.*experimento=geo-/);
  await page.getByLabel("Periodo global").selectOption("90");
  await expect(page).toHaveURL(/dias=90.*experimento=geo-/);
  await expect(page.getByRole("button",{name:"Ejecutar en universo sintético",exact:true})).toBeVisible();
});
