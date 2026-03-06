import unittest
import os
import json


class TestProjectInit(unittest.TestCase):
    def test_backend_pyproject_exists_and_contains_packages(self):
        pyproject_path = os.path.join("backend", "pyproject.toml")
        self.assertTrue(
            os.path.exists(pyproject_path),
            "backend/pyproject.toml is missing",
        )
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
        for pkg in ["fastapi", "uvicorn", "pydantic", "pytest"]:
            self.assertIn(pkg, content, f"{pkg} not listed in backend/pyproject.toml")

    def test_frontend_package_json_contains_next(self):
        self.assertTrue(os.path.exists("package.json"), "package.json is missing")
        with open("package.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        deps = {}
        if isinstance(data, dict):
            deps.update(data.get("dependencies", {}))
            deps.update(data.get("devDependencies", {}))
        self.assertIn("next", deps, "next not found in package.json dependencies")


if __name__ == "__main__":
    unittest.main()
