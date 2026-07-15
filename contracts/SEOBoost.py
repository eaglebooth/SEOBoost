# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import typing
import json


@gl.evm.contract_interface
class _Recipient:
    class View:
        pass

    class Write:
        pass


class SEOBoost(gl.Contract):
    campaign_count: u256
    escrow_balance: u256
    escrow_released: u256
    escrow_refunded: u256

    campaign_clients: TreeMap[u256, str]
    campaign_agencies: TreeMap[u256, str]
    campaign_target_domains: TreeMap[u256, str]
    campaign_keywords: TreeMap[u256, str]
    campaign_target_ranks: TreeMap[u256, u256]
    campaign_rewards: TreeMap[u256, u256]
    campaign_hold_days: TreeMap[u256, u256]
    campaign_created_times: TreeMap[u256, u256]
    campaign_evidence_deadlines: TreeMap[u256, u256]
    campaign_revision_deadlines: TreeMap[u256, u256]
    campaign_evidence_revisions: TreeMap[u256, u256]
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
        self.escrow_refunded = u256(0)

    @gl.public.write.payable
    def create_campaign(
        self,
        agency_wallet: str,
        target_domain: str,
        keyword: str,
        target_rank: u256,
        hold_days: u256,
        evidence_window_days: u256,
    ) -> typing.Any:
        if self._valid_wallet(agency_wallet) == u256(0):
            raise gl.vm.UserError("INVALID_AGENCY_WALLET")
        if self._valid_domain(target_domain) == u256(0):
            raise gl.vm.UserError("INVALID_TARGET_DOMAIN")
        if len(keyword) == 0 or len(keyword) > 160:
            raise gl.vm.UserError("INVALID_KEYWORD")
        if target_rank == u256(0) or target_rank > u256(100):
            raise gl.vm.UserError("BAD_TARGET_RANK")
        if hold_days < u256(15) or hold_days > u256(90):
            raise gl.vm.UserError("INVALID_HOLD_PERIOD")
        if evidence_window_days == u256(0) or evidence_window_days > u256(60):
            raise gl.vm.UserError("INVALID_EVIDENCE_WINDOW")

        reward = gl.message.value
        if reward == u256(0):
            raise gl.vm.UserError("ZERO_REWARD")

        campaign_id = self.campaign_count
        created_at = gl.get_block_timestamp()
        self.campaign_clients[campaign_id] = gl.message.sender_address.as_hex.lower()
        self.campaign_agencies[campaign_id] = agency_wallet.lower()
        self.campaign_target_domains[campaign_id] = target_domain.lower()
        self.campaign_keywords[campaign_id] = keyword
        self.campaign_target_ranks[campaign_id] = target_rank
        self.campaign_rewards[campaign_id] = reward
        self.campaign_hold_days[campaign_id] = hold_days
        self.campaign_created_times[campaign_id] = created_at
        self.campaign_evidence_deadlines[campaign_id] = created_at + evidence_window_days * u256(86400)
        self.campaign_revision_deadlines[campaign_id] = u256(0)
        self.campaign_evidence_revisions[campaign_id] = u256(0)
        self.campaign_statuses[campaign_id] = "FUNDED"
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
            raise gl.vm.UserError("CAMPAIGN_NOT_FOUND")
        if self.campaign_agencies[campaign_id] != gl.message.sender_address.as_hex.lower():
            raise gl.vm.UserError("AGENCY_ONLY")

        status = self.campaign_statuses[campaign_id]
        now = gl.get_block_timestamp()
        if status == "FUNDED":
            if now > self.campaign_evidence_deadlines[campaign_id]:
                raise gl.vm.UserError("EVIDENCE_WINDOW_CLOSED")
        elif status == "NEEDS_REVIEW":
            if self.campaign_evidence_revisions[campaign_id] != u256(0):
                raise gl.vm.UserError("REVISION_ALREADY_USED")
            if now > self.campaign_revision_deadlines[campaign_id]:
                raise gl.vm.UserError("REVISION_WINDOW_CLOSED")
            self.campaign_evidence_revisions[campaign_id] = u256(1)
        else:
            raise gl.vm.UserError("CAMPAIGN_NOT_OPEN")

        domain = self.campaign_target_domains[campaign_id]
        if self._article_matches_domain(article_url, domain) == u256(0):
            raise gl.vm.UserError("ARTICLE_DOMAIN_MISMATCH")
        if self._trusted_serp(serp_url) == u256(0):
            raise gl.vm.UserError("UNTRUSTED_SERP_SOURCE")
        if self._trusted_analytics(analytics_url) == u256(0):
            raise gl.vm.UserError("UNTRUSTED_ANALYTICS_SOURCE")
        if self._trusted_backlink(backlink_url) == u256(0):
            raise gl.vm.UserError("UNTRUSTED_BACKLINK_SOURCE")

        self.campaign_article_urls[campaign_id] = article_url
        self.campaign_serp_urls[campaign_id] = serp_url
        self.campaign_analytics_urls[campaign_id] = analytics_url
        self.campaign_backlink_urls[campaign_id] = backlink_url
        self.campaign_statuses[campaign_id] = "EVIDENCE_READY"
        self.campaign_decisions[campaign_id] = "PENDING"
        return "EVIDENCE_READY"

    @gl.public.write
    def audit_campaign(self, campaign_id: u256) -> typing.Any:
        if campaign_id >= self.campaign_count:
            raise gl.vm.UserError("CAMPAIGN_NOT_FOUND")
        if self.campaign_statuses[campaign_id] != "EVIDENCE_READY":
            raise gl.vm.UserError("EVIDENCE_NOT_READY")

        target_domain = self.campaign_target_domains[campaign_id]
        keyword = self.campaign_keywords[campaign_id]
        target_rank = self.campaign_target_ranks[campaign_id]
        hold_days = self.campaign_hold_days[campaign_id]
        article_url = self.campaign_article_urls[campaign_id]
        serp_url = self.campaign_serp_urls[campaign_id]
        analytics_url = self.campaign_analytics_urls[campaign_id]
        backlink_url = self.campaign_backlink_urls[campaign_id]

        def run_audit() -> str:
            def render(url: str) -> str:
                try:
                    return str(gl.nondet.web.render(url, mode="html"))[:3200]
                except Exception:
                    return "WEB_RENDER_FAILED"

            article = render(article_url)
            serp = render(serp_url)
            analytics = render(analytics_url)
            backlinks = render(backlink_url)
            prompt = f"""You are SEOBoost, an on-chain white-hat SEO escrow jury.

Campaign terms locked by the client:
- target domain: {target_domain}
- target keyword: {keyword}
- target rank: {target_rank}
- required stable days: {hold_days}
- reward is fixed by the contract and must not be estimated by the jury

Evidence sources validated by the contract before this audit:
ARTICLE ON TARGET DOMAIN ({article_url}):
{article}

INDEPENDENT SEARCH RESULT ({serp_url}):
{serp}

TRUSTED RANK ANALYTICS ({analytics_url}):
{analytics}

TRUSTED BACKLINK REPORT ({backlink_url}):
{backlinks}

If any source says WEB_RENDER_FAILED, return NEEDS_REVIEW. Do not approve from the article alone.
Approve only when independent SERP and analytics evidence both prove the target rank and hold period.

Scoring:
- rank_position: 1 is best, 0 if not independently proven.
- observed_days: independently evidenced days at or above the target.
- depth_score 0-100: expertise, originality, usefulness, and topical depth.
- whitehat_score 0-100: natural optimization without stuffing or cloaking.
- stability_score 0-100: durable ranking rather than a short manipulation spike.
- conversion_value_score 0-100: usefulness to real prospective customers.
- blackhat_risk_score 0-100: spam, PBN, stuffing, cloaking, fake traffic, or scraped fluff.

Decision rules:
- APPROVED only if rank_position > 0 and <= {target_rank}, observed_days >= {hold_days}, depth_score >= 70,
  whitehat_score >= 75, stability_score >= 70, and blackhat_risk_score <= 30.
- NEEDS_REVIEW when trusted evidence is unreadable, incomplete, ambiguous, or conflicting.
- REJECTED when rank or hold terms fail, content is thin, or black-hat risk is material.

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
  "reason": "one concise sentence citing the decisive independent evidence"
}}"""
            return gl.nondet.exec_prompt(prompt)

        principle = """Two SEOBoost reviews are equivalent only when they agree on the substantive escrow outcome:
the same APPROVED, NEEDS_REVIEW, or REJECTED decision; the same conclusion about independently proven target rank
and hold duration; and similar score bands supporting that outcome. Ignore JSON key order and harmless wording
differences. Never treat an approval and a withholding/refund outcome as equivalent."""

        consensus = gl.eq_principle.prompt_comparative(run_audit, principle)
        parsed = self._parse_audit(consensus)
        decision = str(parsed["decision"])
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

        if decision == "NEEDS_REVIEW":
            if self.campaign_evidence_revisions[campaign_id] == u256(0):
                self.campaign_revision_deadlines[campaign_id] = gl.get_block_timestamp() + u256(604800)
            else:
                decision = "REJECTED"
                reason = "Independent evidence remained inconclusive after the permitted revision."

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
            raise gl.vm.UserError("CAMPAIGN_NOT_FOUND")
        if self.campaign_statuses[campaign_id] != "APPROVED":
            raise gl.vm.UserError("NOT_APPROVED")
        reward = self.campaign_rewards[campaign_id]
        if reward == u256(0) or reward > self.escrow_balance or reward > self.balance:
            raise gl.vm.UserError("ESCROW_BALANCE_MISMATCH")

        self.escrow_balance = self.escrow_balance - reward
        self.escrow_released = self.escrow_released + reward
        self.campaign_statuses[campaign_id] = "PAID"
        _Recipient(Address(self.campaign_agencies[campaign_id])).emit_transfer(value=reward)
        return "PAID"

    @gl.public.write
    def refund_reward(self, campaign_id: u256) -> str:
        if campaign_id >= self.campaign_count:
            raise gl.vm.UserError("CAMPAIGN_NOT_FOUND")
        if self.campaign_clients[campaign_id] != gl.message.sender_address.as_hex.lower():
            raise gl.vm.UserError("CLIENT_ONLY")
        status = self.campaign_statuses[campaign_id]
        refundable = status == "REJECTED"
        if status == "FUNDED" and gl.get_block_timestamp() > self.campaign_evidence_deadlines[campaign_id]:
            refundable = True
        if status == "NEEDS_REVIEW" and gl.get_block_timestamp() > self.campaign_revision_deadlines[campaign_id]:
            refundable = True
        if not refundable:
            raise gl.vm.UserError("NOT_REFUNDABLE")

        reward = self.campaign_rewards[campaign_id]
        if reward == u256(0) or reward > self.escrow_balance or reward > self.balance:
            raise gl.vm.UserError("ESCROW_BALANCE_MISMATCH")

        self.escrow_balance = self.escrow_balance - reward
        self.escrow_refunded = self.escrow_refunded + reward
        self.campaign_statuses[campaign_id] = "REFUNDED"
        _Recipient(Address(self.campaign_clients[campaign_id])).emit_transfer(value=reward)
        return "REFUNDED"

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
                "refunded": int(self.escrow_refunded),
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
                "created_at": int(self.campaign_created_times[campaign_id]),
                "decision": self.campaign_decisions[campaign_id],
                "evidence_deadline": int(self.campaign_evidence_deadlines[campaign_id]),
                "evidence_revisions": int(self.campaign_evidence_revisions[campaign_id]),
                "hold_days": int(self.campaign_hold_days[campaign_id]),
                "keyword": self.campaign_keywords[campaign_id],
                "revision_deadline": int(self.campaign_revision_deadlines[campaign_id]),
                "reward": int(self.campaign_rewards[campaign_id]),
                "serp_url": self.campaign_serp_urls[campaign_id],
                "status": self.campaign_statuses[campaign_id],
                "target_domain": self.campaign_target_domains[campaign_id],
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

    def _valid_wallet(self, value: str) -> u256:
        if len(value) != 42 or value[:2] != "0x":
            return u256(0)
        return u256(1)

    def _valid_domain(self, value: str) -> u256:
        if len(value) < 4 or len(value) > 253:
            return u256(0)
        if "." not in value or "/" in value or ":" in value or " " in value:
            return u256(0)
        return u256(1)

    def _article_matches_domain(self, url: str, domain: str) -> u256:
        normalized = url.lower()
        base = "https://" + domain.lower()
        if normalized == base or normalized[: len(base) + 1] == base + "/":
            return u256(1)
        return u256(0)

    def _trusted_serp(self, url: str) -> u256:
        value = url.lower()
        if value[:30] == "https://www.google.com/search?":
            return u256(1)
        if value[:28] == "https://www.bing.com/search?":
            return u256(1)
        return u256(0)

    def _trusted_analytics(self, url: str) -> u256:
        value = url.lower()
        if value[:26] == "https://search.google.com/":
            return u256(1)
        if value[:29] == "https://analytics.google.com/":
            return u256(1)
        if value[:24] == "https://www.semrush.com/":
            return u256(1)
        if value[:24] == "https://app.semrush.com/":
            return u256(1)
        if value[:23] == "https://app.ahrefs.com/":
            return u256(1)
        return u256(0)

    def _trusted_backlink(self, url: str) -> u256:
        value = url.lower()
        if value[:19] == "https://ahrefs.com/":
            return u256(1)
        if value[:23] == "https://app.ahrefs.com/":
            return u256(1)
        if value[:24] == "https://www.semrush.com/":
            return u256(1)
        if value[:24] == "https://app.semrush.com/":
            return u256(1)
        if value[:16] == "https://moz.com/":
            return u256(1)
        return u256(0)

    def _clamp_score(self, value: typing.Any) -> int:
        try:
            number = int(value)
            if number < 0:
                return 0
            if number > 100:
                return 100
            return number
        except Exception:
            return 0

    def _parse_audit(self, raw: str) -> typing.Any:
        try:
            data = json.loads(raw)
        except Exception:
            data = {}

        decision = str(data.get("decision", "NEEDS_REVIEW"))
        if decision != "APPROVED" and decision != "REJECTED":
            decision = "NEEDS_REVIEW"
        try:
            rank_position = int(data.get("rank_position", 0))
        except Exception:
            rank_position = 0
        if rank_position < 0:
            rank_position = 0
        if rank_position > 100:
            rank_position = 100
        try:
            observed_days = int(data.get("observed_days", 0))
        except Exception:
            observed_days = 0
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
            "reason": str(data.get("reason", "Trusted evidence was incomplete or malformed.")),
            "stability_score": self._clamp_score(data.get("stability_score", 0)),
            "whitehat_score": self._clamp_score(data.get("whitehat_score", 0)),
        }
