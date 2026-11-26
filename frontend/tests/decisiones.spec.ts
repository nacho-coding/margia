import {expect,test,type APIRequestContext} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import {mkdir,readFile} from "node:fs/promises";
import path from "node:path";
import type {ScenarioDraft,ScenarioExecution} from "../src/services/escenarios";

async function preparar(request:APIRequestContext,nombre:string){
  const r=await request.post("/api/v1/escenarios",{data:{nombre:`QA decisiones ${nombre} ${Date.now()}`}});
  expect(r.ok()).toBeTruthy();const s:ScenarioDraft=await r.json();
  const ejec=await request.post(`/api/v1/escenarios/${s.id}/ejecutar`,{data:{revision:1}});
  expect(ejec.ok()).toBeTruthy();return {s,e:await ejec.json() as ScenarioExecution};
}

test("borrador: guardar, revisar sin reescribir, duplicar y archivar con teclado",async({page,request})=>{
  const nombre=`QA revisión ${Date.now()}`;
  await page.goto("/escenarios");
  await page.getByLabel("Nombre de la comparación",{exact:false}).fill(nombre);
  await page.getByRole("button",{name:"Guardar borrador",exact:true}).click();
  await expect(page).toHaveURL(/escenario=borr-/);
  const sid=new URL(page.url()).searchParams.get("escenario")!;
  await expect(page.getByRole("heading",{name:"Editar borrador",exact:true})).toBeVisible();
  const original:ScenarioDraft=await (await request.get(`/api/v1/escenarios/${sid}`)).json();
  expect(original.ejecuciones).toEqual([]);
  await page.getByRole("button",{name:"Comparar y buscar alternativa",exact:true}).click();
  await expect(page).toHaveURL(/ejecucion=ejec-/);
  const eid=new URL(page.url()).searchParams.get("ejecucion")!;
  const antes=await (await request.get(`/api/v1/escenarios/ejecuciones/${eid}`)).json();
  await page.getByRole("link",{name:"Ver revisiones",exact:true}).click();
  await expect(page.getByLabel("Recorte de SEM marca (%)",{exact:false})).toHaveValue("50");
  await page.getByLabel("Recorte de SEM marca (%)",{exact:false}).fill("25");
  await page.getByRole("button",{name:"Guardar borrador",exact:true}).click();
  await expect(page.getByRole("status").filter({hasText:"Borrador guardado · revisión 2"})).toBeVisible();
  expect((await (await request.get(`/api/v1/escenarios/${sid}`)).json()).revisiones).toHaveLength(2);
  expect(await (await request.get(`/api/v1/escenarios/ejecuciones/${eid}`)).json()).toEqual(antes);
  await page.getByRole("button",{name:"Comparar y buscar alternativa",exact:true}).click();
  await expect(page).toHaveURL(/ejecucion=ejec-/);
  expect(new URL(page.url()).searchParams.get("ejecucion")).not.toBe(eid);
  await page.getByRole("button",{name:"Duplicar",exact:true}).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByRole("button",{name:"Conservar sin cambios",exact:true})).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.getByRole("button",{name:"Duplicar",exact:true})).toBeFocused();
  await page.getByRole("button",{name:"Duplicar",exact:true}).click();
  await page.getByLabel("Nombre de la copia",{exact:false}).fill(`${nombre} copia`);
  await page.getByRole("button",{name:"Crear copia",exact:true}).click();
  await expect(page).toHaveURL(/escenario=borr-/);
  const copia=new URL(page.url()).searchParams.get("escenario")!;expect(copia).not.toBe(sid);
  await page.getByRole("button",{name:"Archivar",exact:true}).click();
  await page.getByLabel("Motivo del archivo",{exact:false}).fill("Archivo explícito de la copia, conservando su revisión.");
  await page.getByRole("button",{name:"Archivar con motivo",exact:true}).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.getByRole("status").filter({hasText:"Archivado · revisión 1"})).toBeVisible();
  await expect(page.getByRole("heading",{name:"Editar borrador",exact:true})).toHaveCount(0);
  expect((await (await request.get(`/api/v1/escenarios/${copia}`)).json()).estado).toBe("archivado");
});

test("decisión: validación, error recuperable, aprobación persistida y descargas",async({page,request})=>{
  const {e}=await preparar(request,"aprobación");
  await page.goto(`/escenarios?ejecucion=${e.id}`);
  await expect(page.getByRole("heading",{name:"Registrar una decisión",exact:true})).toBeVisible();
  await page.getByRole("button",{name:"Registrar decisión",exact:true}).click();
  await expect(page.getByLabel("Motivo de la decisión",{exact:false})).toBeFocused();
  await expect(page.getByTestId("decision-guardada")).toHaveCount(0);
  const motivo="Mantener la estrategia hasta disponer de evidencia suficiente sobre reparto.";
  await page.getByLabel("Motivo de la decisión",{exact:false}).fill(motivo);
  await page.route(`**/api/v1/escenarios/ejecuciones/${e.id}/decision`,async route=>{
    if(route.request().method()==="POST")await route.fulfill({status:503,contentType:"application/json",body:JSON.stringify({detail:"Error temporal de QA al registrar; reintenta."})});else await route.continue();
  });
  await page.getByRole("button",{name:"Registrar decisión",exact:true}).click();
  await expect(page.locator(".form-error[role=alert]")).toContainText("Error temporal de QA");
  await expect(page.locator(".form-error[role=alert]")).toBeFocused();
  await expect(page.getByLabel("Motivo de la decisión",{exact:false})).toHaveValue(motivo);
  await page.unroute(`**/api/v1/escenarios/ejecuciones/${e.id}/decision`);
  await page.getByRole("button",{name:"Registrar decisión",exact:true}).click();
  await expect(page).toHaveURL(/decision=dec-/);
  const did=new URL(page.url()).searchParams.get("decision")!;
  await expect(page.getByTestId("decision-guardada")).toContainText(motivo);
  await expect(page.getByRole("heading",{name:"Aprobación registrada",exact:true})).toBeFocused();
  await page.reload();await expect(page.getByTestId("decision-guardada")).toContainText(did);
  await page.getByLabel("Periodo global").selectOption("90");
  await expect(page).toHaveURL(new RegExp(`decision=${did}`));
  for(const [formato,label] of [["csv","Descargar CSV"],["md","Descargar Markdown"]]){
    const download=page.waitForEvent("download");
    await page.getByTestId("decision-guardada").getByRole("link",{name:label,exact:true}).click();
    const archivo=await download;expect(archivo.suggestedFilename()).toBe(`margia-${e.id}.${formato}`);
    const contenido=await readFile((await archivo.path())!,"utf8");expect(contenido).toContain(e.id);expect(contenido).toContain(did);expect(contenido).toContain(motivo);
  }
  await page.goto("/");
  const enlace=page.locator(`a[href*="decision=${did}"]`);await expect(enlace).toBeVisible();await enlace.click();
  await expect(page.getByTestId("decision-guardada")).toContainText(did);
});

test("decisión: bloqueo real de reinversión y rechazo razonado sin alterar comparación",async({page,request})=>{
  const {e}=await preparar(request,"bloqueo");
  await page.goto(`/escenarios?ejecucion=${e.id}`);
  await page.getByRole("radio",{name:/B · reinvertir/}).check();
  await expect(page.locator(".scenario-decision-block")).toContainText("MMM");
  await page.getByLabel("Motivo de la decisión",{exact:false}).fill("La reinversión depende de un MMM que sigue bloqueado.");
  await page.getByRole("button",{name:"Registrar decisión",exact:true}).click();
  await expect(page.locator(".form-error[role=alert]")).toContainText("Aprobación bloqueada");
  await page.getByRole("radio",{name:"Rechazar el plan",exact:true}).check();
  await page.getByRole("button",{name:"Registrar decisión",exact:true}).click();
  await expect(page.getByRole("heading",{name:"Rechazo registrado",exact:true})).toBeVisible();
  expect((await (await request.get(`/api/v1/escenarios/ejecuciones/${e.id}`)).json()).resultado).toEqual(e.resultado);
  const d=await (await request.get(`/api/v1/escenarios/ejecuciones/${e.id}/decision`)).json();
  expect(d.decision.estado).toBe("rechazado");expect(d.decision.evidencia.activa_publicidad).toBeFalsy();
  await page.route(/\/api\/v1\/escenarios(?:\?.*)?$/,route=>route.fulfill({status:503,contentType:"application/json",body:JSON.stringify({detail:"Catálogo temporalmente indisponible en QA."})}));
  await page.reload();
  await expect(page.getByTestId("decision-guardada")).toContainText("Rechazo registrado");
  await expect(page.getByTestId("delta-escenario-ahorro")).toBeVisible();
});

test("borrador: una revisión externa evita sobrescribir cambios",async({page,request})=>{
  const {s}=await preparar(request,"conflicto");
  await page.goto(`/escenarios?escenario=${s.id}`);
  await expect(page.getByRole("heading",{name:"Editar borrador",exact:true})).toBeVisible();
  const externo=await request.patch(`/api/v1/escenarios/${s.id}`,{data:{revision:1,parametros:{...s.parametros,nombre:"QA cambio externo conservado"}}});expect(externo.ok()).toBeTruthy();
  await page.getByLabel("Nombre de la comparación",{exact:false}).fill("QA cambio local en conflicto");
  await page.getByRole("button",{name:"Guardar borrador",exact:true}).click();
  await expect(page.locator(".form-error[role=alert]")).toContainText("otra revisión");
  await expect(page.locator(".form-error[role=alert]")).toBeFocused();
  await expect(page.getByLabel("Nombre de la comparación",{exact:false})).toHaveValue("QA cambio local en conflicto");
  const d=await (await request.get(`/api/v1/escenarios/${s.id}`)).json();expect(d.nombre).toBe("QA cambio externo conservado");expect(d.revision).toBe(2);
});

test("decisión y archivo: revisión visual y accesibilidad en cuatro tamaños",async({page,request})=>{
  test.setTimeout(180_000);
  const {s,e}=await preparar(request,"visual");
  const dir=path.resolve("../artifacts/qa");await mkdir(dir,{recursive:true});
  const sizes=[{width:1440,height:900},{width:1920,height:1080},{width:1280,height:720},{width:390,height:844}];
  await page.goto(`/escenarios?ejecucion=${e.id}`);
  await expect(page.getByRole("heading",{name:"Registrar una decisión",exact:true})).toBeVisible();
  async function capture(estado:string){for(const size of sizes){
    await page.setViewportSize(size);await page.evaluate(()=>document.fonts.ready);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth)).toBeFalsy();
    await page.evaluate(()=>window.scrollTo(0,0));
    await page.screenshot({path:path.join(dir,`decisiones-${estado}-${size.width}.png`),fullPage:true});
    await page.locator(estado==="formulario"?".scenario-decision":".scenario-decision-record").screenshot({path:path.join(dir,`decisiones-detalle-${estado}-${size.width}.png`)});
    const axe=await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze();
    expect(axe.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
  }}
  await capture("formulario");
  await page.getByLabel("Motivo de la decisión",{exact:false}).fill("Mantener la estrategia mientras se contrasta la hipótesis de reinversión.");
  await page.getByRole("button",{name:"Registrar decisión",exact:true}).click();
  await expect(page.getByTestId("decision-guardada")).toBeVisible();
  await capture("registrada");
  await page.setViewportSize(sizes[0]);
  await page.getByRole("button",{name:"Archivar",exact:true}).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.screenshot({path:path.join(dir,"decisiones-archivo-1440.png")});
  expect((await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze()).violations).toEqual([]);
  await page.keyboard.press("Escape");
  const detalle=await (await request.get(`/api/v1/escenarios/${s.id}`)).json();expect(detalle.estado).toBe("borrador");
});
