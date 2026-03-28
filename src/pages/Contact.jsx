import React from 'react';
import { Mail, Phone, MapPin, ShieldCheck, Globe, MessageSquare, Headphones, Users } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Contact() {
  const contacts = [
    { name: "Siddharth V.", role: "Head of Risk Systems", phone: "+91 98765 43210", email: "siddharth.v@delinq.ai" },
    { name: "Ananya R.", role: "Lead Solutions Architect", phone: "+91 91234 56789", email: "ananya.r@delinq.ai" },
    { name: "Vikram M.", role: "Director of Data Integrity", phone: "+91 90000 11111", email: "vikram.m@delinq.ai" }
  ];

  return (
    <div className="space-y-10 animate-in fade-in duration-700 pb-12 px-4">
      {/* Header Section */}
      <section className="relative overflow-hidden p-12 rounded-[2rem] bg-slate-900/60 border border-white/5 backdrop-blur-3xl shadow-2xl">
        <div className="absolute top-0 right-0 p-8 opacity-10">
          <Globe className="w-64 h-64 text-cyan-400 rotate-12" />
        </div>
        
        <div className="relative z-10 max-w-2xl">
          <motion.div 
            initial={{ opacity: 0, x: -20 }} 
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3 text-cyan-400 font-black uppercase tracking-widest text-xs mb-6"
          >
            <ShieldCheck className="w-5 h-5" />
            Global Support Presence
          </motion.div>
          <motion.h1 
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-6xl font-black text-white mb-6 leading-tight"
          >
            Get in touch with the <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">DelinqAI</span> Team
          </motion.h1>
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-lg text-slate-400 leading-relaxed"
          >
            <p>
              DelinqAI uses a <span className="text-cyan-400 font-bold">Behavioral-First</span> intervention strategy. Instead of waiting for a missed payment (DPD), we monitor 84+ real-time signals including salary fragmentation, P2P dependency, and spending volatility.
            </p>
          </motion.div>
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Support Tiers */}
        <div className="lg:col-span-2 space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ContactCard 
              icon={Headphones} 
              title="Enterprise Support" 
              desc="Dedicated support for high-volume banking partners. Available 24/7."
              action="primary-support@delinq.ai"
            />
            <ContactCard 
              icon={MessageSquare} 
              title="Solutions Consulting" 
              desc="Custom integration assistance for newer liquidity stress modules."
              action="solutions@delinq.ai"
            />
          </div>

          <div className="bg-slate-900/40 backdrop-blur-md p-8 rounded-[2rem] border border-white/5">
            <h2 className="text-xl font-bold text-white mb-8 flex items-center gap-3">
              <Users className="w-6 h-6 text-cyan-400" />
              Key Support Contacts
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {contacts.map((c, i) => (
                <div key={i} className="p-6 bg-white/5 rounded-2xl border border-white/10 hover:border-cyan-500/30 transition-all group">
                  <p className="font-bold text-white mb-1 group-hover:text-cyan-400 transition-colors uppercase tracking-tight">{c.name}</p>
                  <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-4">{c.role}</p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <Phone className="w-3 h-3" /> {c.phone}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <Mail className="w-3 h-3" /> {c.email}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Office Info */}
        <div className="space-y-8">
          <div className="bg-cyan-500/10 backdrop-blur-md p-8 rounded-[2rem] border border-cyan-500/20 shadow-[0_0_30px_rgba(6,182,212,0.05)]">
            <MapPin className="w-8 h-8 text-cyan-400 mb-6" />
            <h3 className="text-xl font-bold text-white mb-4">India Headquarters</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Block 4, Tech Innovation Hub<br />
              Varthur Road, Whitefield<br />
              Bengaluru, Karnataka 560066
            </p>
          </div>

          <div className="bg-slate-900/40 backdrop-blur-md p-8 rounded-[2rem] border border-white/5">
            <h3 className="text-lg font-bold text-white mb-4">Quick Links</h3>
            <div className="space-y-4">
              <button className="w-full py-4 px-6 bg-white/5 border border-white/10 rounded-2xl text-left text-sm text-slate-300 hover:bg-white/10 transition-colors flex justify-between items-center group">
                Support Documentation <Globe className="w-4 h-4 opacity-30 group-hover:opacity-100 transition-opacity" />
              </button>
              <button className="w-full py-4 px-6 bg-white/5 border border-white/10 rounded-2xl text-left text-sm text-slate-300 hover:bg-white/10 transition-colors flex justify-between items-center group">
                Developer API Specs <ShieldCheck className="w-4 h-4 opacity-30 group-hover:opacity-100 transition-opacity" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ContactCard({ icon: Icon, title, desc, action }) {
  return (
    <div className="bg-slate-900/40 backdrop-blur-md p-8 rounded-[2rem] border border-white/5 hover:border-white/10 transition-all flex flex-col items-start gap-4 shadow-xl">
      <div className="p-4 bg-cyan-500/10 rounded-2xl border border-cyan-500/10">
        <Icon className="w-6 h-6 text-cyan-400" />
      </div>
      <div>
        <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
        <p className="text-sm text-slate-500 leading-relaxed mb-6">{desc}</p>
        <p className="text-cyan-400 font-mono text-sm underline underline-offset-4 cursor-pointer hover:text-cyan-300 transition-colors">{action}</p>
      </div>
    </div>
  );
}
