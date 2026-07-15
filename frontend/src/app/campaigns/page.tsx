import { CampaignRegistry } from "@/components/CampaignRegistry";
import { PageIntro } from "@/components/PageIntro";
export default function Campaigns(){return <main><PageIntro back="/" kicker="On-chain registry" title="CAMPAIGNS FROM THE SELECTED DEPLOYMENT." copy="The registry reads six records per page to keep RPC work bounded as the protocol grows."/><CampaignRegistry/></main>}
