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