#!/usr/bin/env python3
import re
import stat
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_YAML_BYTES = 64 * 1024
ALLOWED_SKILL_FIELDS = {"allowed-tools", "description", "license", "metadata", "name"}


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def construct_unique_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key: {key}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def relative(path):
    return path.relative_to(ROOT)


def load_yaml(path, content):
    if len(content.encode("utf-8")) > MAX_YAML_BYTES:
        raise ValueError(f"{relative(path)}: YAML exceeds {MAX_YAML_BYTES} byte limit")
    try:
        data = yaml.load(content, Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f"{relative(path)}: invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{relative(path)}: YAML root must be a mapping")
    return data


def load_front_matter(path):
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"{relative(path)}: could not read UTF-8 text: {exc}") from exc
    if not lines or lines[0] != "---":
        raise ValueError(f"{relative(path)}: missing opening front matter delimiter")
    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{relative(path)}: missing closing front matter delimiter") from exc
    return load_yaml(path, "\n".join(lines[1:closing]))


def require_text(mapping, key, path):
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{relative(path)}: {key} must be a non-empty string")
    return value.strip()


def validate_skill(skill_dir):
    errors = []
    manifest = skill_dir / "SKILL.md"
    if not manifest.is_file() or manifest.is_symlink():
        return [f"{relative(skill_dir)}: missing regular SKILL.md"]

    try:
        metadata = load_front_matter(manifest)
        name = require_text(metadata, "name", manifest)
        description = require_text(metadata, "description", manifest)
        unexpected = set(metadata) - ALLOWED_SKILL_FIELDS
        if unexpected:
            errors.append(
                f"{relative(manifest)}: unexpected front matter fields: "
                f"{', '.join(sorted(map(str, unexpected)))}"
            )
        if name != skill_dir.name:
            errors.append(f"{relative(manifest)}: name must match directory ({skill_dir.name})")
        if not SKILL_NAME.fullmatch(name):
            errors.append(f"{relative(manifest)}: invalid skill name: {name}")
        if len(name) > 64:
            errors.append(f"{relative(manifest)}: name exceeds 64 characters")
        if len(description) > 1024:
            errors.append(f"{relative(manifest)}: description exceeds 1024 characters")
        if "<" in description or ">" in description:
            errors.append(f"{relative(manifest)}: description cannot contain angle brackets")
    except ValueError as exc:
        errors.append(str(exc))

    agents_dir = skill_dir / "agents"
    if agents_dir.is_symlink():
        return errors
    agent_manifest = agents_dir / "openai.yaml"
    if agent_manifest.is_symlink():
        return errors
    if agent_manifest.exists():
        try:
            content = agent_manifest.read_text(encoding="utf-8")
            agent = load_yaml(agent_manifest, content)
            interface = agent.get("interface")
            if not isinstance(interface, dict):
                raise ValueError(f"{relative(agent_manifest)}: interface must be a mapping")
            require_text(interface, "display_name", agent_manifest)
            short_description = require_text(interface, "short_description", agent_manifest)
            default_prompt = require_text(interface, "default_prompt", agent_manifest)
            if not 25 <= len(short_description) <= 64:
                errors.append(
                    f"{relative(agent_manifest)}: short_description must be 25-64 characters"
                )
            if f"${skill_dir.name}" not in default_prompt:
                errors.append(
                    f"{relative(agent_manifest)}: default_prompt must mention ${skill_dir.name}"
                )
            for key in ("icon_small", "icon_large"):
                if key not in interface:
                    continue
                icon = require_text(interface, key, agent_manifest)
                try:
                    icon_path = (skill_dir / icon).resolve()
                except (OSError, RuntimeError) as exc:
                    errors.append(f"{relative(agent_manifest)}: invalid {key} path: {exc}")
                    continue
                try:
                    icon_path.relative_to(skill_dir.resolve())
                except ValueError:
                    errors.append(f"{relative(agent_manifest)}: {key} escapes the skill directory")
                    continue
                if not icon_path.is_file():
                    errors.append(f"{relative(agent_manifest)}: {key} does not reference a file")
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(str(exc))
    return errors


def validate_install_tree():
    errors = []
    if not SKILLS_DIR.is_dir() or SKILLS_DIR.is_symlink():
        return ["skills: missing regular skills directory"]

    for path in [SKILLS_DIR, *SKILLS_DIR.rglob("*")]:
        if path.is_symlink():
            errors.append(f"{relative(path)}: symlinks are not allowed in installable content")
            continue
        if path.lstat().st_mode & stat.S_IWOTH:
            errors.append(f"{relative(path)}: world-writable installable content is not allowed")

    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir() or entry.is_symlink():
            errors.append(f"{relative(entry)}: unexpected top-level entry")
            continue
        if not SKILL_NAME.fullmatch(entry.name):
            errors.append(f"{relative(entry)}: invalid skill directory name")
            continue
        errors.extend(validate_skill(entry))
    return errors


def main():
    errors = validate_install_tree()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("OK: skill manifests and installable paths are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
