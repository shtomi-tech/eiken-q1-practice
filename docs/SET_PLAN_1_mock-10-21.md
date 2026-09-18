# 英検1級 セット収録語 選定計画（mock-10 〜 mock-21）

> 出典: ユーザー提供の単語集一覧（Unit1 動詞 / Unit2 名詞 / Unit3 形容詞・副詞 p.106-142 / Unit4 句動詞 p.146-166）。
> 既存 `data/vocab_1_*.json` 全12セット（延べ960語）と lemma 正規化で照合し、重複語は除外済み。
> 各行が1問分の選択肢4語。★は正解語（想定）。問題文・和訳・例文・IPA は実装時に作成する。

## 品詞構成（既存 mock-7〜9 と同一）

1セット = 25問 / 100語: 名詞7問(28語)・動詞7問(28語)・形容詞6問(24語)・副詞1問(4語)・句動詞4問(16語)

## 在庫と割り当て（mock-10 収録分を除く）

| 品詞 | 残語数 | 作れる問数 | 11セットで必要 |
| --- | --- | --- | --- |
| 名詞 | 338 | 84 | 77 |
| 動詞 | 312 | 78 | 77 |
| 形容詞 | 280 | 70 | 66〜68 |
| 副詞 | 44（うち8語はネット調査で補完） | 11 | 11 |
| 句動詞 | 184 | 46 | 44 |

**mock-11〜21 の11セットを割り当てた。全セットで既存 mock-7〜9 と同一の品詞比を維持する。**

単語集の副詞は37語（＝9問分）しかなく2セット分不足したため、下記8語をネット調査（Weblio の語彙レベル表示 12 以上＝英検1級以上）で補完し、mock-20・mock-21 の副詞問に充てた。単語集由来の `haphazardly` は既存データの `haphazard` と重複するため不採用とした。

| 語 | 意味 | 典拠レベル |
| --- | --- | --- |
| gingerly | 慎重に、恐る恐る | えいたんごクイズ「英検1級」 |
| warily | 用心深く | Weblio レベル21 |
| aptly | 適切に、うまく | Weblio レベル12・英検1級以上 |
| doggedly | 粘り強く、頑固に | Weblio レベル16 |
| summarily | 即座に、略式に | Weblio レベル13 |
| wryly | 皮肉っぽく、苦々しげに | Weblio レベル22 |
| conspicuously | 目立って、著しく | Weblio レベル12・英検1級以上 |
| sparingly | 控えめに、節約して | Weblio レベル13 |

## mock-10（確定済み）

### 名詞（Q1-7）

1. ★anecdote / turmoil / larceny / prowess
2. ★backlash / fissure / brevity / tenet
3. ★loophole / skirmish / prelude / morsel
4. ★remorse / euphoria / apathy / zeal
5. ★impediment / precedent / gadget / ambush
6. ★stigma / hoard / deceit / tundra
7. ★hunch / rebuke / servitude / foray

### 動詞（Q8-14）

8. ★eschew / entangle / ransack / garble
9. ★exacerbate / replenish / mitigate / retract
10. ★divulge / baffle / hoist / punctuate
11. ★oust / enlist / saunter / dilate
12. ★corroborate / demoralize / gnaw / splurge
13. ★procrastinate / fumble / coalesce / glean
14. ★preclude / excavate / smuggle / chide

### 形容詞（Q15-20）・副詞（Q21）

15. ★surreptitious / callous / hilarious / redolent
16. ★stringent / vicarious / ambient / palatial
17. ★imprudent / residual / endemic / garish
18. ★congenial / illegible / abject / forensic
19. ★haughty / bereaved / contrived / solvent
20. ★complicit / repugnant / invariable / perverse
21. ★sporadically / blatantly / eloquently / belatedly

### 句動詞（Q22-25）

22. ★rein in / dish out / chip in / tap into
23. ★shrug off / dawn on / wolf down / spruce up
24. ★rule out / jot down / pin down / fend off
25. ★pull off / trail off / harp on / opt for

## mock-11

### 名詞（Q1-7）

1. ★clique / blotch / pinnacle / bounty
2. ★prelate / farce / offshoot / platitude
3. ★caucus / testament / juncture / enmity
4. ★endowment / periphery / deferral / commotion
5. ★genealogy / propensity / extrovert / contention
6. ★cavity / reformation / socialite / fugitive
7. ★velocity / trance / upstart / ember

### 動詞（Q8-14）

8. ★default / revitalize / gargle / amplify
9. ★emancipate / abate / distort / delineate
10. ★whimper / liquidate / flounder / peck
11. ★sanitize / rejuvenate / barter / muster
12. ★abduct / cringe / orchestrate / vanquish
13. ★churn / swirl / fraternize / beguile
14. ★impoverish / tilt / accrue / ruminate

### 形容詞（Q15-20）・副詞（Q21）

15. ★imperative / astronomical / satirical / acrimonious
16. ★conciliatory / derelict / poised / pervasive
17. ★conscientious / venerable / cognizant / equitable
18. ★forlorn / antagonistic / brash / venomous
19. ★nascent / stocky / feasible / commensurate
20. ★momentous / legible / jocular / propitious
21. ★elusively / abysmally / forlornly / nominally

### 句動詞（Q22-25）

22. ★spill over / kick in / muddle through / iron out
23. ★scrimp on / vouch for / nail down / ramp up
24. ★strike off / wash out / lock away / louse up
25. ★lead on / rail against / pep up / stow away

## mock-12

### 名詞（Q1-7）

1. ★adherent / infirmity / speculation / prodigy
2. ★ovation / ebullience / infatuation / swathe
3. ★lassitude / repercussion / surge / chivalry
4. ★laceration / totem / imposition / camaraderie
5. ★sojourn / blight / swamp / avarice
6. ★amiability / opulence / mutation / grind
7. ★mainstay / erudition / consecration / caliber

### 動詞（Q8-14）

8. ★tyrannize / console / grovel / dwindle
9. ★desist / subsidize / perpetuate / satirize
10. ★drizzle / lunge / masquerade / reiterate
11. ★emaciate / salivate / sequester / lubricate
12. ★besiege / remunerate / annotate / venerate
13. ★flex / blanch / repeal / lather
14. ★deviate / stymie / fathom / decipher

### 形容詞（Q15-20）・副詞（Q21）

15. ★frenetic / condescending / lavish / scant
16. ★docile / succinct / pensive / copious
17. ★bombastic / tenacious / anecdotal / malleable
18. ★acrid / appalling / pompous / explicit
19. ★malicious / preposterous / premeditated / erudite
20. ★jaded / posthumous / submissive / inanimate
21. ★daintily / fraudulently / fortuitously / benevolently

### 句動詞（Q22-25）

22. ★coast along / rally around / nibble at / grate on
23. ★cut back / butt in / fork out / nose around
24. ★roll out / pick over / throw back / pass off
25. ★kick around / wallow in / side with / bundle up

## mock-13

### 名詞（Q1-7）

1. ★gorge / duplicity / prudence / conurbation
2. ★insanity / deviation / fallacy / subjugation
3. ★implosion / snag / exponent / remission
4. ★jubilee / tedium / exodus / impulse
5. ★elucidation / ordeal / commutation / reprieve
6. ★collateral / retention / scarcity / solace
7. ★penance / swarm / absurdity / compliance

### 動詞（Q8-14）

8. ★clench / nauseate / deplore / accredit
9. ★conjugate / perturb / converge / forestall
10. ★rumple / repatriate / estrange / commiserate
11. ★rebuff / launder / jumble / desensitize
12. ★abdicate / mangle / germinate / eavesdrop
13. ★vent / prevaricate / slander / catapult
14. ★confiscate / fracture / resuscitate / incapacitate

### 形容詞（Q15-20）・副詞（Q21）

15. ★avid / uptight / uncanny / frivolous
16. ★pragmatic / morbid / skittish / profane
17. ★unequivocal / brazen / intrinsic / flimsy
18. ★dreary / impetuous / tantamount / insufferable
19. ★luminous / recalcitrant / convoluted / disparate
20. ★inalienable / hereditary / culpable / salient
21. ★inadvertently / crucially / horrendously / listlessly

### 句動詞（Q22-25）

22. ★lag behind / while away / mark up / brace for
23. ★pack off / cut across / wash over / toy with
24. ★knock back / drag off / fly at / sail through
25. ★pine for / rig up / bear up / circle back

## mock-14

### 名詞（Q1-7）

1. ★aggravation / abstinence / compunction / vice
2. ★calibration / brawl / redemption / edifice
3. ★hype / quandary / cognition / felony
4. ★mortality / referendum / zest / reproach
5. ★dispensation / diatribe / schism / sanctity
6. ★escapade / epiphany / autocrat / malaise
7. ★traction / grimace / animosity / lesion

### 動詞（Q8-14）

8. ★exterminate / recuperate / immerse / ingratiate
9. ★coerce / waver / hobble / bombard
10. ★ignite / adorn / astound / derail
11. ★mutilate / usurp / wean / lurk
12. ★enthrall / pounce / babble / dribble
13. ★gloat / apprehend / nibble / orient
14. ★retort / instigate / stutter / emboss

### 形容詞（Q15-20）・副詞（Q21）

15. ★luxuriant / profound / ample / vulgar
16. ★bumbling / clairvoyant / crabby / eclectic
17. ★plausible / ubiquitous / frazzled / philanthropic
18. ★stagnant / preemptive / resplendent / wanton
19. ★somber / clandestine / adversarial / barbarous
20. ★ingenious / irate / covert / candid
21. ★stupendously / posthumously / semantically / belligerently

### 句動詞（Q22-25）

22. ★goof off / let on / wear down / mill about
23. ★spin out / bunch up / shell out / fence in
24. ★tear off / stub out / swear in / drag out
25. ★flesh out / bawl out / grind up / leaf through

## mock-15

### 名詞（Q1-7）

1. ★frenzy / subordination / groove / fervor
2. ★ailment / semblance / figment / hindrance
3. ★amenity / hubris / profanity / deposition
4. ★contraption / inundation / anonymity / conjunction
5. ★precept / humiliation / onus / libel
6. ★dowry / fidelity / conglomeration / inhalation
7. ★aversion / augmentation / configuration / perjury

### 動詞（Q8-14）

8. ★assuage / dawdle / drool / debunk
9. ★conjure / budge / impeach / repudiate
10. ★supplant / plagiarize / engulf / articulate
11. ★sever / lampoon / extrapolate / pollinate
12. ★marshal / litigate / collocate / embezzle
13. ★enlighten / harness / demur / shove
14. ★engender / prowl / levitate / sprout

### 形容詞（Q15-20）・副詞（Q21）

15. ★subliminal / flamboyant / abrasive / unwitting
16. ★anemic / brusque / deceased / garrulous
17. ★sordid / plenary / truculent / palatable
18. ★cursory / abortive / inscrutable / illicit
19. ★demure / gallant / untenable / lethargic
20. ★impervious / delirious / prolific / carnivorous
21. ★exponentially / dismally / scrupulously / altruistically

### 句動詞（Q22-25）

22. ★dip into / cast off / head off / dumb down
23. ★egg on / let up on / stand in for / get down to
24. ★load up / storm out / push back / pile into
25. ★glance off / tip off / fizzle out / plow through

## mock-16

### 名詞（Q1-7）

1. ★fiasco / allure / treatise / tatter
2. ★accreditation / delegation / severance / deluge
3. ★latitude / hassle / retaliation / truce
4. ★travesty / spree / credulity / profusion
5. ★knack / zenith / pertinence / capitulation
6. ★predicament / conflagration / throng / cowardice
7. ★acquisition / abstention / inception / statute

### 動詞（Q8-14）

8. ★beseech / ameliorate / preside / bewilder
9. ★bicker / cower / incur / invoke
10. ★recant / intersperse / flaunt / grill
11. ★inoculate / meander / pervade / inculcate
12. ★antagonize / forage / tangle / disconcert
13. ★feign / intercept / languish / coddle
14. ★spurn / segregate / circumvent / petrify

### 形容詞（Q15-20）・副詞（Q21）

15. ★idyllic / putrid / apathetic / deplorable
16. ★conducive / frigid / pallid / innocuous
17. ★desolate / shrewd / menial / dispassionate
18. ★obnoxious / celibate / ephemeral / emblematic
19. ★effusive / ostensible / fervent / buoyant
20. ★placid / quaint / provident / ineligible
21. ★gallantly / vehemently / sheepishly / irreparably

### 句動詞（Q22-25）

22. ★stamp out / whip up / dash off / palm off
23. ★chew over / blurt out / strip out / wave aside
24. ★blend in / paper over / trip up / drown out
25. ★sound out / fuss over / talk down / rack up

## mock-17

### 名詞（Q1-7）

1. ★debutante / concession / bombardment / altercation
2. ★harbinger / poise / incarnation / insinuation
3. ★embargo / bundle / reconnaissance / havoc
4. ★virulence / debris / pleasantry / demarcation
5. ★affront / coercion / respite / inertia
6. ★severity / oration / eviction / regression
7. ★serendipity / emblem / felicity / conveyance

### 動詞（Q8-14）

8. ★avail / imbue / foment / pilfer
9. ★admonish / mar / append / propel
10. ★stifle / span / depose / berate
11. ★decimate / regale / drone / consecrate
12. ★falter / goad / incriminate / detest
13. ★blur / barricade / capitulate / alienate
14. ★align / crumple / chant / perpetrate

### 形容詞（Q15-20）・副詞（Q21）

15. ★fickle / verbose / belligerent / interim
16. ★inveterate / euphoric / efficacious / reticent
17. ★strident / circumspect / delinquent / nonchalant
18. ★cumbersome / poignant / morose / harrowing
19. ★personable / recurrent / astute / defunct
20. ★errant / obtrusive / affable / abhorrent
21. ★enviably / immortally / diversely / impeccably

### 句動詞（Q22-25）

22. ★bowl over / knuckle down / drift off / scoot over
23. ★hole up / carve up / clog up / choke up
24. ★lead up to / step down from / pick up after / fend for
25. ★keel over / ebb away / duck out / stop off

## mock-18

### 名詞（Q1-7）

1. ★partisan / outage / progeny / redress
2. ★suffrage / rampage / rampart / fruition
3. ★acrimony / hegemony / stench / blunder
4. ★rubble / ingenuity / clout / kickback
5. ★tycoon / scruple / memento / protagonist
6. ★parity / inhibition / haven / bureaucrat
7. ★denizen / ruckus / equilibrium / lineage

### 動詞（Q8-14）

8. ★maim / pare / mesmerize / wriggle
9. ★scorn / behold / sabotage / remit
10. ★deface / yield / transpire / adjourn
11. ★accost / parry / fathom / forfeit
12. ★allot / wager / rustle / amble
13. ★scuttle / dangle / allude / galvanize
14. ★lure / elicit / lambaste / plunder

### 形容詞（Q15-20）・副詞（Q21）

15. ★counterfeit / insidious / defamatory / meticulous
16. ★implausible / vacuous / dogmatic / ludicrous
17. ★precarious / lugubrious / banal / nocturnal
18. ★abysmal / elliptical / insubstantial / homely
19. ★adroit / subdued / lurid / trite
20. ★barbaric / detrimental / desultory / derisive
21. ★marginally / bashfully / intently / tenaciously

### 句動詞（Q22-25）

22. ★pass over / dote on / stitch up / whisk away
23. ★rake in / swear by / hinge on / snuff out
24. ★rattle off / live up to / stand out from / zero in on
25. ★come by / chime in / answer back / crouch down

## mock-19

### 名詞（Q1-7）

1. ★stopgap / rationale / asylum / homage
2. ★longevity / rift / adversary / jetty
3. ★temperance / dissipation / infamy / payoff
4. ★charlatan / pundit / agility / vortex
5. ★jurisdiction / rendezvous / feat / layman
6. ★vulgarity / rendition / veracity / snitch
7. ★caricature / onrush / truancy / redolence

### 動詞（Q8-14）

8. ★garnish / suffocate / debase / meddle
9. ★epitomize / satiate / retaliate / purport
10. ★huddle / temper / perish / arbitrate
11. ★exhale / juggle / extricate / improvise
12. ★discard / smear / misconstrue / syndicate
13. ★abscond / avenge / garner / scrounge
14. ★manipulate / reprove / defuse / defraud

### 形容詞（Q15-20）・副詞（Q21）

15. ★opulent / macabre / redundant / obstinate
16. ★irrefutable / gaudy / raucous / sadistic
17. ★prodigious / leery / impalpable / flagrant
18. ★invincible / pitiless / incessant / incremental
19. ★measly / savvy / precipitous / fluorescent
20. ★listless / inflatable / exorbitant / sanguine
21. ★figuratively / diabolically / adamantly / fervently

### 句動詞（Q22-25）

22. ★run up against / look back on / fall in with / simmer down
23. ★horse around / live down / hike up / thumb through
24. ★square off against / gang up on / tear into / get away with
25. ★boil down to / come down on / get back at / smooth over

## mock-20

### 名詞（Q1-7）

1. ★treason / pilgrimage / acolyte / grudge
2. ★prospectus / remuneration / electorate / glint
3. ★bout / consternation / summation / calamity
4. ★stalk / patronage / projectile / concoction
5. ★smirk / contingency / stalwart / dissertation
6. ★premise / interlude / repertoire / reparation
7. ★installment / arson / penchant / gratuity

### 動詞（Q8-14）

8. ★manifest / jeopardize / guzzle / taunt
9. ★slaughter / maroon / scour / inaugurate
10. ★stratify / appall / swindle / instill
11. ★encapsulate / adjudicate / emulate / lob
12. ★reprimand / encumber / advocate / inscribe
13. ★downplay / embolden / siphon / incinerate
14. ★denounce / entice / fetter / demonize

### 形容詞（Q15-20）・副詞（Q21）

15. ★palpable / inept / unkempt / indignant
16. ★aloof / laconic / obsequious / quarrelsome
17. ★sultry / vociferous / arduous / altruistic
18. ★extrinsic / ulterior / contemptible / comatose
19. ★oblique / assiduous / strident / extenuating
20. ★waning / impermeable / generic / succulent
21. ★gingerly / warily / aptly / doggedly

### 句動詞（Q22-25）

22. ★chew out / box up / dispense with / ride on
23. ★level with / shoot for / bulk up / lean on
24. ★suck up to / come in for / leap out at / bear down on
25. ★gain on / weed out / beef up / lash out

## mock-21

### 名詞（Q1-7）

1. ★disclaimer / ramification / stowage / innuendo
2. ★luster / misgiving / yardstick / debacle
3. ★prognosis / paradigm / exhilaration / doctrine
4. ★catalyst / volition / dissidence / finesse
5. ★efficacy / regimen / foliage / timidity
6. ★feasibility / tinge / impeachment / contraband
7. ★propagation / impudence / acquittal / tyranny

### 動詞（Q8-14）

8. ★mingle / precipitate / brandish / elude
9. ★replicate / indulge / inundate / contrive
10. ★covet / cripple / espouse / heave
11. ★impound / embellish / adjoin / hamper
12. ★refute / engross / jiggle / squash
13. ★infest / inflict / incubate / ensue
14. ★verify / relegate / dazzle / squabble

### 形容詞（Q15-20）・副詞（Q21）

15. ★perishable / apolitical / strenuous / prophetic
16. ★fervent / complacent / laborious / incendiary
17. ★ostentatious / antiseptic / infantile / omniscient
18. ★discerning / inquisitive / irascible / exquisite
19. ★intractable / shoddy / furtive / despondent
20. ★reprehensible / adept / volatile / prescient
21. ★summarily / wryly / conspicuously / sparingly

### 句動詞（Q22-25）

22. ★cave in / fire away / mull over / blow away
23. ★crack up / deck out / roll in / play down
24. ★hunker down / scrape by / limber up / snap off
25. ★jockey for / butter up / pore over / ride out

## 未割当（余剰在庫）

- 名詞（30語, うち ordeal は差し替えで使用済み）: enactment, patent, hermit, gimmick, decorum, dungeon, scourge, accomplice, insurgency, protrusion, modulation, ordeal, conscription, curator, immunity, denunciation, forerunner, dissent, proximity, culprit, inflammation, inclination, constriction, partition, allusion, affinity, conflagration, wrath, matrimony, disintegration
- 動詞（4語）: lampoon, inter, perish, avenge
- 形容詞（16語）: atrocious, chivalrous, fanatical, diffident, repulsive, scrumptious, facetious, chronic, perfunctory, languid, tentative, emaciated, poignant, voracious, decrepit, immaculate
- 副詞（0語）: なし
- 句動詞（8句、うち bawl out・butter up は差し替えで使用済み）: burn out, squeeze in, wear in, come by, leaf through, tear into, buy off, strike up

## 差し替え記録

`data/lemmas.json`（全級共有の原形辞書）と衝突した4語を、余剰在庫の同品詞語へ差し替えた。

| 元の語 | 差し替え後 | 箇所 |
| --- | --- | --- |
| nomination | ordeal | mock-13 Q5 |
| scatter | lampoon | mock-14 Q11（正解を sever へ変更） |
| renounce | perish | mock-18 Q10 |
| flourish | avenge | mock-18 Q13 |

既存セットの活用形と実質的に同じ句動詞だった2件も、余剰在庫の句動詞へ差し替えた。

| 元の句 | 差し替え後 | 箇所 | 衝突相手 |
| --- | --- | --- | --- |
| buy off | bawl out | mock-14 Q25 | `bought off`（mock-1） |
| strike up | butter up | mock-19 Q25 | `struck up`（mock-5） |
| gloat over | leaf through | mock-14 Q25 | 同一セット Q13 の動詞 `gloat` と紛らわしい |
| inoculation | conflagration | mock-16 Q6 | 同一セット Q11 の動詞 `inoculate` と紛らわしい |
| virulent | poignant | mock-17 Q18 | 同一セット Q4 の名詞 `virulence` と紛らわしい |
| prone | fathom | mock-18 Q11 | 単語集の動詞ページにある `prone` は形容詞のため |
| creep up on | come by | mock-18 Q25 | 既存 `crept up on` と実質重複 |
| contingent | strident | mock-20 Q19 | 同一セット Q5 の名詞 `contingency` と紛らわしい |
| indulgent | fervent | mock-21 Q16 | 同一セット Q9 の動詞 `indulge` と紛らわしい |
| load up on | tear into | mock-19 Q24 | mock-15 の `loaded up` と同じ句動詞のため |
