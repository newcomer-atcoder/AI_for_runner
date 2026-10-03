//最後に成功した推論結果の文字列 (D4.2)
let lastInferenceResult = null;

//「実際に走る距離(km)」の推論
const inference_your_distance = async(event) => {
    event.preventDefault();   //ブラウザの検証(required/min/max)を通過した場合だけ、ここに来る
    const distance = document.getElementById('inference-distance').value;
    const condition = document.getElementById('inference-condition').value;

    const res = await withOverlay('AIが計算中です…', () => fetch(
        `/inference/?distance=${encodeURIComponent(distance)}&condition=${encodeURIComponent(condition)}`,
        {method : 'POST', headers : {'Content-Type' : 'application/json'}}
    ));

    if(res.status == 422){
        showMessage('inference-message', '入力エラー', 'ng');
        return;
    }
    if(!res.ok){
        showMessage('inference-message', '推論に失敗しました（サーバエラー）', 'ng');
        return;
    }
    const result = await res.json();
    showMessage('inference-message', result.inference_result, result.inference_ok ? 'ok' : 'ng');
    if(result.inference_ok){
        lastInferenceResult = result.inference_result;
        document.getElementById('btn-save').disabled = false;
    }
}

//推論結果を次の走行予定として保存 (D4)
const saveAsSchedule = async() => {
    if(!lastInferenceResult) return;
    const res = await fetch('/save/?saveInfo=' + encodeURIComponent(lastInferenceResult), {method : 'POST'});
    if(!res.ok){
        showMessage('inference-message', '予定の保存に失敗しました（サーバエラー）', 'ng');
        return;
    }
    const item = await res.json();
    if(item.schedule){
        showMessage('inference-message', item.result, 'ok');
        applySchedule(item.schedule);   //登録タブのフォームを上書き (D4.3)。タブは切り替えない
    }else{
        showMessage('inference-message', item.result, 'ng');
    }
}

//保存した予定を登録フォームに反映 (D4.3)
const applySchedule = (s) => {
    document.getElementById('entry-date').value =
        `${s.yyyy}-${String(s.mm).padStart(2, '0')}-${String(s.dd).padStart(2, '0')}`;
    document.getElementById('entry-distance').value = s.distance;
    document.getElementById('entry-condition').value = s.condition;
    document.getElementById('entry-runningDist').value = s.runningDist;
    document.getElementById('fromSchedule').value = '1';
}
