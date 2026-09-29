# 暗記カード語源の分類と品質点検

`scripts/classify_word_origins.py` によるルール分類の結果（対象 2787語 = `data/word_origins.json` の全件）。
再生成: `python scripts/classify_word_origins.py --report docs/WORD_ORIGIN_CLASSIFICATION.md`。
語ごとの結果は `out/word-origin-classes.csv`（gitignore 対象）に出る。

## 系統（lineage）

語源をさかのぼった最も古い系統。再調査台帳の originLanguage・historicalPath と A型語根の由来を優先し、
表示文と合わせて最も古い系統を採る。ゲルマン系と古典語系の要素を＋で組み合わせた語（dead＋line など）は mixed、
英語内部の派生・複合しか書かれていない語は english。french_non_latin はフランス語より前の系統が書かれていない語。

| ラベル | 語数 | 割合 |
| --- | ---: | ---: |
| latin | 1514 | 54.3% |
| germanic | 399 | 14.3% |
| french_non_latin | 385 | 13.8% |
| english | 336 | 12.1% |
| greek | 132 | 4.7% |
| other | 14 | 0.5% |
| mixed | 7 | 0.3% |

## なりたち（formation）

判定順: unclear → imitative → eponym → shortening → 句（compound）→ 接辞＋語根 → 複合 → 意味の転用 → 借用。

| ラベル | 語数 | 割合 |
| --- | ---: | ---: |
| borrowing | 1194 | 42.8% |
| affix_root | 1047 | 37.6% |
| semantic_shift | 275 | 9.9% |
| unclear | 229 | 8.2% |
| compound | 19 | 0.7% |
| shortening | 12 | 0.4% |
| imitative | 9 | 0.3% |
| eponym | 2 | 0.1% |

## 系統 × なりたち

| lineage \ formation | borrowing | affix_root | semantic_shift | unclear | compound | shortening | imitative | eponym |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| latin | 574 | 794 | 133 | 3 | 2 | 8 |  |  |
| germanic | 212 | 91 | 84 | 4 | 1 | 1 | 6 |  |
| french_non_latin | 338 | 21 | 21 | 1 | 2 |  | 2 |  |
| english |  | 78 | 20 | 221 | 13 | 3 | 1 |  |
| greek | 52 | 60 | 17 |  | 1 |  |  | 2 |
| other | 14 |  |  |  |  |  |  |  |
| mixed | 4 | 3 |  |  |  |  |  |  |

## A型・B型 × なりたち

| type \ formation | borrowing | affix_root | semantic_shift | unclear | compound | shortening | imitative | eponym |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B | 1194 | 145 | 275 | 229 | 19 | 10 | 9 | 2 |
| A |  | 902 |  |  |  | 2 |  |  |

## 品質フラグ

| フラグ | 語数 | 意味 |
| --- | ---: | --- |
| bogus_source | 53 | 語源でない語（the・a など）・言語名・接頭辞だけを「英語 X に由来」と書いている |
| circular | 150 | 見出し語自身・原形・派生語を挙げるだけで語源になっていない |
| inflected_key | 243 | キーが原形でない（「原形Xからの語形変化」） |
| no_arrow | 0 | 現在の意味への「→」がない |
| low_confidence | 34 | 再調査台帳の confidence が low |
| legacy | 230 | 再調査台帳で未再調査 |

### bogus_source（53語）

| 語 | 導出文 |
| --- | --- |
| tundra | 英語 Russianに由来。 → ツンドラ、凍土帯 |
| hoard | 英語 theに由来。 → 蓄え、隠し財産 |
| ransacked | 英語 aに由来。原形ransackからの語形変化。 → 荒らし回った、くまなく探した |
| enlisted | 英語 en-に由来（由来には不確かな点がある）。原形enlistからの語形変化。 → (協力を)得た、入隊させた |
| garish | 英語 obsoleteに由来（由来には不確かな点がある）。 → けばけばしい、派手すぎる |
| illegible | 英語 assimilatedに由来。 → 読めない、判読できない |
| pecked | 英語 Middleに由来（由来には不確かな点がある）。原形peckからの語形変化。 → (くちばしで)つついた |
| rejuvenated | 英語 re-に由来。原形rejuvenateからの語形変化。 → 若返らせた、活気づけた |
| cringed | 英語 causativeに由来。原形cringeからの語形変化。 → 身がすくんだ、縮こまった |
| brash | 英語 aに由来（由来には不確かな点がある）。 → 生意気な、無遠慮な |
| totem | 英語 Algonquianに由来。 → トーテム、象徴 |
| scant | 英語 aに由来（由来には不確かな点がある）。 → わずかな、乏しい |
| scarcity | 英語 Oldに由来。 → 不足、欠乏 |
| mangled | 英語 Dutchに由来。原形mangleからの語形変化。 → ずたずたにした、めちゃくちゃにした |
| uncanny | 英語 un-に由来。 → 不気味なほどの、驚くほどの |
| skittish | 英語 Scandinavianに由来（由来には不確かな点がある）。 → (馬などが)おびえやすい、落ち着かない |
| unequivocal | 英語 un-に由来。 → 明確な、あいまいでない |
| brazen | 英語 brに由来（由来には不確かな点がある）。 → 厚かましい、ずうずうしい |
| lurked | 英語 Scandinavianに由来（由来には不確かな点がある）。原形lurkからの語形変化。 → 潜んだ、待ち伏せた |
| enthralled | 英語 en-に由来。原形enthrallからの語形変化。 → 魅了した |
| gloated | 英語 aに由来。原形gloatからの語形変化。 → 勝ち誇った、いい気になった |
| inhalation | 英語 pastに由来。 → 吸入 |
| sprouted | 英語 theに由来。原形sproutからの語形変化。 → 芽を出した |
| untenable | 英語 un-に由来。 → 擁護できない、成り立たない |
| tatter | 英語 aに由来。 → ぼろ切れ |
| knack | 英語 orに由来（由来には不確かな点がある）。 → こつ、才覚 |
| cowered | 英語 Middleに由来。原形cowerからの語形変化。 → 縮こまった、すくんだ |
| bickered | 英語 theに由来（由来には不確かな点がある）。原形bickerからの語形変化。 → 口論した、言い争った |
| faltered | 英語 aに由来（由来には不確かな点がある）。原形falterからの語形変化。 → ためらった、揺らいだ |
| insufferable | 英語 in-に由来。 → 我慢できない、鼻持ちならない |
| harrowing | 英語 presentに由来。 → 痛ましい、悲惨な |
| outage | 英語 outに由来。 → 停電、供給停止 |
| kickback | 英語 theに由来。 → リベート、不正な謝礼 |
| tycoon | 英語 Japaneseに由来。 → 大立者、実業界の大物 |
| haven | 英語 Oldに由来（由来には不確かな点がある）。 → 避難所、安息の地 |
| wriggle | 英語 Middleに由来。 → 身をよじる、くねくね動く |
| yielded | 英語 theに由来。原形yieldからの語形変化。 → 生み出した、譲った |
| fathomed | 英語 aに由来。原形fathomからの語形変化。 → (真意などを)理解した |
| dangle | 英語 Scandinavianに由来（由来には不確かな点がある）。 → ぶら下げる、ぶら下がる |
| implausible | 英語 assimilatedに由来。 → ありそうもない、信じがたい |
| homage | 英語 cに由来。 → 敬意、賛辞 |
| rift | 英語 aに由来。 → 亀裂、不和 |
| debase | 英語 de-に由来。 → 価値を落とす、卑しめる |
| huddled | 英語 Lowに由来。原形huddleからの語形変化。 → 身を寄せ合った |
| scrounged | 英語 dialectalに由来（由来には不確かな点がある）。原形scroungeからの語形変化。 → かき集めた、せしめた |
| macabre | 英語 Oldに由来（由来には不確かな点がある）。 → 不気味な、死を思わせる |
| gaudy | 英語 theに由来（由来には不確かな点がある）。 → けばけばしい、派手な |
| leery | 英語 dialectalに由来（由来には不確かな点がある）。 → 警戒している、疑っている |
| impound | 英語 assimilatedに由来。 → 押収する、留置する |
| squabbled | 英語 aに由来。原形squabbleからの語形変化。 → つまらぬ口論をした |
| apolitical | 英語 a-に由来。 → 政治に無関心な、非政治的な |
| shoddy | 英語 theに由来（由来には不確かな点がある）。 → 粗悪な、いいかげんな |
| done | 英語 doの過去分詞形。 → 終えた、済んだ |

### circular（150語）

| 語 | 導出文 |
| --- | --- |
| rebuke | 英語 rebukeに由来。 → 叱責、非難 |
| hunch | 英語 hunchに由来。 → 勘、直感 |
| garbled | 英語 garbleに由来。 → (内容を)ゆがめた、不明瞭にした |
| baffled | 英語 baffleに由来。原形baffleからの語形変化。 → 当惑させた |
| sauntered | 英語 saunterに由来。原形saunterからの語形変化。 → ぶらぶら歩いた |
| splurged | 英語 splurgeに由来。原形splurgeからの語形変化。 → 大金を使った、散財した |
| fumbled | 英語 fumbleに由来。原形fumbleからの語形変化。 → 手探りした、しくじった |
| smuggled | 英語 smuggleに由来。原形smuggleからの語形変化。 → 密輸した |
| forensic | 英語 forensicに由来。 → 法医学の、犯罪科学の |
| blatantly | 英語 blatantに由来。原形blatantからの語形変化。 → 露骨に、あからさまに |
| blotch | 英語 blotchに由来（由来には不確かな点がある）。 → しみ、斑点 |
| caucus | 英語 caucusに由来。 → 党員集会、幹部会 |
| socialite | 英語 socialに由来（由来には不確かな点がある）。 → 社交界の名士 |
| defaulted | 英語 defaultに由来。原形defaultからの語形変化。 → (債務を)履行しなかった |
| gargled | 英語 gargleに由来。原形gargleからの語形変化。 → うがいをした |
| emancipated | 英語 emancipateに由来。 → 解放した |
| orchestrated | 英語 orchestrationに由来。原形orchestrateからの語形変化。 → 画策した、周到に組織した |
| abducted | 英語 abductionに由来。原形abductからの語形変化。 → 誘拐した、拉致した |
| swirled | 英語 swirlに由来。原形swirlからの語形変化。 → 渦を巻いた |
| churned | 英語 churnに由来。原形churnからの語形変化。 → 激しくかき回した、泡立てた |
| cognizant | 英語 cognizanceに由来。 → 認識している、気づいている |
| blight | 英語 blightに由来。 → (植物の)病害、荒廃の原因 |
| swamp | 英語 swampに由来。 → 沼地、湿地 |
| grind | 英語 grindに由来。 → 骨の折れる単調な仕事 |
| consoled | 英語 consolに由来。原形consolからの語形変化。 → 慰めた |
| groveled | 英語 grovelingに由来（由来には不確かな点がある）。原形grovelからの語形変化。 → 卑屈にへつらった |
| masqueraded | 英語 masqueradeに由来。原形masqueradeからの語形変化。 → (~の)ふりをした、仮装した |
| emaciated | 英語 emaciateに由来。 → (衰弱して)やせ細らせた |
| stymie | 英語 stymieに由来（由来には不確かな点がある）。 → 妨害する、行き詰まらせる |
| condescending | 英語 condescendに由来。 → 見下すような、恩着せがましい |
| lavish | 英語 lavishに由来。 → 豪華な、気前のよい |
| deviation | 英語 deviateに由来。 → 逸脱、偏差 |
| snag | 英語 snagに由来。 → 思わぬ障害、支障 |
| implosion | 英語 implosionに由来。 → 内部破裂、内向きの崩壊 |
| elucidation | 英語 elucidateに由来。 → 解明、説明 |
| reprieve | 英語 reprieveに由来。 → 執行猶予、一時的な救済 |
| collateral | 英語 collateralに由来。 → 担保 |
| nauseated | 英語 nauseat-に由来。原形nauseateからの語形変化。 → 吐き気を催させた |
| accredited | 英語 accreditに由来。 → 認可した、公認した |
| clenched | 英語 clenchに由来。原形clenchからの語形変化。 → (拳や歯を)固く握りしめた |
| perturbed | 英語 perturbに由来。 → 動揺させた、乱した |
| jumbled | 英語 jumbleに由来。原形jumbleからの語形変化。 → ごちゃ混ぜにした |
| desensitized | 英語 desensitizeに由来。原形desensitizeからの語形変化。 → 鈍感にした、感覚を麻痺させた |
| eavesdropped | 英語 eavesdropperに由来。原形eavesdropからの語形変化。 → 立ち聞きした、盗み聞きした |
| catapulted | 英語 catapultに由来。原形catapultからの語形変化。 → 急に押し上げた、投射した |
| fractured | 英語 fractureに由来。原形fractureからの語形変化。 → 骨折させた、ひびを入れた |
| flimsy | 英語 flimsyに由来（由来には不確かな点がある）。 → 薄っぺらな、根拠の弱い |
| salient | 英語 salientに由来。 → 顕著な、際立った |
| calibration | 英語 calibrateに由来。 → 較正、目盛り調整 |
| brawl | 英語 brawlに由来。 → 乱闘、けんか |
| quandary | 英語 quandaryに由来（由来には不確かな点がある）。 → 板挟み、窮地 |
| hobbled | 英語 hobbleに由来。原形hobbleからの語形変化。 → 足を引きずって歩いた、動きを妨げた |
| babbled | 英語 babbleに由来。原形babbleからの語形変化。 → わけもなくしゃべった |
| dribbled | 英語 dribbleに由来。原形dribbleからの語形変化。 → したたらせた、ドリブルした |
| nibbled | 英語 nibbleに由来。原形nibbleからの語形変化。 → 少しずつかじった |
| oriented | 英語 orientに由来。 → (方向づけて)適応させた、向けた |
| bumbling | 英語 bumbleに由来。原形bumbleからの語形変化。 → へまばかりする、不器用な |
| clairvoyant | 英語 clairvoyantに由来。 → 透視力のある、予知能力のある |
| frazzled | 英語 frazzleに由来。原形frazzleからの語形変化。 → 疲れ果てた、いらいらした |
| wanton | 英語 wantonに由来。 → 理由のない、放埒な |
| frenzy | 英語 frenzyに由来。 → 熱狂、逆上 |
| groove | 英語 grooveに由来。 → 溝、決まりきったやり方 |
| hindrances | 英語 hindrenに由来。原形hindranceからの語形変化。 → 妨げ、障害 |
| libel | 英語 libelに由来。 → 文書による名誉毀損 |
| dawdle | 英語 dawdleに由来（由来には不確かな点がある）。 → のろのろする、ぐずぐずする |
| drool | 英語 droolに由来。 → よだれを垂らす |
| plagiarized | 英語 plagiaryに由来。原形plagiarizeからの語形変化。 → 盗用した、剽窃した |
| articulated | 英語 articulateに由来。 → 明確に述べた |
| pollinate | 英語 pollinationに由来。 → 受粉させる |
| marshaled | 英語 marshalに由来。原形marshalからの語形変化。 → 整列させた、結集した |
| enlightened | 英語 enlightenに由来。 → 啓発した、教え導いた |
| shoved | 英語 shoveに由来。原形shoveからの語形変化。 → 押しのけた、乱暴に押した |
| prowled | 英語 prowlに由来（由来には不確かな点がある）。原形prowlからの語形変化。 → (獲物を求めて)うろついた |
| anemic | 英語 anemicに由来。 → 貧血の、活気のない |
| deceased | 英語 deceaseに由来。 → 死亡した、故人の |
| gallant | 英語 gallantに由来。 → 勇敢な、礼儀正しい |
| accreditation | 英語 accreditに由来。 → 認定、公認 |
| deluge | 英語 delugeに由来。 → 大洪水、殺到 |
| hassle | 英語 hassleに由来。 → 面倒、いざこざ |
| throng | 英語 throngに由来。 → 群衆 |
| ameliorated | 英語 ameliorationに由来（由来には不確かな点がある）。原形ameliorateからの語形変化。 → 改善した、緩和した |
| bewildered | 英語 bewilderに由来。 → 当惑させた |
| flaunted | 英語 flauntに由来。原形flauntからの語形変化。 → 見せびらかした |
| grilled | 英語 grillに由来。原形grillからの語形変化。 → 厳しく問いただした、焼いた |
| meandered | 英語 meanderに由来（由来には不確かな点がある）。原形meanderからの語形変化。 → 曲がりくねって進んだ |
| tangled | 英語 tangleに由来。原形tangleからの語形変化。 → もつれさせた |
| intercepted | 英語 interceptに由来。原形interceptからの語形変化。 → 途中で捕らえた、傍受した |
| petrified | 英語 petrifyに由来。 → すくませた、石化させた |
| shrewd | 英語 shreweに由来。 → 抜け目のない、鋭い |
| menial | 英語 menialに由来。 → 単調で低賃金の、卑しい |
| desolate | 英語 desolateに由来。 → 荒涼とした、寂れた |
| ephemeral | 英語 ephemeralに由来。 → つかの間の、はかない |
| affront | 英語 affrontに由来。 → 侮辱 |
| goaded | 英語 goadに由来。原形goadからの語形変化。 → 駆り立てた、けしかけた |
| blurred | 英語 blurに由来。原形blurからの語形変化。 → ぼやけさせた、あいまいにした |
| barricaded | 英語 barricadeに由来。原形barricadeからの語形変化。 → バリケードでふさいだ |
| partisan | 英語 partisanに由来。 → 熱烈な支持者、パルチザン |
| rampage | 英語 rampageに由来。 → 暴れ回ること |
| blunder | 英語 blunderに由来。 → 大失策 |
| clout | 英語 cloutに由来（由来には不確かな点がある）。 → 影響力、権勢 |
| scruple | 英語 scrupleに由来。 → 良心のとがめ、ためらい |
| ruckus | 英語 ruckusに由来（由来には不確かな点がある）。 → 騒動、大騒ぎ |
| mesmerize | 英語 mesmerismに由来。 → 魅了する、うっとりさせる |
| sabotage | 英語 sabotageに由来。 → 破壊工作をする、妨害する |
| wagered | 英語 wagerに由来。原形wagerからの語形変化。 → 賭けた |
| rustled | 英語 rustleに由来。原形rustleからの語形変化。 → かさかさ音を立てた、家畜を盗んだ |
| lured | 英語 lureに由来。原形lureからの語形変化。 → おびき寄せた、誘い込んだ |
| plundered | 英語 plunderに由来。原形plunderからの語形変化。 → 略奪した |
| voracious | 英語 voraciousに由来。 → 貪欲な、大食の |
| subdued | 英語 subdueに由来。 → 控えめな、元気のない |
| detrimental | 英語 detrimentalに由来。 → 有害な、不利益な |
| rendezvous | 英語 rendezvousに由来。 → 待ち合わせ、会合 |
| snitch | 英語 snitchに由来（由来には不確かな点がある）。 → 密告者 |
| caricature | 英語 caricatureに由来。 → 風刺画、戯画化 |
| garnish | 英語 garnishに由来。 → (料理を)飾る、添える |
| tempered | 英語 temperに由来。 → 和らげた、鍛えた |
| garnered | 英語 garnerに由来。原形garnerからの語形変化。 → (支持などを)集めた |
| manipulate | 英語 manipulationに由来。 → 操作する、巧みに操る |
| sadistic | 英語 sadisticに由来。 → 加虐的な、残忍な |
| grudge | 英語 grudgeに由来。 → 恨み、遺恨 |
| glint | 英語 glintに由来。 → きらめき、輝き |
| smirk | 英語 smirkに由来。 → 薄ら笑い、にやにや笑い |
| premise | 英語 premiseに由来。 → 前提 |
| guzzle | 英語 guzzleに由来。 → がぶ飲みする、大量消費する |
| taunt | 英語 tauntに由来。 → あざける、なじる |
| slaughter | 英語 slaughterに由来。 → 虐殺する、食肉処理する |
| swindle | 英語 swindlerに由来。 → だまし取る、詐取する |
| advocate | 英語 advocateに由来。 → 主張する、擁護する |
| siphon | 英語 siphonに由来。 → 吸い上げる、抜き取る |
| scrumptious | 英語 scrumptiousに由来。 → とてもおいしい |
| waning | 英語 waningに由来。 → 衰えつつある、欠けていく |
| sparingly | 英語 sparingに由来。 → 控えめに、節約して |
| catalyst | 英語 catalysisに由来。 → 触媒、きっかけ |
| finesse | 英語 finesseに由来。 → 巧妙さ、手際のよさ |
| precipitate | 英語 precipitationに由来。 → 引き起こす、早める |
| cripple | 英語 crippleに由来。 → 機能を損なう、不自由にする |
| heave | 英語 heaveに由来。 → 持ち上げる、投げる |
| hamper | 英語 hamperに由来（由来には不確かな点がある）。 → 妨げる、邪魔する |
| dazzled | 英語 dazzleに由来。原形dazzleからの語形変化。 → 目をくらませた、感嘆させた |
| discerning | 英語 discernに由来。 → 見識のある、目の肥えた |
| admitted | 英語 admitの過去分詞形。 → 認めた |
| composed | 英語 composeの過去分詞形。 → 構成した、作曲した |
| embarrassed | 英語 embarrassの過去分詞形。 → 恥ずかしい思いをさせた |
| evaluated | 英語 evaluateの過去形・過去分詞形。evaluate自体は evaluationからの逆成語とされる → 評価した |
| pretended | 英語 pretendの過去分詞形。 → ふりをした |
| provided | 英語 provideの過去分詞形。 → 提供した、与えた |
| related | 英語 relateの過去分詞形。 → 関係づけた、関連した |
| rotated | rotationから逆成された英語 rotateの過去形・過去分詞形 → 回転させた、交代した |
| spoiled | 英語 spoilの過去分詞形。 → 腐った、だめになった |
| wasted | 英語 wasteの過去分詞形。 → 無駄にした |

### low_confidence（34語）

| 語 | 導出文 |
| --- | --- |
| dodge | 語源・初期の意味が不確かな語。急に身をかわす動きから → 素早く避ける |
| whim | 突然浮かぶ思いつきや気まぐれな空想から → 気まぐれ |
| blister | 皮膚にできる液体を含んだふくらみから → 水ぶくれ |
| trickle | 液体が小さく途切れた流れとなって落ちることから → 少しずつ流れた |
| flout | 語源不詳。中英語 flowten（笛を吹く）や中期オランダ語 fluyten（笛を吹く、嘲る）との関連説がある → 公然と無視した、軽視した |
| spar | 動詞spar（打ち合う、軽く争う）は中英語 sparren（打つ、突く）から発達したが、語源は不確か。名詞spar（梁、船の帆柱）とは別系列の可能性がある → つばぜり合いをする、軽く争う |
| conundrum | 17世紀の英語・オックスフォード大学の俗語とされ、起源不明の語。ラテン語風の冗談めいた語形から、難問やなぞなぞの意味になった → 難問、困難な問題 |
| cuddled | 中英語 cuddel などの方言・幼児語とされ、起源は不確か。抱きしめて寄り添う意味になった → 抱きしめた |
| douse | 中英語 dousen などに由来する動詞で、起源には諸説があり確定しない → 消す、液体を浴びせる |
| flinches | 中英語・古フランス語系の flenchir（曲げる、身を引く）などに関係するとされるが詳細は確定しない。三人称単数の-sは語形変化 → ひるむ |
| jangles | 古フランス語 jangler（おしゃべりする、騒がしく言い争う）などに由来し、ゲルマン語・擬音との関係には不確実さがある。三人称単数の-sは語形変化 → 耳障りに鳴る |
| kindled | 中英語 cundel などから、古ノルド語 kynda（火をつける）に関係するとされるが起源は不確か。過去形の-edは語形変化 → 火をつけた、感情を呼び起こした |
| peevish | 中英語 pevische などから英語へ。基体 peeve の起源と形成にも不確実さがあり、語尾の-ishだけで安定した語源分解とはしない → いら立った、気難しい |
| scrawny | 英語方言 scranny の変形とされ、さらに古ノルド語との関係が推測されるが起源は不確か。語尾の-yだけでは安定した語源分解にならない → やせこけた |
| squandered | 16世紀英語 squander の起源は不明で、広く散らす意味から浪費の意味が生じた。過去形の-edは語形変化 → 浪費した |
| tantrum | 18世紀初頭の口語 tanterum に由来するが、起源は不明 → 癇癪 |
| scuffed | 18世紀スコットランド語 scuff に由来し、スカンジナビア語との関係が推測されるが起源は不確か。過去形の-edは語形変化 → こすって傷をつけた |
| shirked | 中英語・初期近代英語 shirk に由来し、起源には不確実さが残る。過去形の-edは語形変化 → 怠った、回避した |
| dank | 中英語 dank（湿った）に由来し、北欧語系の語との関係が指摘される。 → 湿っぽくて薄暗い |
| swagger | swag（揺れる、重く歩く）から生じた反復的な表現とされ、いばって歩く・威張る意味になった。 → いばって歩く、威張る |
| bog | アイルランド語・ゲール語系のbog（柔らかい、湿った）などと関係し、湿地や泥沼を表す。 → 沼、泥沼 |
| harass | フランス語 harasser（疲れさせる、悩ませる）に由来し、繰り返し攻撃して悩ませる意味になった。 → 悩ませる、嫌がらせをする |
| damp | 中英語 damp（蒸気、湿気）に由来し、湿った状態や気力をくじく意味を表す。 → 湿った、じめじめした |
| irk | 中英語 irken（疲れさせる、うんざりさせる）に由来し、いらだたせる意味を表す。 → いらだたせる |
| scolded | scoldの過去形。scoldは古ノルド語 skald（詩人）との関係が示され、嘲笑や悪口の感覚から叱責の意味へ変化した。 → 叱った |
| troop | フランス語 troupe、古フランス語 trope / trupe（人々の集まり）から、兵士の集団、さらに人や動物の一団を表すようになった。 → 部隊、一団 |
| seize | 古フランス語 saisir（所有する、力ずくで取る）から、ラテン語 sacireを経て、法的な占有や手でつかむ意味を表すようになった。 → つかむ、奪い取る |
| pour | 語源は不確かで、古フランス語 purer・ラテン語 purareに由来する可能性がある。 → 注ぐ、激しく降る |
| shelter | 語源は論争があり、古英語 scyldtruma（盾を組んだ隊列）からの変化説や、shield＋-ture説がある。 → 避難所、シェルター；保護 |
| swell | 古英語 swellan、ゲルマン祖語 *swellananに由来し、大きくなることや膨らむことを表した。 → 膨らむ、腫れる |
| cast | 古ノルド語 kastaから英語 castへ（細部には不確かな点がある）。 → 配役、鋳型、投げること |
| hesitantly | ラテン語 haesitantem「ためらっている」に由来するとされる。英語 hesitantlyの語形形成には異説がある → ためらいながら |
| tracked | 古フランス語 tracから英語 trackへ。trackedはtrackの過去形・過去分詞形（細部には不確かな点がある）。 → 追跡した、記録した |
| trash | 語源は不確かだが、古ノルド語 tros「ごみ・落ち葉」と同系の語とされる → ごみ、くだらないもの |

### 英語より前の系統が書かれていない語（english / unknown、336語）

mumble, dodge, hitch, teeter, whim, rig, canter, trickle, sleek, splash, chuckle, roundabout, bluntly, flap, flippant, onset, pinpoint, pitfall, pushover, rowdy, snowball, spearhead, walkout, cuddled, douse, peevish, sluggish, squandered, tantrum, shirked, quagmire, dank, swagger, irk, lunch, puzzle, scratch, crowded, gloomy, sizzle, haul, backlog, outbreak, turnover, aging, coverage, backlash, loophole, rebuke, hunch, entangled, garbled, baffled, hoisted, enlisted, sauntered, splurged, fumbled, residual, illegible, belatedly, blotch, offshoot, caucus, deferral, endowment, socialite, upstart, defaulted, gargled, emancipated, sanitized, orchestrated, abducted, swirled, beguiled, churned, astronomical, conciliatory, cognizant, antagonistic, momentous, abysmally, nominally, swathe, blight, swamp, grind, mainstay, consoled, masqueraded, emaciated, besieged, flexed, stymie, condescending, lavish, bombastic, anecdotal, jaded, daintily, deviation, snag, implosion, elucidation, reprieve, collateral, compliance, accredited, clenched, perturbed, jumbled, desensitized, eavesdropped, catapulted, fractured, incapacitated, uptight, uncanny, unequivocal, brazen, flimsy, salient, inadvertently, listlessly, calibration, brawl, hype, hobbled, astounded, babbled, dribbled, enthralled, nibbled, oriented, stuttered, bumbling, clairvoyant, crabby, frazzled, preemptive, wanton, adversarial, frenzy, groove, ailments, contraption, libel, dawdle, drool, debunk, plagiarized, articulated, marshaled, enlightened, shoved, prowled, anemic, deceased, palatable, gallant, untenable, delirious, exponentially, tatter, accreditation, deluge, hassle, throng, bewildered, bickered, flaunted, grilled, meandered, tangled, intercepted, petrified, shrewd, menial, dispassionate, ephemeral, gallantly, sheepishly, irreparably, affront, conveyance, faltered, goaded, blurred, euphoric, insufferable, harrowing, cumbersome, partisan, outage, rampage, blunder, clout, kickback, scruple, ruckus, mesmerize, sabotage, yielded, wagered, rustled, lured, plundered, implausible, voracious, homely, subdued, detrimental, stopgap, homage, rift, payoff, rendezvous, layman, snitch, truancy, caricature, garnish, debase, tempered, discard, misconstrue, garnered, scrounged, pitiless, incremental, measly, fluorescent, listless, inflatable, diabolically, grudge, glint, bout, smirk, contingency, premise, jeopardize, guzzle, taunt, slaughter, swindle, advocate, downplay, embolden, siphon, quarrelsome, sultry, scrumptious, waning, sparingly, aptly, doggedly, misgiving, yardstick, catalyst, finesse, feasibility, acquittal, precipitate, cripple, heave, impound, hamper, jiggle, dazzled, apolitical, ostentatious, antiseptic, discerning, shoddy, wryly, admitted, approval, approximately, beaten, beforehand, betting, bled, certainly, complexity, composed, detective, done, embarrassed, emotional, evaluated, folded, had, helping, investment, jealously, means, meant, memorize, moreover, navigate, needlessly, nightmares, pretended, provided, related, replacement, rotated, safely, scenery, seriously, shifts, sight, silently, simply, sitting, soak, spare, spent, spoiled, straighten, strangers, stuck, suitably, surely, thanked, ungrateful, unless, vaguely, visiting, waiting, wasted, way, when, why
