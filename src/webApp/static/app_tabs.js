//画面全体の状態
const appState = {
    currentTab : 'entry',
    recordExists : false,   //DBに記録が1件以上あるか (D2.2)
    pendingCnt : 0,         //未確定件数 (D2.4)
};

//タブ切り替え
//  options.skipPrepare: 登録終了&学習の直後など、prepareが不要な場合にtrue
const switchTab = async(tab, options = {}) => {
    if(tab === 'inference' && !appState.recordExists) return;   //押せない状態 (D2.2)

    appState.currentTab = tab;
    document.querySelectorAll('.tab').forEach(btn => {
        const active = btn.dataset.tab === tab;
        btn.classList.toggle('active', active);
        btn.setAttribute('aria-selected', active);
    });
    document.getElementById('panel-entry').hidden = (tab !== 'entry');
    document.getElementById('panel-inference').hidden = (tab !== 'inference');
    history.replaceState(null, '', `/?tab=${tab}`);   //(D1.4)

    if(tab === 'inference'){
        if(appState.pendingCnt > 0){
            showToast('⚠ 未確定の記録は推論に反映されていません');   //(D2.5)
        }
        if(!options.skipPrepare){
            await prepareModel();
        }
    }
    //タブ移動時はDB登録・学習を行わない (D2.3)
}

//未確定件数の更新：バッジと取り消しボタン (D2.4, D8.7)
const setPendingCnt = (cnt) => {
    appState.pendingCnt = cnt;
    const badge = document.getElementById('pending-badge');
    badge.hidden = (cnt === 0);
    badge.textContent = cnt;
    document.getElementById('btn-cancel').disabled = (cnt === 0);
}

//推論タブを押せるかどうか (D2.2)
const setRecordExists = (exists) => {
    appState.recordExists = exists;
    const tab = document.querySelector('.tab[data-tab="inference"]');
    tab.disabled = !exists;
    tab.title = exists ? '' : 'ランニング記録を1件以上「登録終了&学習」すると使えます';
}

//メッセージ欄 (D5.7)  kind: 'ok' | 'ng'
const showMessage = (elementId, text, kind) => {
    const el = document.getElementById(elementId);
    el.textContent = text;
    el.className = `message ${kind}`;
}

//トースト：3秒で消える (D2.5)
let toastTimer = null;
const showToast = (text) => {
    const toast = document.getElementById('toast');
    toast.textContent = text;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.hidden = true, 3000);
}

//オーバーレイを出している間に非同期処理を行う (D5.6)
//  delayMs: オーバーレイを出すまでの待ち時間(A4)。操作は待ち時間中も止める
const withOverlay = async(text, asyncFn, delayMs = 0) => {
    const app = document.getElementById('app');
    const overlay = document.getElementById('overlay');
    app.inert = true;   //タブ・ヘッダーを含め、すべての操作を止める
    document.getElementById('overlay-text').textContent = text;
    const timer = setTimeout(() => overlay.hidden = false, delayMs);
    try{
        return await asyncFn();
    }finally{
        clearTimeout(timer);
        overlay.hidden = true;
        app.inert = false;
    }
}

//推論タブを開いたときのモデル準備 (D3.2)
const prepareModel = async() => {
    const res = await withOverlay('AIが学習中です…', () => fetch('/api/model/prepare/', {method : 'POST'}), 300);
    if(!res.ok){
        showMessage('inference-message', 'AIの準備に失敗しました（サーバエラー）', 'ng');
    }
}

//アプリ終了 (D5.1.1)
const openExitDialog = () => {
    const warning = document.getElementById('exit-warning');
    const confirmBtn = document.getElementById('btn-exit-confirm');
    if(appState.pendingCnt > 0){
        warning.textContent = `⚠ 未確定の記録が ${appState.pendingCnt} 件あります。破棄して終了しますか？`;
        warning.hidden = false;
        confirmBtn.textContent = '破棄して終了';
    }else{
        warning.hidden = true;
        confirmBtn.textContent = '終了';
    }
    document.getElementById('exit-dialog').showModal();
}
const closeExitDialog = () => document.getElementById('exit-dialog').close();
const confirmExitApp = async() => {
    closeExitDialog();
    await exitApp();   //commonFuncs.js
    //(A7) 終了後の案内。サーバはもう応答しないので、オーバーレイを出したままにする
    document.getElementById('app').inert = true;
    document.getElementById('overlay-text').textContent = 'アプリを終了しました。このタブを閉じてください';
    document.querySelector('#overlay .spinner').hidden = true;
    document.getElementById('overlay').hidden = false;
}

//初期化
document.addEventListener('DOMContentLoaded', () => {
    const ds = document.body.dataset;
    setRecordExists(ds.recordExists === '1');
    setPendingCnt(Number(ds.pendingCnt));
    document.querySelectorAll('.tab').forEach(btn =>
        btn.addEventListener('click', () => switchTab(btn.dataset.tab)));
    switchTab(ds.initialTab);   //初期表示が推論タブなら、ここで prepare が走る
});
