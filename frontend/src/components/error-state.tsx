import { Database } from "lucide-react";
export function ErrorState({message,retry}:{message:string;retry:()=>void}) {
  return <div className="error-state" role="alert"><Database size={26}/><h2>No se han podido cargar los datos</h2><p>{message}</p><button type="button" className="button secondary" onClick={retry}>Reintentar</button></div>;
}
