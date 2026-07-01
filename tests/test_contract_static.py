import ast
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "SEOBoost.py"


class SEOBoostContractStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = CONTRACT.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_required_header(self):
        lines = self.source.splitlines()
        self.assertEqual(lines[0], "# v0.2.16")
        self.assertEqual(
            lines[1],
            '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }',
        )
        self.assertEqual(lines[2], "from genlayer import *")

    def test_only_allowed_imports(self):
        imports = [
            node
            for node in self.tree.body
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        self.assertEqual(len(imports), 3)
        self.assertEqual(imports[0].module, "genlayer")
        self.assertEqual(imports[1].names[0].name, "typing")
        self.assertEqual(imports[2].names[0].name, "json")

    def test_uses_semantic_consensus(self):
        self.assertIn("gl.eq_principle.prompt_comparative(run_audit, principle)", self.source)
        self.assertNotIn("gl.eq_principle.strict_eq", self.source)
        self.assertIn("gl.nondet.web.render", self.source)
        self.assertIn("gl.nondet.exec_prompt", self.source)

    def test_public_signatures_are_flat_and_allowed(self):
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            decorators = [ast.unparse(decorator) for decorator in node.decorator_list]
            if "gl.public.write" not in decorators and "gl.public.view" not in decorators:
                continue
            public_args = [arg for arg in node.args.args if arg.arg != "self"]
            self.assertLessEqual(len(public_args), 6, node.name)
            for arg in public_args:
                self.assertIn(ast.unparse(arg.annotation), {"str", "u256", "typing.Any"}, node.name)
            if node.returns is not None:
                self.assertIn(ast.unparse(node.returns), {"str", "u256", "typing.Any"}, node.name)

    def test_forbidden_public_types_absent(self):
        for token in ["Optional", "List", "Dict", "NamedTuple", "float", "bool"]:
            self.assertNotRegex(self.source, rf"\b{token}\b")

    def test_error_codes_cover_edges(self):
        for code in [
            "ZERO_REWARD",
            "HOLD_TOO_SHORT",
            "BAD_ARTICLE_URL",
            "WEB_RENDER_FAILED",
            "EVIDENCE_NOT_READY",
            "INSUFFICIENT_ESCROW",
            "NOT_APPROVED",
            "PAID",
        ]:
            self.assertIn(code, self.source)

    def test_no_inner_scrollbar_terms(self):
        css = ROOT / "frontend" / "src" / "app" / "globals.css"
        if not css.exists():
            return
        source = css.read_text(encoding="utf-8")
        self.assertNotRegex(source, re.compile(r"overflow-y\s*:\s*auto"))
        self.assertNotRegex(source, re.compile(r"overflow\s*:\s*auto"))
        self.assertNotRegex(source, re.compile(r"height\s*:\s*100vh"))


if __name__ == "__main__":
    unittest.main()
