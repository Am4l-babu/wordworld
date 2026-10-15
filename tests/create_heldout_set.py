"""One-time, prediction-free construction of the 2026-10-15 evaluation set.

This file does not import or execute the parser. Expected actions were authored
before the evaluation run. Keep this dataset separate from development tests.
"""
import ast
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = Path(__file__).with_name("heldout_commands.json")


def add(kind, count=1, color=None, relation=None, target=None, targets=None):
    result = {"action": "add", "type": kind, "count": count, "color": color}
    if relation:
        result.update(relation=relation, target=target or targets[0])
    if targets:
        result["targets"] = targets
    return result


def remove(kind, count="all"):
    return {"action": "remove", "type": kind, "count": count}


def setting(key, value):
    return {"action": "setting", "key": key, "value": value}


CASES = []


def case(text, category, actions, scope="core", note=""):
    CASES.append({"id": f"H{len(CASES)+1:02d}", "text": text, "category": category,
                  "scope": scope, "expected_actions": actions, "label_note": note})


case("Please build four purple cottages beside the stream.", "lexical_grounding", [add("house", 4, "purple", "near", "river")])
case("Plant seven green trees south of the tower.", "spatial_grounding", [add("tree", 7, "green", "below", "tower")])
case("Place 6 yellow blossoms north of the fortress.", "spatial_grounding", [add("flower", 6, "yellow", "above", "castle")])
case("Give me three white cabins west of the pond.", "lexical_grounding", [add("house", 3, "white", "left", "lake")])
case("Draw two paths next to the creek.", "lexical_grounding", [add("road", 2, relation="near", target="river")])
case("Put a boulder in the center of the garden.", "spatial_grounding", [add("rock", relation="inside", target="flower")], note="Use the project's garden→flower alias; this evaluates parsing, not garden geometry.")
case("Show a lighthouse at the back of the cottages.", "lexical_grounding", [add("tower", relation="above", target="house")])
case("Create nine pink flowers around the lake.", "spatial_grounding", [add("flower", 9, "pink", "near", "lake")])
case("Insert a mountain to the right of the bridge.", "spatial_grounding", [add("mountain", relation="right", target="bridge")])
case("Grow a woodland close to the road.", "lexical_grounding", [add("tree", 6, relation="near", target="road")])
case("Add 12 blue homes.", "lexical_grounding", [add("house", 12, "blue")])
case("Build a bridge between the tower and the castle.", "spatial_grounding", [add("bridge", relation="between", targets=["tower", "castle"])])
case("Place two rocks between the pond and the house.", "spatial_grounding", [add("rock", 2, relation="between", targets=["lake", "house"])])
case("Plant three flowers within the castle.", "spatial_grounding", [add("flower", 3, relation="inside", target="castle")])
case("Build a hut, a tower, and a road.", "multi_action_scope", [add("house"), add("tower"), add("road")])
case("Delete 4 boulders, then plant six blossoms.", "multi_action_scope", [remove("rock", 4), add("flower", 6)])
case("Cut down a couple of trees; create a pond.", "multi_action_scope", [remove("tree", 2), add("lake")])
case("Erase one bridge and place three yellow cottages.", "multi_action_scope", [remove("bridge", 1), add("house", 3, "yellow")])
case("Clear the map; show a river and a bridge.", "multi_action_scope", [{"action": "reset"}, add("river"), add("bridge")])
case("Make it morning and plant two trees.", "multi_action_scope", [setting("time", "day"), add("tree", 2)])
case("Make it midnight with snowing.", "settings", [setting("time", "night"), setting("weather", "snow")])
case("Stop the snow and make it sunshine.", "settings", [setting("weather", "clear"), setting("time", "day")])
case("Do not erase the towers; plant five trees.", "negation", [add("tree", 5)])
case("Don't build houses, towers, or castles; add a rock.", "negation", [add("rock")])
case("Add zero bridges and zero roads.", "negation", [])
case("Build eleven houses near the lake.", "quantifiers", [add("house", 11, relation="near", target="lake")])
case("Plant a dozen flowers behind the tower.", "quantifiers", [add("flower", 12, relation="above", target="tower")])
case("Place a pair of rocks beside the river.", "quantifiers", [add("rock", 2, relation="near", target="river")])
case("Add twelve orange cottages.", "quantifiers", [add("house", 12, "orange")])
case("Build a house, then remove it.", "coreference", [add("house"), remove("house", 1)], "capability_probe", "Within-command antecedent: it refers to the newly created house. Pronoun resolution is a documented limitation.")
case("Build a red house and a blue house, then put a tree between them.", "coreference", [add("house", color="red"), add("house", color="blue"), add("tree", relation="between", targets=["house", "house"])], "capability_probe", "Them refers to the two newly created houses. This tests a documented capability gap.")
case("Plant five trees and then delete two of them.", "coreference", [add("tree", 5), remove("tree", 2)], "capability_probe", "Them refers to the five newly created trees; remove two, not all five.")
case("Near the lake, plant four trees.", "fronted_relations", [add("tree", 4, relation="near", target="lake")], note="Initial prepositional phrase modifies plant; lake is an existing landmark.")
case("To the left of the castle, build a tower.", "fronted_relations", [add("tower", relation="left", target="castle")])
case("Between the house and the tower, place a bridge.", "fronted_relations", [add("bridge", relation="between", targets=["house", "tower"])])
case("Add a tree near the lake and a flower beside the castle.", "spatial_grounding", [add("tree", relation="near", target="lake"), add("flower", relation="near", target="castle")])
case("Build three red houses and three blue towers.", "multi_action_scope", [add("house", 3, "red"), add("tower", 3, "blue")], note="Color extraction is scored; tower material recoloring is a separate rendering limitation.")
case("Build one red and one blue house.", "coordination_ellipsis", [add("house", color="red"), add("house", color="blue")], "capability_probe", "One red [house] and one blue house: the omitted first noun denotes a separate house.")
case("Add three red houses and two blue flowers near the river.", "multi_action_scope", [add("house", 3, "red"), add("flower", 2, "blue", "near", "river")], note="Use the documented local/nearest noun-phrase attachment convention for the final relation.")
case("Remove all houses and all towers.", "multi_action_scope", [remove("house"), remove("tower")])
case("Don't remove any trees, but add two flowers.", "negation", [add("flower", 2)])
case("Please do not add a tree or a rock.", "negation", [])
case("Keep the houses and remove the trees.", "protected_mentions", [remove("tree")], "capability_probe", "Keep explicitly protects houses. No new action type is needed: emit only tree removal.")
case("Leave the lake alone and add a bridge.", "protected_mentions", [add("bridge")], "capability_probe", "Lake is a protected mention, not an add subject.")
case("Remove no trees and add two rocks.", "negation", [add("rock", 2)])
case("Build two houses but not a castle.", "negation", [add("house", 2)])
case("Make it rain, then stop raining.", "settings", [setting("weather", "rain"), setting("weather", "clear")])
case("Make it not rain.", "settings", [setting("weather", "clear")], note="The weather enum is mutually exclusive; requesting non-rain maps to clear in this evaluation.")
case("Don’t add any bridges.", "negation", [], note="U+2019 apostrophe; same negation meaning as ASCII Don't.")
case("Make it snow; clear the world; add a pink house.", "settings", [setting("weather", "snow"), {"action": "reset"}, add("house", color="pink")])


def normalized(text):
    return re.sub(r"\s+", " ", text.casefold().strip()).rstrip(".!?")


if __name__ == "__main__":
    if DESTINATION.exists():
        raise SystemExit("Refusing to overwrite the frozen evaluation set.")
    assert len(CASES) == 50
    development = json.loads((ROOT / "tests/commands.json").read_text(encoding="utf-8"))
    known = {normalized(c["text"]) for c in development}
    for path in (ROOT / "tests").glob("test_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        known.update(normalized(node.value) for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str))
    browser_source = (ROOT / "frontend/tests/browser/smoke.spec.js").read_text(encoding="utf-8")
    known.update(normalized(match.group(2)) for match in re.finditer(r"(['\"])([^\n]*?)\1", browser_source))
    known.update(normalized(line) for line in (ROOT / "README.md").read_text(encoding="utf-8").splitlines())
    texts = [normalized(c["text"]) for c in CASES]
    assert len(set(texts)) == 50, "Duplicate evaluation commands"
    assert not set(texts) & known, f"Development overlap: {set(texts) & known}"
    report = {
        "name": "WordWorld new-command evaluation 2026-10-15",
        "method": "50 new hand-authored commands and gold actions frozen before executing the parser. Author had access to implementation and development examples; not independently human-labeled or randomly sampled.",
        "parser_sha256_before": hashlib.sha256((ROOT / "backend/parser.py").read_bytes()).hexdigest(),
        "development_json_sha256": hashlib.sha256((ROOT / "tests/commands.json").read_bytes()).hexdigest(),
        "scope": "44 core commands plus 6 explicitly marked capability probes. Each command is parsed independently; pronoun probes contain their antecedents within the same command. Landmarks are assumed to exist; scene placement is not scored.",
        "gold_policy": "Exact ordered action JSON using existing aliases and action schema. Do not tune the parser or alter labels after observing results. All counts fit the 16-object cap. No out-of-vocabulary object types are requested.",
        "uniqueness": "50 unique commands; no normalized exact matches in development JSON, Python test string literals, browser smoke test literals, or README lines.",
        "cases": CASES,
    }
    DESTINATION.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Frozen {len(CASES)} commands: {DESTINATION}")
    print(f"Dataset SHA256: {hashlib.sha256(DESTINATION.read_bytes()).hexdigest()}")
    print(f"Parser SHA256: {report['parser_sha256_before']}")
    print("No parser execution occurred while constructing the labels.")
