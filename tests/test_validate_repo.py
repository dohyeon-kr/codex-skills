import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import validate_repo


class ValidateRepoTest(unittest.TestCase):
    def test_current_repository_is_valid(self):
        self.assertEqual(validate_repo.validate_install_tree(), [])

    def test_rejects_symlink_in_installable_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills = root / "skills"
            skill = skills / "safe-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: safe-skill\ndescription: Safe test skill.\n---\n",
                encoding="utf-8",
            )
            (skill / "escaped").symlink_to(root / "outside")
            with mock.patch.object(validate_repo, "ROOT", root), mock.patch.object(
                validate_repo, "SKILLS_DIR", skills
            ):
                errors = validate_repo.validate_install_tree()
            self.assertTrue(any("symlinks are not allowed" in error for error in errors), errors)

    def test_rejects_world_writable_installable_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills = root / "skills"
            skill = skills / "safe-skill"
            skill.mkdir(parents=True)
            manifest = skill / "SKILL.md"
            manifest.write_text(
                "---\nname: safe-skill\ndescription: Safe test skill.\n---\n",
                encoding="utf-8",
            )
            manifest.chmod(0o666)
            with mock.patch.object(validate_repo, "ROOT", root), mock.patch.object(
                validate_repo, "SKILLS_DIR", skills
            ):
                errors = validate_repo.validate_install_tree()
            self.assertTrue(any("world-writable" in error for error in errors), errors)

    def test_does_not_read_symlinked_agent_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills = root / "skills"
            skill = skills / "safe-skill"
            agents = skill / "agents"
            agents.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: safe-skill\ndescription: Safe test skill.\n---\n",
                encoding="utf-8",
            )
            outside = root / "outside.yaml"
            outside.write_text("secret: should-not-be-parsed\n", encoding="utf-8")
            (agents / "openai.yaml").symlink_to(outside)
            with (
                mock.patch.object(validate_repo, "ROOT", root),
                mock.patch.object(validate_repo, "SKILLS_DIR", skills),
                mock.patch.object(
                    validate_repo,
                    "load_yaml",
                    wraps=validate_repo.load_yaml,
                ) as load_yaml,
            ):
                errors = validate_repo.validate_install_tree()
            self.assertTrue(any("symlinks are not allowed" in error for error in errors), errors)
            load_yaml.assert_called_once()

    def test_does_not_read_through_symlinked_agents_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills = root / "skills"
            skill = skills / "safe-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: safe-skill\ndescription: Safe test skill.\n---\n",
                encoding="utf-8",
            )
            outside = root / "outside"
            outside.mkdir()
            (outside / "openai.yaml").write_text(
                "secret: should-not-be-parsed\n",
                encoding="utf-8",
            )
            (skill / "agents").symlink_to(outside, target_is_directory=True)
            with (
                mock.patch.object(validate_repo, "ROOT", root),
                mock.patch.object(validate_repo, "SKILLS_DIR", skills),
                mock.patch.object(
                    validate_repo,
                    "load_yaml",
                    wraps=validate_repo.load_yaml,
                ) as load_yaml,
            ):
                errors = validate_repo.validate_install_tree()
            self.assertTrue(any("symlinks are not allowed" in error for error in errors), errors)
            load_yaml.assert_called_once()

    def test_rejects_invalid_front_matter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills = root / "skills"
            skill = skills / "broken-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: broken-skill\ndescription: invalid: mapping\n---\n",
                encoding="utf-8",
            )
            with mock.patch.object(validate_repo, "ROOT", root), mock.patch.object(
                validate_repo, "SKILLS_DIR", skills
            ):
                errors = validate_repo.validate_install_tree()
            self.assertTrue(any("invalid YAML" in error for error in errors), errors)

    def test_rejects_duplicate_front_matter_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills = root / "skills"
            skill = skills / "broken-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: broken-skill\nname: hidden-name\ndescription: Broken.\n---\n",
                encoding="utf-8",
            )
            with mock.patch.object(validate_repo, "ROOT", root), mock.patch.object(
                validate_repo, "SKILLS_DIR", skills
            ):
                errors = validate_repo.validate_install_tree()
            self.assertTrue(any("duplicate key" in error for error in errors), errors)

    def test_rejects_agent_icon_path_escape(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills = root / "skills"
            skill = skills / "safe-skill"
            agents = skill / "agents"
            agents.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: safe-skill\ndescription: Safe test skill.\n---\n",
                encoding="utf-8",
            )
            (agents / "openai.yaml").write_text(
                "interface:\n"
                '  display_name: "Safe Skill"\n'
                '  short_description: "A safe skill used for testing"\n'
                '  default_prompt: "Use $safe-skill for this test."\n'
                '  icon_small: "../../outside.png"\n',
                encoding="utf-8",
            )
            with mock.patch.object(validate_repo, "ROOT", root), mock.patch.object(
                validate_repo, "SKILLS_DIR", skills
            ):
                errors = validate_repo.validate_install_tree()
            self.assertTrue(any("escapes the skill directory" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
