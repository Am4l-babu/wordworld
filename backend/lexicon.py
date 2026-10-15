"""Fixed vocabulary and surface patterns for the grounding grammar."""
from __future__ import annotations

import re

ALIASES = {
    "house": ["house", "houses", "home", "homes", "cottage", "cottages", "hut", "huts", "cabin", "cabins", "village", "villages", "town", "towns"],
    "tree": ["tree", "trees", "forest", "forests", "woods", "woodland", "woodlands"],
    "lake": ["lake", "lakes", "pond", "ponds"],
    "river": ["river", "rivers", "stream", "streams", "creek", "creeks"],
    "bridge": ["bridge", "bridges"],
    "road": ["road", "roads", "path", "paths", "trail", "trails", "street", "streets"],
    "flower": ["flower", "flowers", "garden", "gardens", "blossom", "blossoms"],
    "mountain": ["mountain", "mountains", "hill", "hills", "peak", "peaks"],
    "tower": ["tower", "towers", "lighthouse", "lighthouses"],
    "castle": ["castle", "castles", "fortress", "fortresses"],
    "rock": ["rock", "rocks", "stone", "stones", "boulder", "boulders"],
}
WORD_TO_TYPE = {word: kind for kind, words in ALIASES.items() for word in words}
COLLECTIVE_NOUNS = {"village", "town", "forest", "woods", "woodland", "garden"}
SINGULAR_NOUNS = {word for word in WORD_TO_TYPE if not word.endswith("s") and word not in COLLECTIVE_NOUNS}
ENTITY_RE = re.compile(r"\b(" + "|".join(sorted(map(re.escape, WORD_TO_TYPE), key=len, reverse=True)) + r")\b", re.I)
PRONOUN_RE = re.compile(r"\b(?:it|them)\b", re.I)
MENTION_RE = re.compile(ENTITY_RE.pattern + r"|\b(?:it|them)\b", re.I)
NUMBER_VALUES = dict(zip(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety".split(),
    list(range(20)) + list(range(20, 100, 10)),
))
COUNT_WORDS = {**NUMBER_VALUES, "a": 1, "an": 1, "couple": 2, "few": 3, "several": 4}
UNITS = "one|two|three|four|five|six|seven|eight|nine"
BASE_NUMBER = rf"(?:(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[- ](?:{UNITS}))?|{'|'.join(list(NUMBER_VALUES)[:20])})"
CARDINAL = rf"(?:(?:{BASE_NUMBER})\s+(?:hundred|thousand)(?:\s+(?:and\s+)?{BASE_NUMBER})?|hundred|thousand|{BASE_NUMBER})"
NUMERAL = rf"(?:[+-]?\d+(?:\.\d+)?|{CARDINAL})"
NUMBER_RE = re.compile(
    rf"(?<!\w)(?:(?P<half>half\s+(?:a\s+)?dozen)|(?:(?P<multiplier>{NUMERAL}|a|an)\s+)?(?P<group>dozens?|pairs?|couples?)|(?P<number>{NUMERAL})|(?P<approx>few|several)|(?P<article>a|an))\b", re.I
)
UNKNOWN_QUANTITY_WORDS = {'many', 'some', 'lots', 'numerous', 'million', 'billion', 'quarter'}
UNKNOWN_QUANTITY_RE = re.compile(r"\b(?:" + '|'.join(sorted(UNKNOWN_QUANTITY_WORDS)) + r")\b", re.I)
COLORS = ["red", "blue", "yellow", "pink", "purple", "green", "orange", "white"]
COLOR_RE = re.compile(r"\b(" + "|".join(COLORS) + r")\b", re.I)
RELATION_PATTERNS = [
    ("left", r"\b(?:to the left of|left of|west of)\b"),
    ("right", r"\b(?:to the right of|right of|east of)\b"),
    ("above", r"\b(?:above|behind|north of|at the back of)\b"),
    ("below", r"\b(?:below|in front of|south of)\b"),
    ("near", r"\b(?:beside|next to|near|by|closer to|close to|around the edge of|around|along)\b"),
    ("between", r"\bbetween\b"),
    ("across", r"\b(?:across|over|spanning|crossing)\b"),
    ("inside", r"\b(?:inside|within|in the middle of|in the center of)\b"),
]
ADD_PATTERN = r"add|build|create|place|put|plant|grow|make|draw|generate|insert|show|there (?:is|are)|i want|give me"
REMOVE_PATTERN = r"remove|delete|erase|destroy|cut down|clear away|get rid of"
RESET_PATTERN = r"reset|clear (?:everything|the world|the map)|start over|new world"
PAINT_VERBS = r"paint|colou?r|recolou?r|dye|change\s+the\s+colou?r\s+of"
MOVE_VERBS = r"move|shift|relocate|slide|drag"
RESIZE_VERBS = r"enlarge|shrink|resize"
# These verbs also create objects or switch weather; they edit only with a definite target and a new color or size.
CHANGE_VERBS = r"make|turn|change"
EDIT_BREAK_PATTERN = rf"{PAINT_VERBS}|{MOVE_VERBS}|{RESIZE_VERBS}|change|turn\s+(?:it|them|the)"
PAINT_VERBS = r"paint|colou?r|recolou?r|dye|change\s+the\s+colou?r\s+of"
MOVE_VERBS = r"move|shift|relocate|slide|drag"
RESIZE_VERBS = r"enlarge|shrink|resize"
# These verbs also create objects or switch weather; they edit only with a definite target and a new color or size.
CHANGE_VERBS = r"make|turn|change"
EDIT_BREAK_PATTERN = rf"{PAINT_VERBS}|{MOVE_VERBS}|{RESIZE_VERBS}|change|turn\s+(?:it|them|the)"
PAINT_VERBS = r"paint|colou?r|recolou?r|dye|change\s+the\s+colou?r\s+of"
MOVE_VERBS = r"move|shift|relocate|slide|drag"
RESIZE_VERBS = r"enlarge|shrink|resize"
# These verbs also create objects or switch weather; they edit only with a definite target and a new color or size.
CHANGE_VERBS = r"make|turn|change"
EDIT_BREAK_PATTERN = rf"{PAINT_VERBS}|{MOVE_VERBS}|{RESIZE_VERBS}|change|turn\s+(?:it|them|the)"
PRESERVE_PATTERN = r"keep|leave|preserve|retain|protect|avoid"
OPERATION_RE = re.compile(rf"\b(?P<remove>{REMOVE_PATTERN})\b|\b(?P<reset>{RESET_PATTERN})\b|\b(?P<preserve>{PRESERVE_PATTERN})\b|\b(?P<add>{ADD_PATTERN})\b", re.I)
WEATHER_SWITCH_PATTERN = r'(?:turn|switch)\s+(?:(?:the\s+)?(?:rain|snow)\s+(?:on|off)|(?:on|off)\s+(?:the\s+)?(?:rain|snow))'
WEATHER_SWITCH_RE = re.compile(r'\b(?:turn|switch)\s+(?:(?:the\s+)?(?P<before>rain|snow)\s+(?P<after_state>on|off)|(?P<state>on|off)\s+(?:the\s+)?(?P<after>rain|snow))\b', re.I)
WEATHER_STOP_PATTERN = r'(?:stop|end)\s+(?:the\s+)?(?:rain|snow|storm|shower|raining|snowing)'
WEATHER_STOP_RE = re.compile(r'\b' + WEATHER_STOP_PATTERN + r'\b', re.I)
CLAUSE_BREAK_RE = re.compile(
    rf"[;!?,]+|(?<!\d)\.|\.(?!\d)|\b(?:and then|then)\b|\b(?:and|but)\s+(?=(?:(?:do not|don't|never)\s+)?(?:{ADD_PATTERN}|{REMOVE_PATTERN}|{RESET_PATTERN}|{PRESERVE_PATTERN}|{WEATHER_SWITCH_PATTERN}|{WEATHER_STOP_PATTERN}|{EDIT_BREAK_PATTERN})\b)", re.I
)
NEGATION_RE = re.compile(r"\b(?:no|not|don't|do not|never|without|can't|cannot|shouldn't|mustn't|won't|wouldn't|couldn't)\b", re.I)
MATCH_TRANSLATION = str.maketrans({'\u2018': "'", '\u2019': "'", '\u02bc': "'", '\u2212': '-', '\u2010': '-', '\u2011': '-', '\u2013': '-'})
MAX_PER_COMMAND = 16


PASSIVE_ADVERBS = r'(?:(?:already|recently|just|newly|previously|freshly)\s+){0,2}'
POST_COLOR_RE = re.compile(
    r'\s*,?\s*(?:'
    r'(?:(?:that|which)\s+)?(?:is|are)\s+(?P<predicate>' + '|'.join(COLORS) + r')\b|'
    r'(?:with|having|(?:that|which)\s+(?:has|have))\s+(?:(?:a|an|the)\s+)?(?P<before>' + '|'.join(COLORS) + r')\s+(?P<part_before>roofs?|leaves|foliage|petals?)\b|'
    r'(?:whose|with|having|(?:that|which)\s+(?:has|have))\s+(?:(?:a|an|the)\s+)?(?P<part_after>roofs?|leaves|foliage|petals?)\s+'
    r'(?:(?:(?:that|which)\s+)?(?:is|are)\s+' + PASSIVE_ADVERBS + r'(?:(?:painted|colou?red)\s+)?|(?:(?:that|which)\s+)?(?:will|shall)\s+' + PASSIVE_ADVERBS + r'(?:be|have\s+' + PASSIVE_ADVERBS + r'been)\s+' + PASSIVE_ADVERBS + r'(?:painted|colou?red)\s+|(?:(?:that|which)\s+)?(?:has|have|had)\s+' + PASSIVE_ADVERBS + r'been\s+' + PASSIVE_ADVERBS + r'(?:painted|colou?red)\s+|(?:painted|colou?red)\s+)'
    r'(?P<after>' + '|'.join(COLORS) + r')\b|'
    r'(?:in\s+)?(?P<bare>' + '|'.join(COLORS) + r')\b)', re.I)
COLOR_PARTS = {'house': {'roof', 'roofs'}, 'tree': {'leaves', 'foliage'}, 'flower': {'petal', 'petals'}}
POST_QUANTITY_RE = re.compile(r'\s*,?\s*(?P<phrase>[\w+.-]+(?:\s+[\w+.-]+){0,7}?)\s+(?:of\s+them|in\s+(?:total|all)|total|altogether)\b', re.I)
TOTAL_OF_PREFIX_RE = re.compile(r'\s*[, :]?\s*(?:(?:not|no|never|without)\s+)?(?:a|the)\s+total\s+of\s+', re.I)
POST_QUANTITY_WORDS = set(COUNT_WORDS) | {'exactly','dozen','dozens','pair','pairs','couples','half','of','hundred','thousand','and','or','to','not'} | UNKNOWN_QUANTITY_WORDS


GROUP_SIZES = {'small','large','little','tiny','cozy','big','tall','short'}
GROUP_MODIFIER_RE = re.compile(r'\s+(' + '|'.join(sorted(GROUP_SIZES | set(COLORS))) + r')\b', re.I)
