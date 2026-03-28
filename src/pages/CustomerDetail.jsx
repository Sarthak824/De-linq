import { useParams } from "react-router-dom";

export default function CustomerDetail() {
  const { id } = useParams();

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">
        Customer Detail: {id || 'Unknown'}
      </h1>
      <div className="p-8 border border-white/5 bg-slate-900/50 backdrop-blur-md rounded-2xl flex items-center justify-center min-h-[400px]">
        <p className="text-slate-400">Customer Detail placeholder content area</p>
      </div>
    </div>
  );
}
