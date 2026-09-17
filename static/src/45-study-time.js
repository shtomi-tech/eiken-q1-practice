/* ============================================================
   学習時間（日ごと・累計。全級合算）
   学習画面（#sessionPanel）が見えていて、最後の操作から3分以内の間だけ加算する。
   クラウドでは _meta.studyTimeV1_<端末ID> に端末ごとの日別秒数を置く。
   サーバーは _meta をキー単位でマージするので、端末同士で上書きし合わない。
   合計＝自端末の記録＋クラウドから読んだ他端末の記録。
   ============================================================ */
const STUDY_TIME_KEY = "eiken_q1_study_time_v1";
const STUDY_TIME_DEVICE_KEY = "eiken_q1_device_id";
const STUDY_TIME_META_PREFIX = "studyTimeV1_";
const STUDY_TIME_IDLE_MS = 3 * 60 * 1000;
const STUDY_TIME_TICK_MS = 1000;
const STUDY_TIME_MAX_TICK_MS = 5 * 1000; // スリープ復帰などで間隔が飛んだ分は数えない
const STUDY_TIME_FLUSH_MS = 30 * 1000;
const STUDY_TIME_DAY_RE = /^\d{4}-\d{2}-\d{2}$/;

let studyTime = null; // { days: {YYYY-MM-DD: 秒}, remote: {端末ID: {YYYY-MM-DD: 秒}} }
let studyTimeDeviceId = "";
let pendingCloudStudyTime = null; // applyCloudProgress で受け取った端末別の記録
let studyTimeCarryMs = 0;
let studyTimeLastTick = 0;
let studyTimeLastActivity = 0;
let studyTimeLastFlush = 0;
let studyTimeDirty = false;
let studyTimeTimer = null;

function studyTimeDayKey(date = new Date()) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}
function normalizeStudyTimeDays(value) {
  const days = {};
  if (!value || typeof value !== "object" || Array.isArray(value)) return days;
  Object.entries(value).forEach(([day, sec]) => {
    const n = Math.floor(Number(sec));
    if (STUDY_TIME_DAY_RE.test(day) && Number.isFinite(n) && n > 0) days[day] = n;
  });
  return days;
}
function mergeStudyTimeDays(a, b) {
  const out = { ...a };
  Object.entries(b).forEach(([day, sec]) => { out[day] = Math.max(out[day] || 0, sec); });
  return out;
}
function studyTimeDevice() {
  if (studyTimeDeviceId) return studyTimeDeviceId;
  try { studyTimeDeviceId = localStorage.getItem(STUDY_TIME_DEVICE_KEY) || ""; } catch (e) { /* ignore */ }
  if (!/^[A-Za-z0-9-]{8,64}$/.test(studyTimeDeviceId)) {
    studyTimeDeviceId = (window.crypto && crypto.randomUUID)
      ? crypto.randomUUID()
      : `d${Date.now().toString(36)}${Math.random().toString(36).slice(2, 10)}`;
    writeStored(STUDY_TIME_DEVICE_KEY, studyTimeDeviceId);
  }
  return studyTimeDeviceId;
}
// クラウドの _meta から端末別の記録を抜き出す（applyCloudProgress から呼ぶ）
function captureCloudStudyTime(meta) {
  const found = {};
  Object.entries(meta || {}).forEach(([key, value]) => {
    if (!key.startsWith(STUDY_TIME_META_PREFIX)) return;
    const id = key.slice(STUDY_TIME_META_PREFIX.length);
    if (id && value && typeof value === "object") found[id] = normalizeStudyTimeDays(value.days);
  });
  pendingCloudStudyTime = found;
}
function studyTimeMeta() {
  if (!studyTime || !Object.keys(studyTime.days).length) return {};
  return { [STUDY_TIME_META_PREFIX + studyTimeDevice()]: { days: studyTime.days } };
}
// 生徒別のストレージ範囲が決まった後（boot 内）で呼ぶ
function initStudyTime() {
  const deviceId = studyTimeDevice();
  const stored = readStoredObject(scopedStorageKey(STUDY_TIME_KEY)) || {};
  let days = normalizeStudyTimeDays(stored.days);
  const remote = {};
  Object.entries(stored.remote && typeof stored.remote === "object" ? stored.remote : {})
    .forEach(([id, value]) => { remote[id] = normalizeStudyTimeDays(value); });
  if (pendingCloudStudyTime) {
    Object.entries(pendingCloudStudyTime).forEach(([id, value]) => {
      if (id === deviceId) days = mergeStudyTimeDays(days, value);
      else remote[id] = value; // 他端末分はクラウドを正とする
    });
    pendingCloudStudyTime = null;
  }
  delete remote[deviceId];
  studyTime = { days, remote };
  writeStoredJson(scopedStorageKey(STUDY_TIME_KEY), studyTime);
  startStudyTimeTracking();
}
function studyTimeIsActive(now) {
  if (window.EikenActiveAppId !== "q1") return false;
  if (document.visibilityState !== "visible") return false;
  const panel = document.getElementById("sessionPanel");
  if (!panel || panel.classList.contains("hide")) return false;
  return now - studyTimeLastActivity < STUDY_TIME_IDLE_MS;
}
function studyTimeTick() {
  const now = Date.now();
  const elapsed = now - studyTimeLastTick;
  studyTimeLastTick = now;
  if (!studyTime || !studyTimeIsActive(now)) return;
  studyTimeCarryMs += Math.min(Math.max(elapsed, 0), STUDY_TIME_MAX_TICK_MS);
  const sec = Math.floor(studyTimeCarryMs / 1000);
  if (sec > 0) {
    studyTimeCarryMs -= sec * 1000;
    const day = studyTimeDayKey(new Date(now));
    studyTime.days[day] = (studyTime.days[day] || 0) + sec;
    studyTimeDirty = true;
  }
  if (studyTimeDirty && now - studyTimeLastFlush >= STUDY_TIME_FLUSH_MS) flushStudyTime();
}
function flushStudyTime() {
  studyTimeLastFlush = Date.now();
  if (!studyTime || !studyTimeDirty) return;
  studyTimeDirty = false;
  writeStoredJson(scopedStorageKey(STUDY_TIME_KEY), studyTime);
  if (cloud) cloud.queueSave();
}
function markStudyActivity() {
  studyTimeLastActivity = Date.now();
}
function startStudyTimeTracking() {
  if (studyTimeTimer) return;
  studyTimeLastTick = Date.now();
  studyTimeLastActivity = Date.now();
  studyTimeLastFlush = Date.now();
  ["pointerdown", "keydown", "wheel", "touchstart", "scroll"].forEach((type) => {
    document.addEventListener(type, markStudyActivity, { capture: true, passive: true });
  });
  document.addEventListener("visibilitychange", () => {
    studyTimeLastTick = Date.now();
    if (document.visibilityState === "hidden") flushStudyTime();
    else markStudyActivity();
  });
  window.addEventListener("pagehide", flushStudyTime);
  studyTimeTimer = setInterval(studyTimeTick, STUDY_TIME_TICK_MS);
}
function studyTimeTotals() {
  const today = studyTimeDayKey();
  const prev = new Date();
  prev.setDate(prev.getDate() - 1);
  const yesterday = studyTimeDayKey(prev);
  const totals = { today: 0, yesterday: 0, total: 0, average: 0 };
  if (!studyTime) return totals;
  let firstDay = "";
  [studyTime.days, ...Object.values(studyTime.remote)].forEach((days) => {
    Object.entries(days).forEach(([day, sec]) => {
      totals.total += sec;
      if (day === yesterday) totals.yesterday += sec;
      if (day === today) totals.today += sec;
      if (!firstDay || day < firstDay) firstDay = day;
    });
  });
  // 平均＝累計 ÷ 最初に記録した日から今日までの日数（学習しなかった日も含む）
  if (firstDay) {
    const [y, m, d] = firstDay.split("-").map(Number);
    const start = new Date(y, m - 1, d);
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const spanDays = Math.max(1, Math.round((todayStart - start) / 86400000) + 1);
    totals.average = Math.round(totals.total / spanDays);
  }
  return totals;
}
function formatStudyDuration(sec) {
  const minutes = Math.floor(sec / 60);
  if (minutes < 60) return `${minutes}分`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `${hours}時間${rest}分` : `${hours}時間`;
}
function studyTimeCard() {
  const totals = studyTimeTotals();
  const metric = (label, sec) => el("div", { class: "studyTimeMetric" },
    el("span", { class: "label" }, label),
    el("strong", {}, formatStudyDuration(sec)),
  );
  return el("section", { class: "card studyTimeCard", "aria-labelledby": "studyTimeTitle" },
    el("h3", { id: "studyTimeTitle" }, "学習時間"),
    el("div", { class: "studyTimeMetrics" },
      metric("今日", totals.today),
      metric("前日", totals.yesterday),
      metric("1日平均", totals.average),
      metric("累計", totals.total),
    ),
    el("p", { class: "hint" }, "学習画面を開いている間に自動で記録します（3分操作がなければ停止）。全級の合計です。"),
  );
}
