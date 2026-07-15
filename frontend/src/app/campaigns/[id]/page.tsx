import { CampaignRecord } from "@/components/CampaignRecord";
import { PageIntro } from "@/components/PageIntro";
export default async function CampaignPage({params}:{params:Promise<{id:string}>}){const{id}=await params;return <main><PageIntro kicker={`Campaign ${id}`} title="LIVE CAMPAIGN RECORD." copy="Read the stored terms, role addresses, evidence, audit result, and settlement state directly from the selected contract."/><CampaignRecord campaignId={id}/></main>}
