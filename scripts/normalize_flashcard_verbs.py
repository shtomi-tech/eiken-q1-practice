"""Apply reviewed display-only verb lemmas from the 2026-10-08 Jev audit.

Does not change questions, vocabulary surfaces, meanings or progress keys.
Run with --apply to update data/lemmas.json; otherwise prints the proposed diff.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Explicitly reviewed English morphology; Jev labels are not applied blindly.
PAIRS = """
committing|commit
adjusting|adjust
betting|bet
made by|be made by
answered for|answer for
applied to|apply to
led to|lead to
kept up|keep up
pretended|pretend
deceived|deceive
decreased|decrease
provided|provide
collapsed|collapse
overcame|overcome
gestured|gesture
functioned|function
making|make
done|do
did|do
putting out|put out
writing down|write down
throwing away|throw away
turning off|turn off
cutting down|cut down
trying out|try out
you required|require
embarrassed|embarrass
thanked|thank
surrendered|surrender
cheered|cheer
piled|pile
spoiled|spoil
bled|bleed
beaten|beat
urged|urge
featured|feature
appealed|appeal
sighed|sigh
opened|open
related|relate
met|meet
came|come
helping|help
waiting|wait
sitting|sit
visiting|visit
referred|refer
admitted|admit
folded|fold
evaluated|evaluate
composed|compose
violated|violate
tracked|track
rotated|rotate
declared|declare
filled|fill
stuck|stick
wasted|waste
meant|mean
spent|spend
has spent|spend
had spent|spend
brought up|bring up
looked over|look over
gave away|give away
carrying over|carry over
cracking down|crack down
wasting away|waste away
heading up|head up
piecing together|piece together
punching out|punch out
stirring up|stir up
reined in|rein in
shrugged off|shrug off
kicked in|kick in
ironed out|iron out
struck off|strike off
led on|lead on
threw back|throw back
lagged behind|lag behind
knocked back|knock back
dragged off|drag off
goofed off|goof off
wore down|wear down
milled about|mill about
tore off|tear off
stubbed out|stub out
stood in for|stand in for
pushed back|push back
stamped out|stamp out
dashed off|dash off
palmed off|palm off
blurted out|blurt out
bowled over|bowl over
knuckled down|knuckle down
drifted off|drift off
doted on|dote on
snuffed out|snuff out
tore into|tear into
chewed out|chew out
came in for|come in for
leapt out at|leap out at
bore down on|bear down on
mulled over|mull over
"""
MAPPING = dict(line.split('|') for line in PAIRS.strip().splitlines())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'data/lemmas.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    mapping = data.setdefault('flashcardDisplayLemmas', {})
    # had was retired with the tense-only Q13 repair on 2026-10-08.
    assert len(MAPPING) == 104
    changed = {}
    for surface, lemma in MAPPING.items():
        old = mapping.get(surface)
        if old == lemma:
            continue
        if old is not None:
            raise ValueError(f'Conflicting existing display mapping: {surface}')
        changed[surface] = lemma
    print(json.dumps({'changes': changed, 'count': len(changed)}, ensure_ascii=False, indent=2))
    if args.apply:
        mapping.update(changed)
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))

if __name__ == '__main__':
    main()
