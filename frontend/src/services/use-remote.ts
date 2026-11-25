"use client";
import { useEffect, useState } from "react";
import { api } from "@/services/api";

export function useRemote<T>(path:string) {
  const [retry,setRetry]=useState(0);
  const [state,setState]=useState<{key:string;data?:T;error?:string}>({key:""});
  const key=`${path}#${retry}`;
  useEffect(()=>{
    const abort=new AbortController();
    api<T>(path,abort.signal).then(data=>setState({key,data})).catch(error=>{
      if(!abort.signal.aborted)setState({key,error:error.message});
    });
    return ()=>abort.abort();
  },[path,key]);
  return {data:state.key===key?state.data:undefined,error:state.key===key?state.error:undefined,retry:()=>setRetry(v=>v+1)};
}
