"use client";
import { useEffect, useRef } from "react";
import * as echarts from "echarts/core";
import { LineChart, BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent, AriaComponent, MarkLineComponent, MarkAreaComponent, LegendComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import type { EChartsCoreOption } from "echarts/core";

echarts.use([LineChart, BarChart, GridComponent, TooltipComponent, AriaComponent, MarkLineComponent, MarkAreaComponent, LegendComponent, CanvasRenderer]);

export function Chart({option, label, className=""}:{option:EChartsCoreOption; label:string; className?:string}) {
  const ref=useRef<HTMLDivElement>(null);
  useEffect(()=>{
    if(!ref.current) return;
    const instance=echarts.init(ref.current, undefined, {renderer:"canvas"});
    instance.setOption({...option, animation:false, textStyle:{fontFamily:"Inter Variable, sans-serif"}, aria:{enabled:true, label:{description:label}}});
    const observer = new ResizeObserver(()=>instance.resize());
    observer.observe(ref.current);
    return ()=>{observer.disconnect(); instance.dispose();};
  },[option,label]);
  return <div className={`chart ${className}`} ref={ref} role="img" aria-label={label} />;
}
