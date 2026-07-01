# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import typing
import json


class SEOBoost(gl.Contract):
    campaign_count: u256
    escrow_balance: u256
    escrow_released: u256

    campaign_clients: TreeMap[u256, str]
    campaign_agencies: TreeMap[u256, str]
    campaign_keywords: TreeMap[u256, str]
    campaign_target_ranks: TreeMap[u256, u256]
    campaign_rewards: TreeMap[u256, u256]
    campaign_hold_days: TreeMap[u256, u256]
    campaign_statuses: TreeMap[u256, str]

    campaign_article_urls: TreeMap[u256, str]
    campaign_serp_urls: TreeMap[u256, str]
    campaign_analytics_urls: TreeMap[u256, str]
    campaign_backlink_urls: TreeMap[u256, str]

    campaign_decisions: TreeMap[u256, str]
    campaign_rank_positions: TreeMap[u256, u256]
    campaign_observed_days: TreeMap[u256, u256]
    campaign_depth_scores: TreeMap[u256, u256]
    campaign_whitehat_scores: TreeMap[u256, u256]
    campaign_stability_scores: TreeMap[u256, u256]
    campaign_conversion_scores: TreeMap[u256, u256]
    campaign_blackhat_risk_scores: TreeMap[u256, u256]
    campaign_ai_reports: TreeMap[u256, str]

    def __init__(self):
        self.campaign_count = u256(0)
        self.escrow_balance = u256(0)
        self.escrow_released = u256(0)

    @gl.public.write
    def create_campaign(
        self,
        client_wallet: str,
        agency_wallet: str,
        keyword: str,
        target_rank: u256,
        reward: u256,
        hold_days: u256,
    ) -> typing.Any:
        if len(client_wallet) == 0:
            return "EMPTY_CLIENT"
        if len(agency_wallet) == 0:
            return "EMPTY_AGENCY"
        if len(keyword) == 0:
            return "EMPTY_KEYWORD"
        if target_rank == u256(0) or target_rank > u256(100):
            return "BAD_TARGET_RANK"
        if reward == u256(0):
            return "ZERO_REWARD"
        if hold_days < u256(15):
            return "HOLD_TOO_SHORT"

        campaign_id = self.campaign_count
        self.campaign_clients[campaign_id] = client_wallet
        self.campaign_agencies[campaign_id] = agency_wallet
        self.campaign_keywords[campaign_id] = keyword
        self.campaign_target_ranks[campaign_id] = target_rank
        self.campaign_rewards[campaign_id] = reward
        self.campaign_hold_days[campaign_id] = hold_days
        self.campaign_statuses[campaign_id] = "CREATED"
        self.campaign_article_urls[campaign_id] = ""
        self.campaign_serp_urls[campaign_id] = ""
        self.campaign_analytics_urls[campaign_id] = ""
        self.campaign_backlink_urls[campaign_id] = ""
        self.campaign_decisions[campaign_id] = "PENDING"
        self.campaign_rank_positions[campaign_id] = u256(0)
        self.campaign_observed_days[campaign_id] = u256(0)
        self.campaign_depth_scores[campaign_id] = u256(0)
        self.campaign_whitehat_scores[campaign_id] = u256(0)
        self.campaign_stability_scores[campaign_id] = u256(0)
        self.campaign_conversion_scores[campaign_id] = u256(0)
        self.campaign_blackhat_risk_scores[campaign_id] = u256(0)
        self.campaign_ai_reports[campaign_id] = ""
        self.escrow_balance = self.escrow_balance + reward
        self.campaign_count = campaign_id + u256(1)
        return campaign_id

    @gl.public.write
    def submit_evidence(
        self,
        campaign_id: u256,
        article_url: str,
        serp_url: str,
        analytics_url: str,
        backlink_url: str,
    ) -> str:
        if campaign_id >= self.campaign_count:
            return "CAMPAIGN_NOT_FOUND"
        if self.campaign_statuses[campaign_id] != "CREATED":
            return "CAMPAIGN_NOT_OPEN"
        if self._is_url(article_url) == u256(0):
            return "BAD_ARTICLE_URL"
        if self._is_url(serp_url) == u256(0):
            return "BAD_SERP_URL"
        if self._is_url(analytics_url) == u256(0):
            return "BAD_ANALYTICS_URL"
        if self._is_url(backlink_url) == u256(0):
            return "BAD_BACKLINK_URL"

        self.campaign_article_urls[campaign_id] = article_url
        self.campaign_serp_urls[campaign_id] = serp_url
        self.campaign_analytics_urls[campaign_id] = analytics_url
        self.campaign_backlink_urls[campaign_id] = backlink_url
        self.campaign_statuses[campaign_id] = "EVIDENCE_READY"
        return "EVIDENCE_READY"

    @gl.public.write
    def audit_campaign(self, campaign_id: u256) -> typing.Any:
        if campaign_id >= self.campaign_count:
            return "CAMPAIGN_NOT_FOUND"
        if self.campaign_statuses[campaign_id] != "EVIDENCE_READY":
            return "EVIDENCE_NOT_READY"

        keyword = self.campaign_keywords[campaign_id]
        target_rank = self.campaign_target_ranks[campaign_id]
        hold_days = self.campaign_hold_days[campaign_id]
        article_url = self.campaign_article_urls[campaign_id]
        serp_url = self.campaign_serp_urls[campaign_id]
        analytics_url = self.campaign_analytics_urls[campaign_id]
        backlink_url = self.campaign_backlink_urls[campaign_id]

        def run_audit() -> str:
            article = self._render_evidence(article_url)
            serp = self._render_evidence(serp_url)
            analytics = self._render_evidence(analytics_url)
            backlinks = self._render_evidence(backlink_url)
            prompt = f"""You are SEOBoost, an on-chain white-hat SEO escrow auditor.

Campaign:
- target keyword: {keyword}
- target_google_rank: {target_rank}
- required_stable_days: {hold_days}

Evidence read on-chain:
ARTICLE PAGE:
{article}

SERP SNAPSHOT / GOOGLE RESULT EVIDENCE:
{serp}

RANK TRACKING / ANALYTICS EVIDENCE:
{analytics}

BACKLINK / SOURCE QUALITY EVIDENCE:
{backlinks}

Audit the agency's work. Pay only for durable, white-hat SEO.

Scoring:
- rank_position: current rank where 1 is best, 0 if unknown.
- observed_days: number of days the page appears to have held the target range.
- depth_score 0-100: topical depth, expertise, originality, helpfulness.
- whitehat_score 0-100: clean SEO practices, natural links, no stuffing, no cloaking.
- stability_score 0-100: rank appears stable rather than short-lived manipulation.
- conversion_value_score 0-100: page is useful for actual buyers, not empty traffic.
- blackhat_risk_score 0-100: higher means spam, PBN, keyword stuffing, cloaking, fake traffic, or scraped AI fluff.

Decision rules:
- APPROVED if rank_position is >0 and <= target_google_rank, observed_days >= required_stable_days, depth_score >= 70, whitehat_score >= 75, stability_score >= 70, and blackhat_risk_score <= 30.
- NEEDS_REVIEW if evidence is missing, ambiguous, rank is close but stability is unclear, or any source fails to render.
- REJECTED if rank misses target, content is thin/AI fluff, blackhat risk is high, or observed days are below requirement.

Respond with ONLY this JSON, no markdown:
{{
  "decision": "APPROVED|NEEDS_REVIEW|REJECTED",
  "rank_position": 0,
  "observed_days": 0,
  "depth_score": 0,
  "whitehat_score": 0,
  "stability_score": 0,
  "conversion_value_score": 0,
  "blackhat_risk_score": 0,
  "reason": "one concise sentence citing the evidence"
}}"""
            return gl.nondet.exec_prompt(prompt)

        principle = """Two SEOBoost audit outputs are equivalent when they agree on the substantive payout outcome:
the same decision label among APPROVED, NEEDS_REVIEW, and REJECTED; the same conclusion about whether the page met
the target rank for the required hold period; similar score bands for content depth, white-hat quality, rank stability,
conversion value, and black-hat risk; and the same material reason for paying or withholding escrow. Ignore JSON key
order, exact phrasing, punctuation, or harmless wording differences. Reject equivalence if one output pays while the
other withholds, if the rank/hold requirement conclusion differs, or if black-hat risk changes the payout outcome."""

        consensus = gl.eq_principle.prompt_comparative(run_audit, principle)
        parsed = self._parse_audit(consensus)

        decision = parsed["decision"]
        rank_position = u256(int(parsed["rank_position"]))
        observed_days = u256(int(parsed["observed_days"]))
        depth_score = u256(int(parsed["depth_score"]))
        whitehat_score = u256(int(parsed["whitehat_score"]))
        stability_score = u256(int(parsed["stability_score"]))
        conversion_score = u256(int(parsed["conversion_value_score"]))
        blackhat_risk = u256(int(parsed["blackhat_risk_score"]))
        reason = str(parsed["reason"])[:900]

        if decision == "APPROVED":
            if rank_position == u256(0) or rank_position > target_rank:
                decision = "NEEDS_REVIEW"
            if observed_days < hold_days:
                decision = "NEEDS_REVIEW"
            if depth_score < u256(70) or whitehat_score < u256(75):
                decision = "NEEDS_REVIEW"
            if stability_score < u256(70) or blackhat_risk > u256(30):
                decision = "NEEDS_REVIEW"

        self.campaign_decisions[campaign_id] = decision
        self.campaign_rank_positions[campaign_id] = rank_position
        self.campaign_observed_days[campaign_id] = observed_days
        self.campaign_depth_scores[campaign_id] = depth_score
        self.campaign_whitehat_scores[campaign_id] = whitehat_score
        self.campaign_stability_scores[campaign_id] = stability_score
        self.campaign_conversion_scores[campaign_id] = conversion_score
        self.campaign_blackhat_risk_scores[campaign_id] = blackhat_risk
        self.campaign_ai_reports[campaign_id] = reason
        self.campaign_statuses[campaign_id] = decision
        return self.get_audit(campaign_id)

    @gl.public.write
    def release_reward(self, campaign_id: u256) -> str:
        if campaign_id >= self.campaign_count:
            return "CAMPAIGN_NOT_FOUND"
        if self.campaign_statuses[campaign_id] != "APPROVED":
            return "NOT_APPROVED"

        reward = self.campaign_rewards[campaign_id]
        if reward == u256(0):
            return "ZERO_REWARD"
        if reward > self.escrow_balance:
            return "INSUFFICIENT_ESCROW"

        self.escrow_balance = self.escrow_balance - reward
        self.escrow_released = self.escrow_released + reward
        self.campaign_statuses[campaign_id] = "PAID"
        return "PAID"

    @gl.public.view
    def get_campaign_count(self) -> u256:
        return self.campaign_count

    @gl.public.view
    def get_escrow_state(self) -> str:
        return json.dumps(
            {
                "balance": int(self.escrow_balance),
                "campaign_count": int(self.campaign_count),
                "released": int(self.escrow_released),
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @gl.public.view
    def get_campaign(self, campaign_id: u256) -> str:
        if campaign_id >= self.campaign_count:
            return "CAMPAIGN_NOT_FOUND"
        return json.dumps(
            {
                "agency": self.campaign_agencies[campaign_id],
                "analytics_url": self.campaign_analytics_urls[campaign_id],
                "article_url": self.campaign_article_urls[campaign_id],
                "backlink_url": self.campaign_backlink_urls[campaign_id],
                "client": self.campaign_clients[campaign_id],
                "decision": self.campaign_decisions[campaign_id],
                "hold_days": int(self.campaign_hold_days[campaign_id]),
                "keyword": self.campaign_keywords[campaign_id],
                "reward": int(self.campaign_rewards[campaign_id]),
                "serp_url": self.campaign_serp_urls[campaign_id],
                "status": self.campaign_statuses[campaign_id],
                "target_rank": int(self.campaign_target_ranks[campaign_id]),
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @gl.public.view
    def get_audit(self, campaign_id: u256) -> str:
        if campaign_id >= self.campaign_count:
            return "CAMPAIGN_NOT_FOUND"
        return json.dumps(
            {
                "blackhat_risk_score": int(self.campaign_blackhat_risk_scores[campaign_id]),
                "conversion_value_score": int(self.campaign_conversion_scores[campaign_id]),
                "decision": self.campaign_decisions[campaign_id],
                "depth_score": int(self.campaign_depth_scores[campaign_id]),
                "observed_days": int(self.campaign_observed_days[campaign_id]),
                "rank_position": int(self.campaign_rank_positions[campaign_id]),
                "reason": self.campaign_ai_reports[campaign_id],
                "stability_score": int(self.campaign_stability_scores[campaign_id]),
                "status": self.campaign_statuses[campaign_id],
                "whitehat_score": int(self.campaign_whitehat_scores[campaign_id]),
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    def _is_url(self, value: str) -> u256:
        if len(value) < 8:
            return u256(0)
        if value[:7] == "http://":
            return u256(1)
        if value[:8] == "https://":
            return u256(1)
        return u256(0)

    def _render_evidence(self, url: str) -> str:
        try:
            response = gl.nondet.web.render(url, media_type="html")
            return str(response)[:3600]
        except Exception:
            return "WEB_RENDER_FAILED"

    def _clamp_score(self, value: typing.Any):
        number = int(value)
        if number < 0:
            return 0
        if number > 100:
            return 100
        return number

    def _parse_audit(self, raw: str) -> typing.Any:
        try:
            data = json.loads(raw)
        except Exception:
            return {
                "blackhat_risk_score": 100,
                "conversion_value_score": 0,
                "decision": "NEEDS_REVIEW",
                "depth_score": 0,
                "observed_days": 0,
                "rank_position": 0,
                "reason": "AI returned malformed JSON; manual SEO review required.",
                "stability_score": 0,
                "whitehat_score": 0,
            }

        decision = str(data.get("decision", "NEEDS_REVIEW"))
        if decision != "APPROVED" and decision != "REJECTED":
            decision = "NEEDS_REVIEW"

        rank_position = int(data.get("rank_position", 0))
        if rank_position < 0:
            rank_position = 0
        if rank_position > 100:
            rank_position = 100

        observed_days = int(data.get("observed_days", 0))
        if observed_days < 0:
            observed_days = 0
        if observed_days > 365:
            observed_days = 365

        return {
            "blackhat_risk_score": self._clamp_score(data.get("blackhat_risk_score", 100)),
            "conversion_value_score": self._clamp_score(data.get("conversion_value_score", 0)),
            "decision": decision,
            "depth_score": self._clamp_score(data.get("depth_score", 0)),
            "observed_days": observed_days,
            "rank_position": rank_position,
            "reason": str(data.get("reason", "No reason provided.")),
            "stability_score": self._clamp_score(data.get("stability_score", 0)),
            "whitehat_score": self._clamp_score(data.get("whitehat_score", 0)),
        }
