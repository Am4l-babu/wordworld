r"""Draw the report's figures as dependency-free SVG from the recorded result files.

Usage:  .venv\Scripts\python.exe -m tests.make_figures

Writes docs/assets/fig-*.svg. Re-run after tests.ablation / tests.evaluate_typos. Every figure carries a <title> and <desc>
so screen readers and Markdown viewers get the same numbers the picture shows.
"""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

from tests.compare_extractors import labelled_sets

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/assets"
INK, MUTED, GRID = "#2d3244", "#6b6f86", "#e4e2ee"
PURPLE, GREEN, GREY, AMBER = "#7657cb", "#5aa777", "#a9a7b8", "#d99a3d"
FONT = "font-family=\"DM Sans, Segoe UI, Arial, sans-serif\""


def svg(width, height, title, desc, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="t d" {FONT}>\n'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>\n<rect width="{width}" height="{height}" fill="#ffffff"/>\n{body}</svg>\n')


def text(x, y, s, size=12, fill=INK, anchor="start", weight="400"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{escape(str(s))}</text>\n'


def accuracy_figure():
    ablation = json.loads((ROOT / "evaluation/results/ablation.json").read_text(encoding="utf-8"))["configurations"]
    first_runs = {name: fr for name, _t, fr, _c in labelled_sets() if fr}
    names = list(ablation["full"]["by_set"])
    shown = [n for n in names if n != "development"]
    W, H, left, top, plot_w, plot_h = 940, 400, 56, 64, 860, 250
    body = text(left, 28, "Exact match per labelled set: first run vs retest vs dependency baseline", 15, weight="700")
    body += text(left, 46, "50 commands per set. First run = scored before any tuning on that set; retest = current parser.", 11, MUTED)
    for pct in range(0, 101, 20):
        y = top + plot_h * (1 - pct / 100)
        body += f'<line x1="{left}" y1="{y}" x2="{left + plot_w}" y2="{y}" stroke="{GRID}"/>\n' + text(left - 8, y + 4, f"{pct}%", 10, MUTED, "end")
    group_w = plot_w / len(shown)
    bar_w = group_w / 4
    for i, name in enumerate(shown):
        full = ablation["full"]["by_set"][name]
        base = ablation["baseline"]["by_set"][name]
        first = first_runs[name]
        values = [(first["correct"] / first["total"], PURPLE, "first run"), (full[0] / full[1], GREEN, "retest"), (base[0] / base[1], GREY, "baseline")]
        for j, (value, colour, _label) in enumerate(values):
            x = left + i * group_w + group_w * 0.12 + j * bar_w
            h = plot_h * value
            body += f'<rect x="{x:.1f}" y="{top + plot_h - h:.1f}" width="{bar_w - 2:.1f}" height="{h:.1f}" fill="{colour}"/>\n'
        body += text(left + i * group_w + group_w / 2, top + plot_h + 18, name.replace("fresh_", ""), 11, MUTED, "middle")
    ly = H - 52
    for k, (colour, label) in enumerate([(PURPLE, "Rules, first run (frozen)"), (GREEN, "Rules, retest after fixes"), (GREY, "Dependency baseline (frozen before use)")]):
        x = left + k * 290
        body += f'<rect x="{x}" y="{ly}" width="14" height="14" fill="{colour}"/>\n' + text(x + 20, ly + 12, label, 12)
    body += text(left, H - 14, "heldout, v2 … v12 are successive frozen sets; the retest numbers are optimistic because the rules were improved on each set after its first run.", 10.5, MUTED)
    desc = "; ".join(f"{n.replace('fresh_', '')}: first run {first_runs[n]['correct']}/50, retest {ablation['full']['by_set'][n][0]}/50, baseline {ablation['baseline']['by_set'][n][0]}/50" for n in shown)
    return svg(W, H, "Exact match per labelled set", desc, body)


def ablation_figure():
    data = json.loads((ROOT / "evaluation/results/ablation.json").read_text(encoding="utf-8"))["configurations"]
    order = ["full", "no_context", "no_filters", "no_edits", "no_spacy", "baseline"]
    W, H, left, top, plot_w, row = 1080, 370, 250, 70, 620, 36
    body = text(40, 28, "Ablation: removing one component at a time (650 labelled commands)", 15, weight="700")
    body += text(40, 46, "Bars are exact match; whiskers are 95% Wilson intervals.", 11, MUTED)
    for pct in range(0, 101, 20):
        x = left + plot_w * pct / 100
        body += f'<line x1="{x}" y1="{top - 6}" x2="{x}" y2="{top + row * len(order)}" stroke="{GRID}"/>\n' + text(x, top + row * len(order) + 16, f"{pct}%", 10, MUTED, "middle")
    for i, key in enumerate(order):
        s = data[key]
        y = top + i * row
        value = s["correct"] / s["total"]
        colour = GREY if key == "baseline" else PURPLE if key == "full" else AMBER if key != "no_spacy" else GREEN
        body += text(left - 12, y + 19, s["label"], 12, INK, "end")
        body += f'<rect x="{left}" y="{y + 6}" width="{plot_w * value:.1f}" height="20" fill="{colour}"/>\n'
        lo, hi = s["ci95"]
        mid = y + 16
        body += (f'<line x1="{left + plot_w * lo:.1f}" y1="{mid}" x2="{left + plot_w * hi:.1f}" y2="{mid}" stroke="{INK}" stroke-width="1.5"/>\n'
                 f'<line x1="{left + plot_w * lo:.1f}" y1="{mid - 5}" x2="{left + plot_w * lo:.1f}" y2="{mid + 5}" stroke="{INK}" stroke-width="1.5"/>\n'
                 f'<line x1="{left + plot_w * hi:.1f}" y1="{mid - 5}" x2="{left + plot_w * hi:.1f}" y2="{mid + 5}" stroke="{INK}" stroke-width="1.5"/>\n')
        body += text(left + plot_w + 12, y + 20, f"{s['correct']}/{s['total']}  ({value:.1%})", 12, INK)
    body += text(40, H - 18, "Removing spaCy changes 0 of 650 outputs: the rules use it only for token annotations, never to choose actions.", 10.5, MUTED)
    desc = "; ".join(f"{data[k]['label']}: {data[k]['correct']}/{data[k]['total']} ({data[k]['correct'] / data[k]['total']:.1%})" for k in order)
    return svg(W, H, "Ablation of the grounding pipeline", desc, body)


def typo_figure():
    typos = json.loads((ROOT / "evaluation/results/ablation.json").read_text(encoding="utf-8"))["typos"]
    if not typos:
        return None
    W, H, left, top, plot_w = 880, 210, 230, 70, 420
    body = text(40, 28, f"One typo in a vocabulary word: exact match on {typos['corrupted']} commands", 15, weight="700")
    body += text(40, 46, "Seed 4 was never inspected. Whiskers are 95% Wilson intervals.", 11, MUTED)
    rows = [("Rules alone", typos["rules_alone"], typos["rules_alone_ci95"], AMBER), ("Rules + “Did you mean” applied", typos["with_suggestion"], typos["with_suggestion_ci95"], GREEN)]
    for pct in range(0, 101, 20):
        x = left + plot_w * pct / 100
        body += f'<line x1="{x}" y1="{top - 6}" x2="{x}" y2="{top + 80}" stroke="{GRID}"/>\n' + text(x, top + 96, f"{pct}%", 10, MUTED, "middle")
    for i, (label, correct, ci, colour) in enumerate(rows):
        y = top + i * 40
        value = correct / typos["corrupted"]
        body += text(left - 12, y + 19, label, 12, INK, "end") + f'<rect x="{left}" y="{y + 6}" width="{plot_w * value:.1f}" height="20" fill="{colour}"/>\n'
        body += (f'<line x1="{left + plot_w * ci[0]:.1f}" y1="{y + 16}" x2="{left + plot_w * ci[1]:.1f}" y2="{y + 16}" stroke="{INK}" stroke-width="1.5"/>\n')
        body += text(left + plot_w + 12, y + 20, f"{correct}/{typos['corrupted']} ({value:.1%})", 12)
    body += text(40, H - 16, "Chosen to stress the system: every command carries a typo in a word the grammar needs. The app only shows a suggestion; it never applies one.", 10.5, MUTED)
    desc = f"Rules alone {typos['rules_alone']}/{typos['corrupted']}; with the suggestion applied {typos['with_suggestion']}/{typos['corrupted']}."
    return svg(W, H, "Typo robustness", desc, body)


def pipeline_figure():
    W, H = 980, 330
    box = lambda x, y, w, h, fill, stroke: f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n'
    arrow = lambda x1, y1, x2, y2, dash="": (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.6" {dash} marker-end="url(#a)"/>\n')
    body = '<defs><marker id="a" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#2d3244"/></marker></defs>\n'
    body += text(30, 28, "WordWorld pipeline: a sentence becomes ordered, inspectable actions", 15, weight="700")
    boxes = [
        (30, 70, 150, 70, "#f3efff", PURPLE, ["Sentence", "+ what “it” means", "(client context)"]),
        (225, 70, 170, 70, "#fff7e6", AMBER, ["Clause splitting", "+ grammar", "(rules, regexes)"]),
        (440, 70, 170, 70, "#fff7e6", AMBER, ["Grounding", "add · remove · recolor", "resize · move · settings"]),
        (655, 70, 140, 70, "#eaf6ee", GREEN, ["Action JSON", "(ordered, exact)"]),
        (840, 70, 110, 70, "#eaf6ee", GREEN, ["Scene", "placement", "+ undo"]),
    ]
    for x, y, w, h, fill, stroke, lines in boxes:
        body += box(x, y, w, h, fill, stroke)
        for k, line in enumerate(lines):
            body += text(x + w / 2, y + 26 + k * 17, line, 12 if k else 13, INK, "middle", "700" if k == 0 else "400")
    for x1, x2 in [(180, 225), (395, 440), (610, 655), (795, 840)]:
        body += arrow(x1, 105, x2, 105)
    # side branches
    body += box(225, 200, 170, 64, "#eef3ff", "#5a7fcf") + text(310, 226, "spaCy annotations", 13, INK, "middle", "700") + text(310, 244, "tokens · POS · dependencies", 11.5, INK, "middle")
    body += arrow(310, 200, 310, 142, 'stroke-dasharray="5 4"')
    body += text(318, 176, "explains, never decides", 10.5, MUTED)
    body += box(440, 200, 170, 64, "#fdeeee", "#cf6f6f") + text(525, 226, "“Did you mean…?”", 13, INK, "middle", "700") + text(525, 244, "edit distance + re-parse", 11.5, INK, "middle")
    body += arrow(525, 200, 525, 142, 'stroke-dasharray="5 4"')
    body += text(533, 176, "only if measurably better", 10.5, MUTED)
    body += box(655, 200, 295, 64, "#f2f2f7", GREY) + text(802, 226, "Dependency baseline (comparison only)", 13, INK, "middle", "700") + text(802, 244, "reads the same actions from spaCy arcs · never applied", 11, INK, "middle")
    body += text(30, H - 18, "Solid arrows drive the world. Dashed arrows are explanations or suggestions that a person can ignore.", 10.5, MUTED)
    desc = ("A sentence, with client context for 'it' and 'them', passes through clause splitting and rule grammar, then grounding into ordered action JSON, "
            "then the scene. spaCy annotations explain but never decide; typo suggestions appear only when a re-parse is measurably better; "
            "a dependency baseline is shown for comparison and never applied.")
    return svg(W, H, "WordWorld pipeline", desc, body)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    figures = {"fig-pipeline.svg": pipeline_figure(), "fig-accuracy.svg": accuracy_figure(), "fig-ablation.svg": ablation_figure(), "fig-typos.svg": typo_figure()}
    for name, content in figures.items():
        if content:
            (OUT / name).write_text(content, encoding="utf-8", newline="\n")
            print("wrote", OUT / name)


if __name__ == "__main__":
    main()
