import { Workspace } from "@/components/workspace";
import { Suspense } from "react";
import { Loading } from "@/components/ui";
import type { Metadata } from "next";

export async function generateMetadata({params}:{params:Promise<{ruta?:string[]}>}):Promise<Metadata> {
  const route=(await params).ruta?.join("/")||"";
  const titles:Record<string,string>={"":"Centro de decisiones",medicion:"Medición de medios","one-search":"One Search",creatividad:"Inteligencia creativa",experimentos:"Laboratorio de experimentos",escenarios:"Laboratorio de escenarios",fiabilidad:"Fiabilidad del dato",ajustes:"Configuración"};
  return {title:`${titles[route]||"Página no encontrada"} · MARGIA`};
}

export default function Page() { return <Suspense fallback={<Loading/>}><Workspace /></Suspense>; }
