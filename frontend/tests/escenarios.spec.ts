import {expect,test,type APIRequestContext} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import {mkdir} from "node:fs/promises";
import path from "node:path";
import type {ScenarioExecution} from "../src/services/escenarios";

const euros=(v:number)=>new Intl.NumberFormat("es-ES",{style:"currency",currency:"EUR",maximumFractionDigits:0}).format(v);

async function propuesta(request:APIRequestContext,nombre:string,frecuencia=2.5){
  const respuesta=await request.post("/api/v1/creativos/evaluar",{data:{objetivo:`QA escenario ${nombre} ${Date.now()}`,frecuencia}});
  expect(respuesta.ok()).toBeTruthy();const p=await respuesta.json();
  const s=await request.post("/api/v1/creativos/selecciones",{data:{pretest_id:p.id,variante_id:p.variantes[1].id}});
  expect(s.ok()).toBeTruthy();return {p,s:await s.json()};
}

test("escenarios: Search → comparación → búsqueda limitada → recarga y contexto",async({page,request})=>{
  const errors:string[]=[];page.on("pageerror",e=>errors.push(e.message));
  const ctx=await (await request.get("/api/v1/contexto")).json();
  await page.goto("/one-search");
  await page.getByLabel("Recorte de SEM marca (%)",{exact:true}).fill("50");
  await page.getByRole("button",{name:"Calcular recorte",exact:true}).click();
  const enlace=page.getByRole("link",{name:"Comparar ahorro y reinversión",exact:true});
  await expect(enlace).toBeVisible();await enlace.click();
  await expect(page).toHaveURL(/simulacion=sim-search-/);
  const origen=new URL(page.url()).searchParams.get("simulacion")!;
  await expect(page.getByRole("heading",{name:"Preparar comparación",exact:true})).toBeVisible();
  await page.getByLabel("Nombre de la comparación",{exact:false}).fill(`QA comparación Search ${Date.now()}`);
  await page.getByRole("button",{name:"Comparar y buscar alternativa",exact:true}).click();
  await expect(page).toHaveURL(/ejecucion=ejec-/);
  const id=new URL(page.url()).searchParams.get("ejecucion")!;
  const d:ScenarioExecution=await (await request.get(`/api/v1/escenarios/ejecuciones/${id}`)).json();
  expect(d.entradas.simulacion_search_id).toBe(origen);
  expect(d.resultado.optimizacion.demanda_habilitada).toBeFalsy();
  expect(d.resultado.reinversion.elegible).toBeFalsy();
  await expect(page.getByTestId("delta-escenario-ahorro")).toHaveText(euros(d.resultado.ahorro.delta));
  await expect(page.getByText("Búsqueda limitada a Search",{exact:true})).toBeVisible();
  await expect(page.locator(".scenario-waterfall canvas")).toHaveCount(1);
  await page.getByRole("button",{name:"Ahorro",exact:true}).click();
  await expect(page.getByRole("region",{name:"Desglose económico del escenario",exact:true}).locator("tbody tr").last()).toContainText(euros(d.resultado.ahorro.delta));
  await page.getByRole("button",{name:"Método y restricciones",exact:true}).click();
  await expect(page.getByRole("dialog")).toContainText(d.resultado.traza_draws.checksum);
  await page.keyboard.press("Escape");await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.reload();await expect(page.getByTestId("delta-escenario-ahorro")).toHaveText(euros(d.resultado.ahorro.delta));
  await page.getByLabel("Periodo global").selectOption("90");
  await expect(page).toHaveURL(new RegExp(`dias=90.*ejecucion=${id}`));
  await expect(page.getByTestId("delta-escenario-ahorro")).toHaveText(euros(d.resultado.ahorro.delta));
  expect((await (await request.get(`/api/v1/escenarios/ejecuciones/${id}`)).json()).resultado).toEqual(d.resultado);
  expect((await (await request.get("/api/v1/contexto")).json()).checksum).toBe(ctx.checksum);
  expect(errors).toEqual([]);
});

test("escenarios: selección con aprendizaje A/B conserva imagen y solo imputa producción",async({page,request})=>{
  const {p,s}=await propuesta(request,"aprendizaje",3.4);
  const diseno=await request.post("/api/v1/creativos/pruebas/disenar",{data:{pretest_id:p.id,control:p.variantes[0].id,tratamientos:[p.variantes[1].id],nombre:`QA A/B para escenario ${Date.now()}`}});
  expect(diseno.ok()).toBeTruthy();const ab=await diseno.json();
  for(const paso of ["ejecutar","evaluar","aceptar"])expect((await request.post(`/api/v1/creativos/pruebas/${ab.id}/${paso}`,{data:{}})).ok()).toBeTruthy();
  await page.goto(`/creatividad?vista=pretest&evaluacion=${p.id}&seleccion=${s.id}`);
  await page.getByRole("link",{name:"Comparar en un escenario",exact:true}).click();
  await expect(page.getByLabel("Propuesta guardada",{exact:true})).toHaveValue(s.id);
  await expect(page.locator(".scenario-creative img")).toHaveCount(1);
  await page.getByLabel("Nombre de la comparación",{exact:false}).fill(`QA producción ${Date.now()}`);
  await page.getByLabel("Producción pendiente para B (€)",{exact:false}).fill("350");
  await page.getByRole("button",{name:"Comparar y buscar alternativa",exact:true}).click();
  await expect(page).toHaveURL(/ejecucion=ejec-/);
  const id=new URL(page.url()).searchParams.get("ejecucion")!;
  const d:ScenarioExecution=await (await request.get(`/api/v1/escenarios/ejecuciones/${id}`)).json();
  expect(d.resultado.reinversion.metricas.creatividad).toBe(350);
  expect(d.modelos.creativo_ab).toBeTruthy();
  await expect(page.locator(".scenario-selected")).toContainText("Aprendizaje A/B de CTR");
  const control=await request.post("/api/v1/escenarios/ejecutar",{data:{...d.entradas,nombre:`QA control de coste ${Date.now()}`,coste_produccion:0}});
  expect(control.ok()).toBeTruthy();const sinCoste:ScenarioExecution=await control.json();
  expect(d.resultado.reinversion.delta).toBeCloseTo(sinCoste.resultado.reinversion.delta-350,6);
  expect(d.resultado.reinversion.delta_pedidos).toBe(sinCoste.resultado.reinversion.delta_pedidos);
  expect(d.resultado.reinversion.multiplicador_demanda).toBe(1);
  await page.reload();await expect(page.locator(".scenario-selected img")).toHaveCount(1);
  await expect(page.getByTestId("delta-escenario-reinversion")).toHaveText(euros(d.resultado.reinversion.delta));
  await page.getByRole("link",{name:"Consultar propuesta y aprendizaje",exact:true}).click();
  await expect(page.getByTestId("seleccion-creativa")).toContainText(s.id);
});

test("escenarios: validación, error recuperable, ámbito nacional y ausencia de candidato",async({page,request})=>{
  let broken=true;
  await page.route("**/api/v1/escenarios/ejecutar",route=>broken?route.fulfill({status:503,contentType:"application/json",body:JSON.stringify({detail:"No se ha podido guardar la comparación."})}):route.continue());
  await page.goto("/escenarios");
  const cut=page.getByLabel("Recorte de SEM marca (%)",{exact:false});
  await page.getByLabel("Producción pendiente para B (€)",{exact:false}).fill("10");
  await page.getByRole("button",{name:"Comparar y buscar alternativa",exact:true}).click();
  await expect(page.locator(".form-error")).toContainText("Selecciona una propuesta guardada");
  await page.getByLabel("Producción pendiente para B (€)",{exact:false}).fill("0");
  await cut.fill("-1");await page.getByRole("button",{name:"Comparar y buscar alternativa",exact:true}).click();
  expect(await cut.evaluate((el:HTMLInputElement)=>el.validity.rangeUnderflow)).toBeTruthy();
  await cut.fill("50");await page.getByRole("button",{name:"Comparar y buscar alternativa",exact:true}).click();
  await expect(page.locator(".form-error")).toContainText("No se ha podido guardar");
  await expect(page.locator(".form-error")).toBeFocused();await expect(cut).toHaveValue("50");
  broken=false;
  await page.getByLabel("Mercado global").selectOption("m01");
  await page.getByRole("button",{name:"Comparar y buscar alternativa",exact:true}).click();
  await expect(page.locator(".form-error")).toContainText("La comparación es nacional");
  await page.getByLabel("Mercado global").selectOption("");
  await page.getByText("Restricciones de búsqueda y límites por canal",{exact:true}).click();
  await page.getByLabel("Techo total de medios (€)",{exact:false}).fill("0");
  await page.getByRole("button",{name:"Comparar y buscar alternativa",exact:true}).click();
  await expect(page).toHaveURL(/ejecucion=ejec-/);
  await expect(page.getByRole("heading",{name:"Revisar las restricciones",exact:true})).toBeVisible();
  await expect(page.getByTestId("delta-optimizacion")).toHaveCount(0);
  const id=new URL(page.url()).searchParams.get("ejecucion")!;
  expect((await (await request.get(`/api/v1/escenarios/ejecuciones/${id}`)).json()).resultado.optimizacion.mejor).toBeNull();
});

test("escenarios: diseño y resultado visuales accesibles en cuatro tamaños",async({page,request})=>{
  test.setTimeout(180_000);
  const {s}=await propuesta(request,"visual");
  const dir=path.resolve("../artifacts/qa");await mkdir(dir,{recursive:true});
  const sizes=[{width:1440,height:900},{width:1920,height:1080},{width:1280,height:720},{width:390,height:844}];
  async function capture(label:string){for(const size of sizes){
    await page.setViewportSize(size);await page.evaluate(()=>document.fonts.ready);
    await expect.poll(()=>page.locator(".scenario-workspace img").evaluateAll(imgs=>imgs.length>0&&imgs.every(el=>(el as HTMLImageElement).complete&&(el as HTMLImageElement).naturalWidth>0))).toBeTruthy();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth)).toBeFalsy();
    await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(dir,`escenarios-${label}-${size.width}.png`),fullPage:true});
    const result=await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze();
    expect(result.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
  }}
  await page.goto(`/escenarios?seleccion=${s.id}`);
  await expect(page.getByRole("heading",{name:"Preparar comparación",exact:true})).toBeVisible();
  await capture("diseno");
  const respuesta=await request.post("/api/v1/escenarios/ejecutar",{data:{nombre:`QA visual resultado ${Date.now()}`,seleccion_creativa_id:s.id,coste_produccion:120}});
  expect(respuesta.ok()).toBeTruthy();const d:ScenarioExecution=await respuesta.json();
  await page.goto(`/escenarios?ejecucion=${d.id}`);
  await expect(page.locator(".scenario-waterfall canvas")).toHaveCount(1);
  await capture("resultado");
  await page.goto("/medicion");
  await page.getByLabel("Canal del modelo",{exact:true}).selectOption("youtube");
  await page.getByRole("link",{name:"Comparar este canal en escenarios",exact:true}).click();
  await expect(page).toHaveURL(/canal=youtube/);
  await expect(page.getByLabel("Canal de reinversión",{exact:false})).toHaveValue("youtube");
});
