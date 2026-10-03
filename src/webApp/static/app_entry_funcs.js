//今日の日付を<input type="date">の形式(YYYY-MM-DD)で返す
const todayString = () => {
    const now = new Date();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    return `${now.getFullYear()}-${mm}-${dd}`;
}

//登録後のフォームを「今日の日付・その他は空欄」に戻す (D3.3, A3)
const resetEntryForm = () => {
    document.getElementById('entry-date').value = todayString();
    ['entry-distance', 'entry-condition', 'entry-runningDist'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('fromSchedule').value = '0';
}

//ランニング記録のエントリー(未確定リストに追加)
const entry_runData = async(event) => {
    event.preventDefault();   //ブラウザの検証(required/min/max)を通過した場合だけ、ここに来る
    const [yyyy, mm, dd] = document.getElementById('entry-date').value.split('-').map(Number);   //(D5.4)
    const querys = {
        yyyy, mm, dd,
        distance : document.getElementById('entry-distance').value,
        condition : document.getElementById('entry-condition').value,
        runningDist : document.getElementById('entry-runningDist').value,
    };
    const clearSchedule = document.getElementById('fromSchedule').value;

    const res = await fetch('/entry/?clearSchedule=' + clearSchedule, {
        method : 'POST', headers : {'Content-Type' : 'application/json'}, body : JSON.stringify(querys),
    });

    if(res.status == 422){
        showMessage('entry-message', '登録失敗', 'ng');
    }else if(res.ok){
        const result = await res.json();
        showMessage('entry-message', result.entry_result, 'ok');
        setPendingCnt(result.pending_cnt);
        resetEntryForm();
    }else{
        showMessage('entry-message', '登録失敗（サーバエラー。記録が保存されていない可能性があります）', 'ng');
    }
}

//登録終了&学習 (D3.1)
const exitEntry = async() => {
    const res = await withOverlay('AIが学習中です…', () => fetch('/updateDB/', {method : 'POST'}));
    if(!res.ok){
        showMessage('entry-message', '登録終了に失敗しました（サーバエラー）', 'ng');
        return;
    }
    const items = await res.json();
    setPendingCnt(items.pending_cnt);
    if(items.entry_exit_result == 'NoData'){
        showMessage('entry-message', 'ランニング記録を1件以上登録してください', 'ng');
        return;
    }
    setRecordExists(true);   //(D2.2)
    showMessage('entry-message', '登録を確定しました（学習済み）', 'ok');   //(A6)
    switchTab('inference', {skipPrepare : true});   //学習済みなので prepare は不要 (D3.1.2)
}

//未確定データの取り消し (D8)
const cancelEntry = async() => {
    const res = await fetch('/api/entry/cancel/', {method : 'POST'});
    if(!res.ok){
        showMessage('entry-message', '取り消しに失敗しました（サーバエラー）', 'ng');
        return;
    }
    const items = await res.json();
    showMessage('entry-message', items.cancel_result, 'ok');   //(D8.6)
    setPendingCnt(items.pending_cnt);
    //確認ダイアログは出さない(D8.4)。フォームの値は残す(D8.5)
}
