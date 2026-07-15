import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export function PageIntro({ kicker, title, copy, back = "/campaigns" }: { kicker: string; title: string; copy: string; back?: string }) {
  return <section className="page-intro"><div className="shell">
    <Link className="back-link" href={back}><ArrowLeft size={16} />Back</Link>
    <span className="eyebrow">{kicker}</span>
    <h1>{title}</h1>
    <p>{copy}</p>
  </div></section>;
}
