import Link from "next/link";
import { ArrowRight, BarChart3, FileSearch, LockKeyhole, SearchCheck, ShieldCheck } from "lucide-react";
import { Reveal } from "@/components/Reveal";

const steps = [
  { icon: LockKeyhole, title: "Fund real escrow", copy: "The client creates a campaign from their wallet and locks the exact GEN reward inside the contract." },
  { icon: FileSearch, title: "Constrain evidence", copy: "The agency submits the target-domain article plus independent reports from approved search and SEO providers." },
  { icon: SearchCheck, title: "Reach consensus", copy: "GenLayer validators compare rank durability, content depth, white-hat quality, and black-hat risk." },
  { icon: BarChart3, title: "Settle on-chain", copy: "An approved campaign pays the recorded agency. A rejected or expired campaign refunds the recorded client." },
];

export default function Home() {
  return <main>
    <section className="hero">
      <Reveal className="trust-badge"><ShieldCheck size={18} /> Real white-hat SEO escrow on GenLayer</Reveal>
      <Reveal><h1>Pay for rankings that survive scrutiny.</h1></Reveal>
      <Reveal><p>SEOBoost locks native GEN, reads independent web evidence, and releases funds only after a comparative AI jury confirms durable, clean SEO performance.</p></Reveal>
      <Reveal className="hero-actions"><Link className="primary-action" href="/campaigns/new">Create funded campaign <ArrowRight size={18} /></Link><Link className="dark-action" href="/how-it-works">Review the protocol</Link></Reveal>
      <div className="signal-stage" aria-hidden="true"><div className="corner tl"/><div className="corner tr"/><div className="corner bl"/><div className="corner br"/><div className="mesh">{Array.from({length:18}).map((_,index)=><i key={index}/>)}</div><div className="serp-globe"><span/><span/><span/></div><div className="signal-card card-left"><FileSearch size={18}/>Trusted evidence</div><div className="signal-card card-right"><ShieldCheck size={18}/>Payable custody</div></div>
    </section>
    <section className="content-band"><div className="shell"><Reveal className="section-heading"><span className="eyebrow">Four verifiable stages</span><h2>One campaign. One responsibility per page.</h2><p>Every action maps directly to a public function in the deployed Intelligent Contract.</p></Reveal><div className="feature-grid">{steps.map(({icon:Icon,title,copy},index)=><Reveal className="feature-card" key={title}><span>0{index+1}</span><Icon size={24}/><h3>{title}</h3><p>{copy}</p></Reveal>)}</div></div></section>
  </main>;
}
