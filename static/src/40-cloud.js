/* ============================================================
   cloud sync（生徒別・共有URL ?s=&t=）— harness/cloud.js を利用
   共通スキーマ app_students / app_progress（app="eiken2-q1"）。
   config.json が無ければ no-op で、従来どおり匿名ローカル動作（無回帰）。
   RPC/認証/デバウンス保存は vendor/harness/cloud.js に集約。
   このアプリ固有＝複数データセットの進捗を1つのjsonbにまとめる点のみ。
   ============================================================ */
const APP_ID = "eiken2-q1";
let cloud = null; // harness createCloud のインスタンス（init で生成）
let legacyPre1Cloud = null;
let legacyPre1CloudProgress = null;
let pendingCloudProgress = null;

function cloudMeta() {
  return {
    lastDatasetId: state.datasetId,
    ...(studyPlan ? { studyPlanV1: studyPlan } : {}),
  };
}

function setShareStatus(message, tone = "") {
  const slot = $("#shareStatus");
  if (!slot) return;
  slot.innerHTML = "";
  slot.className = "shareStatus" + (tone ? " " + tone : "");
  if (!message) return;
  if (tone === "ok" || tone === "ng" || tone === "syncing") {
    slot.appendChild(el("span", { class: "shareStatusIcon", "aria-hidden": "true" }));
  }
  slot.appendChild(document.createTextNode(message));
}
// クラウド保存は全データセット分の進捗を1つのjsonbにまとめる: { [datasetId]: progress }
function collectAllProgress() {
  const map = {};
  // 級を絞っても他級の進捗を落とした地図でクラウドを上書きしないよう、manifest全件を見る。
  Object.keys(ALL_DATASETS).forEach((id) => {
    try {
      const raw = localStorage.getItem(progressKey(id));
      if (raw) map[id] = JSON.parse(raw);
    } catch (e) { /* ignore */ }
  });
  map[state.datasetId] = state.progress; // 直近のメモリ状態を優先
  map._meta = cloudMeta();
  return map;
}

