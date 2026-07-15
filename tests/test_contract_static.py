import ast
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "SEOBoost.py"
SOURCE = CONTRACT.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


class SEOBoostContractStaticTests(unittest.TestCase):
    def test_required_runtime_header(self):
        lines = SOURCE.splitlines()
        self.assertEqual(lines[0], "# v0.2.16")
        self.assertEqual(lines[1], '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }')
        self.assertEqual(lines[2], "from genlayer import *")

    def test_campaign_creation_is_real_payable_custody(self):
        self.assertIn("@gl.public.write.payable\n    def create_campaign", SOURCE)
        self.assertIn("reward = gl.message.value", SOURCE)
        self.assertIn("self.campaign_clients[campaign_id] = gl.message.sender_address.as_hex.lower()", SOURCE)
        self.assertNotIn("client_wallet: str", SOURCE)

    def test_invalid_writes_revert_and_roles_are_bound_to_sender(self):
        self.assertGreaterEqual(SOURCE.count("raise gl.vm.UserError"), 15)
        self.assertIn('raise gl.vm.UserError("AGENCY_ONLY")', SOURCE)
        self.assertIn('raise gl.vm.UserError("CLIENT_ONLY")', SOURCE)
        self.assertIn("self.campaign_agencies[campaign_id] != gl.message.sender_address.as_hex.lower()", SOURCE)

    def test_release_and_refund_transfer_real_value(self):
        self.assertIn("def release_reward", SOURCE)
        self.assertIn("def refund_reward", SOURCE)
        self.assertGreaterEqual(SOURCE.count("emit_transfer(value=reward)"), 2)
        self.assertIn("reward > self.balance", SOURCE)
        self.assertIn('self.campaign_statuses[campaign_id] = "PAID"', SOURCE)
        self.assertIn('self.campaign_statuses[campaign_id] = "REFUNDED"', SOURCE)
        self.assertIn('status == "NEEDS_REVIEW"', SOURCE)
        self.assertIn("self.campaign_revision_deadlines[campaign_id]", SOURCE)

    def test_evidence_is_constrained_before_ai_review(self):
        self.assertIn("_article_matches_domain", SOURCE)
        self.assertIn("_trusted_serp", SOURCE)
        self.assertIn("_trusted_analytics", SOURCE)
        self.assertIn("_trusted_backlink", SOURCE)
        self.assertNotIn("example.com/seoboost", SOURCE)
        self.assertIn("Do not approve from the article alone", SOURCE)

    def test_semantic_consensus_wraps_nondeterminism(self):
        self.assertIn("gl.eq_principle.prompt_comparative(run_audit, principle)", SOURCE)
        self.assertNotIn("gl.eq_principle.strict_eq", SOURCE)
        self.assertIn("gl.nondet.web.render", SOURCE)
        self.assertIn("gl.nondet.exec_prompt", SOURCE)

    def test_no_unbounded_entity_scan(self):
        self.assertNotRegex(SOURCE, re.compile(r"while\s+\w+\s*<\s*self\.campaign_count"))

    def test_public_signatures_are_flat_and_supported(self):
        allowed = {"str", "u256", "typing.Any"}
        for node in ast.walk(TREE):
            if not isinstance(node, ast.FunctionDef):
                continue
            decorators = {ast.unparse(item) for item in node.decorator_list}
            if not any(item.startswith("gl.public.") for item in decorators):
                continue
            args = [arg for arg in node.args.args if arg.arg != "self"]
            self.assertLessEqual(len(args), 6, node.name)
            for arg in args:
                self.assertIn(ast.unparse(arg.annotation), allowed, node.name)

    def test_frontend_has_no_nested_vertical_scroll_container(self):
        css = (ROOT / "frontend" / "src" / "app" / "globals.css").read_text(encoding="utf-8")
        self.assertNotRegex(css, re.compile(r"overflow-y\s*:\s*auto"))
        self.assertNotRegex(css, re.compile(r"overflow\s*:\s*auto"))


if __name__ == "__main__":
    unittest.main()
