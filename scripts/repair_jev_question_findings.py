"""Apply the reviewed 2026-10-08 question repairs, preserving question IDs and keys.

Question stems/translations are authored repairs, not corrections to official text.
Replacement vocabulary/context/audio is reused from existing reviewed datasets.
Old audio is retained. Re-running is idempotent.
"""
import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_eiken1_alignment import expected_audio_path

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def write(path, value):
    (ROOT / path).write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))

# Dataset, question, replacement English, completed Japanese translation.
STEMS = [
('eiken2-mock-1',17,"A: Could you explain the situation (   ), using just a few words? B: Certainly. Making a living from art is difficult.","A: ほんの数語で、状況を簡潔に説明してもらえますか。B: もちろんです。芸術で生計を立てるのは難しいです。"),
('eiken2-mock-2',15,"A: Your report received an A, but (   ) of your exam performance, there is room for improvement. B: I understand. I'll study more next time.","A: レポートはA評価でしたが、試験の成績という点では改善の余地があります。B: わかりました。次回はもっと勉強します。"),
('eiken2-mock-3',2,"Alan often wakes up screaming after dreaming that someone is chasing him. These recurring (   ) make him afraid to fall asleep.","アランは誰かに追いかけられる夢を見て、叫びながら目を覚ますことがよくある。繰り返すこうした悪夢のため、彼は眠るのを怖がっている。"),
('eiken2-mock-3',15,"A: Your report needs facts from several sources. You'll have to (   ) a new report using those facts. B: OK. I'll start again from the beginning.","A: レポートには複数の資料から得た事実が必要です。その事実を使って新しいレポートをまとめなければなりません。B: わかりました。最初からやり直します。"),
('eikenp2-mock-2',10,"The students' slides and handouts are not ready yet, so they need to (   ) their materials before tomorrow's presentation.","生徒たちのスライドと配布資料はまだできていないので、明日の発表までに資料を準備する必要がある。"),
('eiken1-mock-6',7,"Vincent smiled (   ) as he admitted his own foolish mistake. It was a spontaneous, heartfelt expression of regret, with none of his usual cheerfulness.","ヴィンセントは自分の愚かな失敗を認めながら、悔やむように微笑んだ。それは自然に出た心からの後悔の表情で、いつもの明るさは全くなかった。"),
('eiken1-mock-9',7,"The priest's (   ) duties included visiting sick parishioners and offering spiritual guidance to members of his congregation.","その司祭の牧会の職務には、病気の教区民を訪問し、会衆に精神的な導きを与えることが含まれていた。"),
('eiken1-mock-7',17,"Whenever we ask for a clear account of his policy, the candidate keeps (   ) the details, using vague phrases that make the proposal harder to understand.","政策の明確な説明を求めるたびに、その候補者は提案を理解しにくくする曖昧な表現を使い、詳細をわかりにくくし続ける。"),
('eiken1-mock-9',23,"The director decided to (   ) the company's efforts to improve staff skills, doubling the training budget and increasing the number of courses.","取締役は研修予算を倍増し、講座数を増やすことで、社員の技能向上に向けた会社の取り組みを強化することにした。"),
('eiken1-mock-11',17,"The technician was (   ) about following every safety rule, checking even the smallest parts rather than skipping steps to save time.","その技術者はあらゆる安全規則を守ることに良心的で、時間を節約するために手順を省くことなく、最も小さな部品まで点検した。"),
('eiken1-mock-13',10,"The child (   ) the freshly ironed tablecloth by pulling it into a tangled heap. Its smooth surface was now covered in creases.","子どもはアイロンをかけたばかりのテーブルクロスを引っ張って絡まった山にし、しわくちゃにした。滑らかだった表面は今やしわだらけだった。"),
('eiken1-mock-16',19,"His (   ) praise came in an enthusiastic torrent of heartfelt compliments. He went on expressing his admiration long after the architect had begun to feel embarrassed.","彼の熱のこもった称賛は、心からの褒め言葉が勢いよくあふれ出るものだった。建築家が気恥ずかしくなってからも、彼は感嘆を表し続けた。"),
('eiken1-mock-18',17,"The hut's position on a crumbling ledge was so (   ) that the slightest movement could send the entire structure tumbling into the lake below.","崩れかけた岩棚にある小屋の位置は非常に不安定で、わずかな動きでも建物全体が下の湖へ転落しかねなかった。"),
('eiken1-mock-19',24,"Writing entirely on his own, the critic (   ) the novel's weak plot in a blistering review, ridiculing its implausible twists and flat characters.","批評家は完全に自分一人で書いた痛烈な書評で、小説の弱い筋書きを酷評し、ありそうもない展開と平板な登場人物をあざ笑った。"),
('eiken1-mock-20',16,"Although he gave long, detailed answers whenever anyone spoke to him at the party, his cold, distant manner made him seem (   ). He showed no interest in getting closer to the other guests.","パーティーで誰かに話しかけられると彼は長く詳しい返答をしたが、冷たく距離を置く態度のため、よそよそしく見えた。他の客と親しくなることに関心を示さなかった。"),
('eiken1-mock-21',18,"The editor had a (   ) eye for literary quality, readily distinguishing subtle differences between an original argument and a merely fashionable one.","その編集者は文学的な質を見抜く目を持ち、独創的な議論と単に流行に乗った議論との微妙な違いを容易に見分けた。"),
('eiken1-mock-21',24,"With barely enough money for food and rent, the family (   ) financially on one small pension. They could not afford even a minor unexpected expense.","食費と家賃を払うのがやっとの家族は、少額の年金一つで経済的にどうにか暮らしていた。わずかな予定外の出費にも対応できなかった。"),
]

# The three tense-only questions become same-grade lexical/idiom items.
# Only donor card/context/audio content is reused; the stems below are new.
REPLACEMENTS = [
('eiken2-mock-1',13,'eiken2-2025-3',3,"exist react seize disappear".split(),"A: How did the audience (   ) when the singer unexpectedly returned to the stage? B: Everyone cheered and clapped loudly.","A: 歌手が予想外にステージに戻ったとき、観客はどう反応しましたか。B: みんな大きな声で歓声を上げ、拍手しました。",'react'),
('eiken2-mock-2',19,'eiken2-2025-3',14,['bit by bit','far and away','all or nothing','safe and sound'],"After being missing for two days, the hikers were found (   ). None of them had suffered any injuries.","2日間行方不明だったハイカーたちは、無事に発見された。誰もけがをしていなかった。",'safe and sound'),
('eiken2-mock-4',20,'eiken2-2025-3',15,['in search of','for fear of','on behalf of','with regard to'],"The lawyer attended the meeting (   ) her client, who was in hospital and could not be there himself.","弁護士は、入院中で自分では出席できなかった依頼人を代表して、その会議に出席した。",'on behalf of'),
]

def main():
    manifest = read('data/manifest.json')['q1']
    archive_path='data/audit/retired-question-vocabulary-20261008.json'
    if not (ROOT/archive_path).exists():
        baseline='d1db34873f3034d038b607686ac79b7baca206ec'
        def original(path):
            return json.loads(subprocess.check_output(['git','show',f'{baseline}:{path}'],cwd=ROOT))
        retired=[]
        for ds,q,*_ in REPLACEMENTS:
            meta=manifest[ds]; vocab=original(meta['vocabUrl'])
            retired.append({'dataset':ds,'q':q,
                'question':next(x for x in original(meta['questionsUrl'])['questions'] if x['q']==q),
                'words':[x for x in vocab['words'] if x['q']==q],
                'idioms':[x for x in vocab['idioms'] if x['q']==q],
                'contexts':[x for x in original(meta['contextUrl'])['contexts'] if x['q']==q],
                'contextTranslations':[x for x in original(meta['contextTranslationUrl'])['items'] if x['q']==q]})
        ledger=original('data/word_origin_research.json')
        write(archive_path,{'baselineCommit':baseline,'reason':'Tense-only items replaced by contextual vocabulary/idioms. Original supplied material, card metadata and etymology evidence retained here; old MP3s retained in place.',
            'retiredItems':retired,'wordOriginEntries':{k:ledger['entries'][k] for k in ['had','have']}})
    for ds,q,stem,ja in STEMS:
        path=manifest[ds]['questionsUrl']; data=read(path)
        item=next(x for x in data['questions'] if x['q']==q)
        item.update(stem=stem,translation=ja); write(path,data)
    for ds,q,donor,dq,choices,stem,ja,answer in REPLACEMENTS:
        dst,src=manifest[ds],manifest[donor]
        qp=dst['questionsUrl']; questions=read(qp)
        item=next(x for x in questions['questions'] if x['q']==q)
        # Retain the original key index: 3 in all three repaired items.
        choices=[c for c in choices if c!=answer]+[answer]
        item.update(stem=stem,translation=ja,choices=choices)
        write(qp,questions)
        vp=dst['vocabUrl']; vocab=read(vp); dv=read(src['vocabUrl'])
        for kind in ['words','idioms']:
            new=[]
            for x in dv[kind]:
                if x['q']!=dq: continue
                y=copy.deepcopy(x); y.update(q=q,is_answer=(x.get('word') or x.get('phrase'))==answer); new.append(y)
                source_audio=expected_audio_path(donor,x); dest_audio=expected_audio_path(ds,y)
                dest_audio.parent.mkdir(parents=True,exist_ok=True)
                if not dest_audio.exists(): shutil.copyfile(source_audio,dest_audio)
            old=vocab[kind]; first=next((i for i,x in enumerate(old) if x['q']==q),len(old))
            vocab[kind]=old[:first]+new+[x for x in old[first:] if x['q']!=q]
        write(vp,vocab)
        for field,key in [('contextUrl','contexts'),('contextTranslationUrl','items')]:
            path=dst[field]; data=read(path); donor_data=read(src[field])
            new=[dict(copy.deepcopy(x),q=q) for x in donor_data[key] if x['q']==dq]
            old=data[key]; first=next(i for i,x in enumerate(old) if x['q']==q)
            data[key]=old[:first]+new+[x for x in old[first:] if x['q']!=q]; write(path,data)
        # Keep the context publication inputs consistent with the repaired data.
        cp=f'data/context-candidates/{ds}.json'; candidates=read(cp)
        new=[dict(copy.deepcopy(x),q=q) for x in read(f'data/context-candidates/{donor}.json')['contexts'] if x['q']==dq]
        old=candidates['contexts']; first=next(i for i,x in enumerate(old) if x['q']==q)
        removed={x['target'] for x in old if x['q']==q}
        candidates['contexts']=old[:first]+new+[x for x in old[first:] if x['q']!=q];write(cp,candidates)
        rp=f'data/context-reviews/{ds}.json'; review=read(rp)
        # The transplanted contexts already have donor review-passed records.
        donor_review=read(f'data/context-reviews/{donor}.json')
        targets={x['target'] for x in new}; donor_items=[copy.deepcopy(x) for x in donor_review['items'] if x['target'] in targets]
        for x in donor_items: x['repairProvenance']=f'{donor} reviewed context reused on 2026-10-08'
        old=review['items']; first=next(i for i,x in enumerate(old) if x['target'] in removed or x['target'] in targets)
        review['items']=old[:first]+donor_items+[x for x in old[first:] if x['target'] not in removed and x['target'] not in targets];write(rp,review)
    # Test pastoral's independently attested clergy sense instead of the sense
    # shared with rustic. Retain both words, their audio, and countryside examples.
    vp=manifest['eiken1-mock-9']['vocabUrl']; vocab=read(vp)
    next(x for x in vocab['words'] if x['q']==7 and x['word']=='pastoral')['meaning']='牧歌的な、田園の、牧会の'
    write(vp,vocab)
    lp='data/lemmas.json'; lemmas=read(lp)
    lemmas.get('flashcardDisplayLemmas',{}).pop('had',None); write(lp,lemmas)
    # These two entries have no remaining active vocabulary owner. Their entire
    # research records are preserved in the archive above, not discarded.
    path='data/word_origin_research.json'; ledger=read(path)
    for key in ['had','have']: ledger['entries'].pop(key,None)
    target=ledger['researchTarget']; target['lemmas']=[k for k in target['lemmas'] if k not in ['had','have']]; target['count']=len(target['lemmas'])
    # Edit only these object spans, retaining the ledger's compact display format.
    crlf=b'\r\n' in (ROOT/path).read_bytes()
    text=(ROOT/path).read_text(encoding='utf-8'); decoder=json.JSONDecoder()
    for key in ['had','have']:
        marker='    '+json.dumps(key)+': '
        start=text.find(marker)
        if start<0: continue
        value_start=start+len(marker); _,length=decoder.raw_decode(text[value_start:])
        end=value_start+length
        if text[end:end+1]==',':end+=1
        if text[end:end+1]=='\n':end+=1
        text=text[:start]+text[end:]
    marker='  "researchTarget": '; start=text.index(marker)+len(marker); _,length=decoder.raw_decode(text[start:])
    replacement=json.dumps(target,ensure_ascii=False,indent=2).replace('\n','\n  ')
    text=text[:start]+replacement+text[start+length:]
    content=text.replace('\n','\r\n') if crlf else text
    # The repository tracks this large ledger with CRLF; keep all untouched
    # lines, but the changed count line must pass git's whitespace check.
    content=content.replace(f'    "count": {target["count"]},\r\n',f'    "count": {target["count"]},\n',1)
    (ROOT/path).write_bytes(content.encode('utf-8'))
    assert read(path)==ledger
    print('Repaired 20 mock questions. Official pre2 Q9 preserved.')

if __name__=='__main__': main()
