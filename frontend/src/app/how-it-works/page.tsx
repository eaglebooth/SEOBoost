import { PageIntro } from "@/components/PageIntro";
import { Reveal } from "@/components/Reveal";

const stages = [
  ["Client funds", "create_campaign", "The connected client becomes the immutable campaign owner. gl.message.value becomes the reward; no typed reward number can fake custody."],
  ["Agency proves", "submit_evidence", "Only the recorded agency can submit evidence. The article must match the locked domain and independent sources must use approved provider hosts."],
  ["Validators judge", "audit_campaign", "web.render reads all four sources and exec_prompt evaluates rank, duration, depth, stability, conversion value, and black-hat risk."],
  ["Contract settles", "release_reward / refund_reward", "Approval transfers GEN to the agency. Rejection or an expired evidence window lets only the client recover the escrow."],
];

export default function HowItWorks() {
  return <main><PageIntro back="/" kicker="Protocol guide" title="FROM FUNDED TERMS TO FINAL SETTLEMENT." copy="The UI follows the same guarded state machine as the contract, with no simulated campaigns or payouts."/><section className="content-band"><div className="shell timeline">{stages.map(([title,fn,copy],index)=><Reveal className="timeline-row" key={fn}><b>{String(index+1).padStart(2,"0")}</b><div><span>{fn}</span><h2>{title}</h2><p>{copy}</p></div></Reveal>)}</div></section></main>;
}
