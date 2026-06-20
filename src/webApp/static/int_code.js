async function deleteRecord(id){
    await fetch(
        '/api/delete/',
        {
            method: "DELETE",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({id: id})
        }
    );

    window.location.href = '/';
}

async function updPage(nextFlg, page){
    console.log(Number(page))
    const nextPage = Number(page) + (nextFlg? 1: -1);
    await fetch(
        `/api/updPage/?page=` + String(nextPage),
        {
            method: 'GET' //念の為明示的に指定する
        }
    );

    window.location.href = '/?page=' + nextPage;
}

function editRecord(btn){
    const row = btn.closest('tr');
    const isEditing = row.classList.contains('editing');

    if(!isEditing){
        //編集モード
        row.querySelectorAll('.cell-view').forEach(elem => {elem.hidden = true;});
        row.querySelectorAll('.cell-edit').forEach(elem => {elem.hidden = false;});
        row.classList.add('editing');
    }
    else{
        submitUpdate(row); //レコード更新を実行
    }
}

function editCancel(btn){
    const row = btn.closest('tr');

    //閲覧用画面に戻る
    row.querySelectorAll('.cell-view').forEach(elem => {elem.hidden = false;});
    row.querySelectorAll('.cell-edit').forEach(elem => {elem.hidden = true;});
    row.classList.remove('editing');
    btn.classList.remove('is-editing');
}

async function submitUpdate(row) {
    const id = row.dataset.id;

    const get = (field) => row.querySelector(`.cell-edit[data-field="${field}"]`).value;
    const [yyyy, mm, dd] = get('edit_date').split('-').map(Number);
    const planned_distance= Number(get('edit_planned_distance'));
    const condition = Number(get('edit_condition'));
    const actual_distance = Number(get('edit_actual_distance'));
    
    // レコード更新をリクエスト
    await fetch(
        '/api/submit/',
        {
            method: 'PUT',
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(
                {
                    id: Number(id),
                    yyyy: yyyy, mm: mm, dd: dd,
                    planned_distance: planned_distance,
                    condition: condition,
                    actual_distance: actual_distance
                }
            )
        }
    );

    window.location.href = '/'
}

let isAdding = false;   // 追加行の二重生成を防ぐフラグ

// ◀▶右隣の「追加」: 0ページ目の最上位に編集可能な行を1行差し込む
function addRecord(){
    // 0ページ目以外なら、まず0ページ目へ寄せてから追加する
    const params = new URLSearchParams(window.location.search);
    const page = Number(params.get('page') || 0);
    if(page !== 0){
        // 0ページ目に遷移してから追加させる(状態を持ち越さないシンプル方式)
        window.location.href = '/';
        return;
    }
    if(isAdding) return;          // 既に1行追加済みなら何もしない
    isAdding = true;

    const tbody = document.querySelector('table tbody');
    const tr = document.createElement('tr');
    tr.dataset.id = '';
    tr.classList.add('editing');
    tr.innerHTML = `
        <td><span class="id-badge">新規</span></td>
        <td><input type="date"   class="cell-edit" data-field="edit_date"></td>
        <td><input type="number" class="cell-edit" data-field="edit_planned_distance" placeholder="単位 : km"></td>
        <td><input type="number" class="cell-edit" data-field="edit_condition"         placeholder="単位 : %"></td>
        <td><input type="number" class="cell-edit" data-field="edit_actual_distance"    placeholder="単位 : km"></td>
        <td>
            <button class="btn-edit is-editing" type="button" onclick="submitAdd(this)">登録</button>
            <button class="btn-delete" type="button" onclick="addCancel(this)">キャンセル</button>
        </td>`;
    tbody.prepend(tr);            // 最上位に挿入
}

// キャンセル → 追加行をDOMから消すだけ(DBは触っていない)
function addCancel(btn){
    btn.closest('tr').remove();
    isAdding = false;
}

// 登録 → POSTして '/' へ遷移
async function submitAdd(btn){
    const row = btn.closest('tr');
    const get = (field) => row.querySelector(`.cell-edit[data-field="${field}"]`).value;
    const [yyyy, mm, dd] = get('edit_date').split('-').map(Number);

    await fetch('/api/add/', {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            yyyy: yyyy, mm: mm, dd: dd,
            planned_distance: Number(get('edit_planned_distance')),
            condition:        Number(get('edit_condition')),
            actual_distance:  Number(get('edit_actual_distance')),
        }),
    });

    window.location.href = '/';   // getMethod(先頭ページ)へ
}