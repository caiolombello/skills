#!/usr/bin/env python3
# Adapted from Agents365-ai/drawio-skill@2ee141e (MIT).
# See ../references/licenses/Agents365-drawio-skill-MIT.txt.
"""Inventory resources from `terraform show -json` and derive defensible edges.

Where tfimports.py reads the *declared* config (`.tf` files), this reads the
*real* state: what Terraform recorded as provisioned. It is provider-agnostic
(the JSON is uniform across AWS / Azure / GCP), expands `count`/`for_each` into
their real instances, keeps module nesting, and reuses tfimports' icon resolver
so every resource shows its official cloud icon. The output feeds autolayout.py:

  terraform show -json | python3 tfstate.py - -o graph.json
  python3 autolayout.py graph.json -o deployed.drawio

Input is the JSON `terraform show -json` prints — from recorded state or a saved
plan — as a file path or `-` for stdin. Nodes are managed resource instances
(data sources are ignored). State values may expose recorded `depends_on`
entries; saved plans instead expose configuration expression references. This
script uses either source when present and emits an inventory-only warning when
the input does not carry defensible dependency information. `--group` boxes
resources by module; `--no-icons` forces plain boxes.

Usage: terraform show -json | python3 tfstate.py - [-o graph.json]
       [--direction TB|LR] [--group] [--no-reduce] [--no-icons]
"""
import argparse
from collections import defaultdict
import importlib.util
import json
import os
import sys


def load_tfimports():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tfimports.py")
    spec = importlib.util.spec_from_file_location("tfimports", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def walk_module(mod, out):
    """Collect (address, type, name, index, module_path, depends_on) for every
    managed resource, recursing into child modules."""
    addr = mod.get("address", "")                    # "" for root, else module.x[...]
    for r in mod.get("resources") or []:
        if r.get("mode") == "data":
            continue
        out.append((r.get("address"), r.get("type"), r.get("name"),
                    r.get("index"), addr, r.get("depends_on") or []))
    for child in mod.get("child_modules") or []:
        walk_module(child, out)


def _bracket_ranges(text):
    """Yield index ranges while respecting quotes and escaped quote characters."""
    start, quote, escaped = None, None, False
    for position, char in enumerate(text):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in {'"', "'"}:
            quote = char
        elif char == "[" and start is None:
            start = position
        elif char == "]" and start is not None:
            yield start, position
            start = None


def _address_segments(address):
    """Split Terraform address segments without splitting quoted keys on dots."""
    text = str(address or "")
    segments, start, depth, quote, escaped = [], 0, 0, None, False
    for position, char in enumerate(text):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in {'"', "'"}:
            quote = char
        elif char == "[":
            depth += 1
        elif char == "]" and depth:
            depth -= 1
        elif char == "." and not depth:
            segments.append(text[start:position])
            start = position + 1
    segments.append(text[start:])
    return segments


def _strip_indexes(segment):
    ranges = list(_bracket_ranges(segment))
    if not ranges:
        return segment
    chunks, cursor = [], 0
    for start, end in ranges:
        chunks.append(segment[cursor:start])
        cursor = end + 1
    chunks.append(segment[cursor:])
    return "".join(chunks)


def static_address(address):
    """Remove indexes, including quoted/escaped keys, from a Terraform address."""
    return ".".join(_strip_indexes(part) for part in _address_segments(address))


def module_prefix(address):
    """Return the concrete module-instance prefix of a resource address."""
    parts = _address_segments(address)
    return ".".join(parts[:-2]) if len(parts) > 2 else ""


def static_module_prefix(address):
    """Return the static module path before the resource type and name."""
    parts = static_address(address).split(".")
    return ".".join(parts[:-2]) if len(parts) > 2 else ""


def resource_instance_key(address):
    """Return the concrete count/for_each key of the resource itself.

    Module instance indexes are intentionally excluded: they establish module
    scope and are handled by ``module_prefix``. The returned text preserves
    Terraform's address representation, so ``[0]`` only matches ``[0]`` and
    ``[\"blue\"]`` only matches ``[\"blue\"]``.
    """
    tail = _address_segments(address)[-1]
    for start, end in _bracket_ranges(tail):
        if end == len(tail) - 1:
            return tail[start + 1:end]
    return None


def expression_references(value):
    """Recursively collect official configuration-expression references."""
    refs = set()
    if isinstance(value, dict):
        raw = value.get("references")
        if isinstance(raw, list):
            refs.update(ref for ref in raw if isinstance(ref, str))
        for child in value.values():
            refs.update(expression_references(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(expression_references(child))
    return refs


def expression_reference_groups(value):
    """Keep reference lists separated by expression leaf.

    Terraform's JSON preserves which references belong to one expression, but
    not the expression source text. Keeping those groups prevents an unrelated
    `count.index`/`each.key` reference from making every dependency on the same
    resource look instance-mapped.
    """
    groups = []
    if isinstance(value, dict):
        raw = value.get("references")
        if isinstance(raw, list):
            references = {ref for ref in raw if isinstance(ref, str)}
            if references:
                groups.append(references)
        for key, child in value.items():
            if key != "references":
                groups.extend(expression_reference_groups(child))
    elif isinstance(value, list):
        for child in value:
            groups.extend(expression_reference_groups(child))
    return groups


def walk_configuration(module, prefix, out):
    """Collect expression references and instance-mapping signals per resource."""
    for resource in module.get("resources") or []:
        if resource.get("mode") == "data" or not resource.get("address"):
            continue
        local = static_address(resource["address"])
        address = f"{prefix}.{local}" if prefix else local
        reference_groups = expression_reference_groups(
            {
                "expressions": resource.get("expressions") or {},
                "count_expression": resource.get("count_expression") or {},
                "for_each_expression": resource.get("for_each_expression") or {},
                "provisioners": resource.get("provisioners") or [],
            }
        )
        out[address] = {"reference_groups": reference_groups}
    for name, call in (module.get("module_calls") or {}).items():
        child = call.get("module") or {}
        child_prefix = f"{prefix}.module.{name}" if prefix else f"module.{name}"
        walk_configuration(child, child_prefix, out)


def referenced_resource(reference, source_static, resources):
    """Resolve a configuration reference to a resource in the same module."""
    source_module = static_module_prefix(source_static)
    local = f"{source_module}.{reference}" if source_module else reference
    for candidate in (local, reference):
        matches = [
            address
            for address in resources
            if candidate == address
            or candidate.startswith(address + ".")
            or candidate.startswith(address + "[")
        ]
        if matches:
            return max(matches, key=len)
    return None


def reference_target(reference, source_static, resources):
    """Resolve a reference to its static resource and optional literal key."""
    target = referenced_resource(reference, source_static, resources)
    if not target:
        return None, None
    source_module = static_module_prefix(source_static)
    local = f"{source_module}.{reference}" if source_module else reference
    candidate = next(
        (
            value
            for value in (local, reference)
            if value == target
            or value.startswith(target + ".")
            or value.startswith(target + "[")
        ),
        reference,
    )
    suffix = candidate[len(target):]
    if not suffix.startswith("["):
        return target, None
    for start, end in _bracket_ranges(suffix):
        if start == 0:
            return target, suffix[start + 1:end]
    return target, None


def _instance_edges(
    sources,
    targets,
    source_static,
    target_static,
    warnings,
    *,
    target_key=None,
    uses_instance_mapping=False,
):
    """Expand only relations whose instance semantics are explicit."""
    if not sources or not targets:
        return set()
    if target_key is not None:
        targets = [target for target in targets if resource_instance_key(target) == target_key]
        if not targets:
            if warnings is not None:
                warnings.add(
                    "literal Terraform dependency omitted: "
                    f"{source_static} -> {target_static}[{target_key}] is absent"
                )
            return set()
    if len(sources) == 1 and len(targets) == 1:
        return {(sources[0], targets[0])} if sources[0] != targets[0] else set()
    if len(targets) == 1:
        # A single target is a shared dependency of every source instance.
        return {(source, targets[0]) for source in sources if source != targets[0]}

    if warnings is not None:
        if uses_instance_mapping:
            warnings.add(
                "ambiguous Terraform dependency omitted: "
                f"{source_static} -> {target_static} includes dynamic or "
                "unresolved references, but the plan JSON does not preserve "
                "an instance mapping"
            )
        else:
            warnings.add(
                "ambiguous Terraform dependency omitted: "
                f"{source_static} -> {target_static} is a static resource "
                "reference, but the plan JSON does not preserve whether one "
                "or all instances are targeted"
            )
    return set()


def expand_static_edge(
    source_static,
    target_static,
    actual_by_static,
    warnings=None,
    *,
    target_key=None,
    uses_instance_mapping=False,
):
    """Expand a relation while preserving its configuration/state semantics."""
    edges = set()
    same_module = static_module_prefix(source_static) == static_module_prefix(target_static)
    sources_by_module = defaultdict(list)
    for source in actual_by_static.get(source_static, []):
        sources_by_module[module_prefix(source)].append(source)
    targets_by_module = defaultdict(list)
    for target in actual_by_static.get(target_static, []):
        targets_by_module[module_prefix(target)].append(target)

    for source_module, sources in sources_by_module.items():
        if same_module:
            targets = targets_by_module.get(source_module, [])
        else:
            targets = [target for group in targets_by_module.values() for target in group]
        edges.update(
            _instance_edges(
                sources,
                targets,
                source_static,
                target_static,
                warnings,
                target_key=target_key,
                uses_instance_mapping=uses_instance_mapping,
            )
        )
    return edges


def configuration_edges(configuration, addresses, warnings=None, evidence=None):
    """Derive saved-plan edges from official expression references."""
    resources = {}
    walk_configuration((configuration or {}).get("root_module") or {}, "", resources)
    actual_by_static = {}
    for address in addresses:
        actual_by_static.setdefault(static_address(address), []).append(address)
    edges = set()
    for source, details in resources.items():
        for references in details["reference_groups"]:
            targets = {}
            unresolved_references = set()
            for reference in references:
                target, target_key = reference_target(reference, source, resources)
                if target:
                    if evidence is not None:
                        evidence.add("configuration")
                    # A literal resource index is more precise than Terraform's
                    # accompanying static/attribute references in this expression.
                    targets.setdefault(target, set()).add(target_key)
                else:
                    unresolved_references.add(reference)
            uses_instance_mapping = bool(unresolved_references)
            for target, keys in targets.items():
                literal_keys = {key for key in keys if key is not None}
                keys_to_expand = literal_keys or {None}
                for target_key in keys_to_expand:
                    edges.update(
                        expand_static_edge(
                            source,
                            target,
                            actual_by_static,
                            warnings,
                            target_key=target_key,
                            uses_instance_mapping=uses_instance_mapping,
                        )
                    )
    return edges


def recorded_dependency_edges(resources, warnings=None, evidence=None):
    """Use only instance relations retained by a state values representation."""
    addresses = {resource[0] for resource in resources}
    actual_by_static = {}
    for address in addresses:
        actual_by_static.setdefault(static_address(address), []).append(address)
    edges = set()
    for source, _, _, _, _, dependencies in resources:
        for dependency in dependencies:
            target_static = static_address(dependency)
            source_static = static_address(source)
            if target_static in actual_by_static:
                if evidence is not None:
                    evidence.add("state")
                targets = actual_by_static[target_static]
                if static_module_prefix(source_static) == static_module_prefix(target_static):
                    targets = [
                        target
                        for target in targets
                        if module_prefix(target) == module_prefix(source)
                    ]
                target_key = resource_instance_key(dependency)
                if target_key is not None:
                    targets = [
                        target
                        for target in targets
                        if resource_instance_key(target) == target_key
                    ]
                    if not targets and warnings is not None:
                        warnings.add(
                            "literal Terraform dependency omitted: "
                            f"{source} -> {dependency} is absent"
                        )
                elif len(targets) > 1:
                    if warnings is not None:
                        warnings.add(
                            "ambiguous recorded state dependency omitted: "
                            f"{source_static} -> {target_static} is a static depends_on "
                            "whose instance mapping is not preserved"
                        )
                    targets = []
                edges.update(
                    (source, target)
                    for target in targets
                    if source != target
                )
    return edges


def main():
    ap = argparse.ArgumentParser(description="`terraform show -json` -> autolayout graph JSON.")
    ap.add_argument("input", help="`terraform show -json` output file, or - for stdin")
    ap.add_argument("-o", "--output", help="output JSON path (default: stdout)")
    ap.add_argument("--direction", default="TB", choices=["TB", "LR"])
    ap.add_argument("--group", action="store_true",
                    help="group resources into containers by module")
    ap.add_argument("--no-reduce", action="store_true",
                    help="keep every edge (skip transitive reduction)")
    ap.add_argument("--no-icons", action="store_true",
                    help="plain boxes instead of official cloud icons")
    args = ap.parse_args()

    if args.input == "-":
        text = sys.stdin.read()
    else:
        with open(args.input, encoding="utf-8") as handle:
            text = handle.read()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        sys.exit(f"error: input is not valid JSON ({exc}) — feed `terraform show -json`")
    # State: top-level "values"; saved plan: "planned_values".
    root = ((data.get("values") or data.get("planned_values") or {}).get("root_module")) or {}
    resources = []
    walk_module(root, resources)
    if not resources:
        sys.exit("error: no managed resources found in the Terraform state/plan")

    addresses = {resource[0] for resource in resources}
    ambiguity_warnings, dependency_evidence = set(), set()
    recorded_edges = recorded_dependency_edges(
        resources, ambiguity_warnings, dependency_evidence
    )
    planned_edges = configuration_edges(
        data.get("configuration"), addresses, ambiguity_warnings, dependency_evidence
    )
    edges = sorted(recorded_edges | planned_edges)

    tf = load_tfimports()
    raw = len(edges)
    if not args.no_reduce and edges:
        edges = tf.transitive_reduce(list(addresses), edges)

    resolver = None if args.no_icons else tf.IconResolver()
    unmatched, nodes = [], []
    for addr, rtype, name, index, mpath, _ in resources:
        label = name if index is None else f"{name}[{index}]"
        node = {"id": addr, "label": label}
        icon = resolver.resolve(rtype) if resolver and rtype else None
        if icon:
            node.update(style=icon["style"], width=icon["w"], height=icon["h"])
        else:
            node["label"] = f"{label}\n{rtype}" if rtype else label
            if resolver and rtype:
                unmatched.append(rtype)
        if args.group and mpath:
            node["group"] = mpath
        nodes.append(node)

    graph = {"direction": args.direction, "nodes": nodes,
             "edges": [{"source": s, "target": t} for s, t in edges]}
    if resolver:
        # Icon labels render below the shape — reserve extra layout spacing.
        graph.update(ranksep=0.7, nodesep=0.6)
    out = json.dumps(graph, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        sys.stderr.write(f"wrote {args.output}\n")
    else:
        sys.stdout.write(out)
    note = "" if args.no_reduce else f" (reduced from {raw})"
    sys.stderr.write(f"{len(nodes)} resources, {len(edges)} edges{note}\n")
    sources = []
    if "state" in dependency_evidence:
        sources.append("recorded state depends_on")
    if "configuration" in dependency_evidence:
        sources.append("saved-plan configuration references")
    if sources:
        sys.stderr.write("dependency source: " + " + ".join(sources) + "\n")
    elif "planned_values" in data:
        sys.stderr.write(
            "warning: no resolvable configuration references; plan rendered as "
            "resource inventory only\n"
        )
    else:
        sys.stderr.write(
            "warning: this state values representation exposes no recorded "
            "dependencies; rendered as resource inventory only\n"
        )
    for warning in sorted(ambiguity_warnings):
        sys.stderr.write("warning: " + warning + "\n")
    if unmatched:
        sys.stderr.write("no icon for: " + ", ".join(sorted(set(unmatched))) + "\n")


if __name__ == "__main__":
    main()
