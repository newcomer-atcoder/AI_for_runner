// 開発者向け管理画面(/intcode/)のフロントエンド制御
// 表示範囲(ページ)・月次レポートの絞り込み・ヘッダ表示はすべてここで完結する
// サーバ(api_int_code.py)はレコード全件と月ごとの集計値を返すだけ
document.addEventListener('DOMContentLoaded', () => {
    const UNIT = 10;            //1ページに表示する件数
    const NO_ITEM = 'no_item';  //「(未選択)」を表すメニューキー

    // 0. 各種DOM要素の取得
    const tbody           = document.querySelector('table tbody');
    const pagination      = document.querySelector('.pagination');
    const parent_area     = document.querySelector('.month-menu-parent-area');
    const month_view      = document.querySelector('.month-view');
    const month_menu_area = document.querySelector('.month-menu-area');
    const selected_tag    = document.querySelector('.month-selected');
    const page_label      = pagination.querySelector('[data-page-label]');
    const menus           = [...month_menu_area.querySelectorAll('.menu-item')];
    const allRows         = [...tbody.querySelectorAll('tr[data-id]')]; //サーバが描画した全レコード

    // 1. URLクエリから表示状態を復元する
    const params      = new URLSearchParams(window.location.search);
    const knownMonths = new Set(menus.map(menu => menu.dataset.month));
    let month    = knownMonths.has(params.get('month')) ? params.get('month') : NO_ITEM;
    let page     = Math.max(0, Number(params.get('page')) || 0);
    let isAdding = false;   //追加行の二重生成を防ぐフラグ

    //月次レポートで絞り込んだ後の行
    const filteredRows = () => {
        if(month === NO_ITEM) return allRows;
        const ym = menus.find(menu => menu.dataset.month === month).dataset.ym;
        return allRows.filter(row => row.dataset.ym === ym);
    };

    //最終ページ番号(0始まり)
    const lastPageNum = () => Math.max(0, Math.ceil(filteredRows().length / UNIT) - 1);

    //表示状態をURLへ反映しておく(リロード後も復元できるようにする)
    const syncUrl = () =>
        history.replaceState(null, '', `/intcode/?page=${page}&month=${month}`);

    //現在の表示状態を保ったままリロードする(追加・更新・削除の後に使う)
    const reload = () => {
        window.location.href = `/intcode/?page=${page}&month=${month}`;
    };

    // 2. 描画: 画面の更新はすべてこの関数を通す
    function render(){
        //編集中・追加中の行をリセットする(現行はページ遷移のたびに閲覧表示へ戻っていた)
        tbody.querySelectorAll('tr.editing').forEach(row => {
            if(row.dataset.id === undefined) row.remove(); //追加行は破棄
            else                             editCancel(row);
        });
        isAdding = false;

        //ページ番号を有効範囲へ丸める(月を切り替えて件数が減っても空表示にならない)
        const rows = filteredRows();
        page = Math.min(Math.max(page, 0), lastPageNum());

        //表示するレコードの切り替え(絞り込み後の配列内での位置で判定する)
        allRows.forEach(row => { row.hidden = true; });
        rows.slice(page * UNIT, (page + 1) * UNIT).forEach(row => { row.hidden = false; });

        //ヘッダ(年月ラベル・集計値・「(選択中)」バッジ)
        //未選択のときは今月の集計を表示する
        const statKey = (month === NO_ITEM) ? 'this_month' : month;
        const stat    = menus.find(menu => menu.dataset.month === statKey);
        document.querySelectorAll('[data-stat="ym"]').forEach(elem => {
            elem.textContent = stat.dataset.ym;
        });
        document.querySelector('[data-stat="run_cnt"]').textContent       = stat.dataset.runCnt;
        document.querySelector('[data-stat="condition_ave"]').textContent = stat.dataset.conditionAve;
        document.querySelector('[data-stat="distance_sum"]').textContent  = stat.dataset.distanceSum;
        selected_tag.hidden = (month === NO_ITEM);

        //ページャ(◀◀ ◀ ▶ ▶▶ の表示可否とページ番号)
        const setHidden = (action, hidden) => {
            pagination.querySelector(`[data-action="${action}"]`).hidden = hidden;
        };
        page_label.textContent = page;
        setHidden('first', page === 0);
        setHidden('prev',  page === 0);
        setHidden('next',  page === lastPageNum());
        setHidden('last',  page === lastPageNum());

        syncUrl();
    }

    // 3. レコード操作
    const cellValue = (row, field) =>
        row.querySelector(`.cell-edit[data-field="${field}"]`).value;

    async function deleteRecord(id){
        await fetch(
            '/api/delete/',
            {
                method: "DELETE",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({id: Number(id)})
            }
        );

        reload();
    }

    //編集モードへの切り替え / 編集中なら更新を送信する
    function editRecord(row){
        if(!row.classList.contains('editing')){
            row.querySelectorAll('.cell-view').forEach(elem => {elem.hidden = true;});
            row.querySelectorAll('.cell-edit').forEach(elem => {elem.hidden = false;});
            row.classList.add('editing');
        }
        else{
            submitUpdate(row); //レコード更新を実行
        }
    }

    //閲覧用画面に戻る
    function editCancel(row){
        row.querySelectorAll('.cell-view').forEach(elem => {elem.hidden = false;});
        row.querySelectorAll('.cell-edit').forEach(elem => {elem.hidden = true;});
        row.classList.remove('editing');
    }

    async function submitUpdate(row){
        const [yyyy, mm, dd] = cellValue(row, 'edit_date').split('-').map(Number);

        // レコード更新をリクエスト
        await fetch(
            '/api/submit/',
            {
                method: 'PUT',
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(
                    {
                        id: Number(row.dataset.id),
                        yyyy: yyyy, mm: mm, dd: dd,
                        planned_distance: Number(cellValue(row, 'edit_planned_distance')),
                        condition:        Number(cellValue(row, 'edit_condition')),
                        actual_distance:  Number(cellValue(row, 'edit_actual_distance'))
                    }
                )
            }
        );

        reload();
    }

    // ◀▶右隣の「追加」: 0ページ目の最上位に編集可能な行を1行差し込む
    function addRecord(){
        //0ページ目以外なら、まず0ページ目へ寄せてから追加させる(状態を持ち越さないシンプル方式)
        if(page !== 0){
            page = 0;
            render();
            return;
        }
        if(isAdding) return;          //既に1行追加済みなら何もしない
        isAdding = true;

        const tr = document.createElement('tr');
        tr.classList.add('editing');  //data-id は付けない(レコード行と区別するため)
        tr.innerHTML = `
            <td><span class="id-badge">新規</span></td>
            <td><input type="date"   class="cell-edit" data-field="edit_date"></td>
            <td><input type="number" class="cell-edit" data-field="edit_planned_distance" placeholder="単位 : km"></td>
            <td><input type="number" class="cell-edit" data-field="edit_condition"         placeholder="単位 : %"></td>
            <td><input type="number" class="cell-edit" data-field="edit_actual_distance"    placeholder="単位 : km"></td>
            <td>
                <button class="btn-edit is-editing" type="button" data-action="add-submit">登録</button>
                <button class="btn-delete" type="button" data-action="add-cancel">キャンセル</button>
            </td>`;
        tbody.prepend(tr);            //最上位に挿入
    }

    // 登録 → POSTして現在の表示状態のままリロード
    async function submitAdd(row){
        const [yyyy, mm, dd] = cellValue(row, 'edit_date').split('-').map(Number);

        await fetch('/api/add/', {
            method: 'POST',
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                yyyy: yyyy, mm: mm, dd: dd,
                planned_distance: Number(cellValue(row, 'edit_planned_distance')),
                condition:        Number(cellValue(row, 'edit_condition')),
                actual_distance:  Number(cellValue(row, 'edit_actual_distance')),
            }),
        });

        reload();
    }

    // 4. イベント登録(すべて委譲。インラインonclickは使わない)
    //ページャ・追加・戻る
    pagination.addEventListener('click', (event) => {
        const btn = event.target.closest('button[data-action]');
        if(!btn) return;

        switch(btn.dataset.action){
            case 'first': page = 0;             render(); break;
            case 'prev':  page -= 1;            render(); break;
            case 'next':  page += 1;            render(); break;
            case 'last':  page = lastPageNum(); render(); break;
            case 'add':   addRecord();                    break;
            case 'back':  window.location.href = '/entry/'; break; //登録画面へ戻る
        }
    });

    //表内のボタン(編集/登録/削除/キャンセル)。動的に挿入した追加行もここで拾える
    tbody.addEventListener('click', (event) => {
        const btn = event.target.closest('button[data-action]');
        if(!btn) return;
        const row = btn.closest('tr');

        switch(btn.dataset.action){
            case 'edit':        editRecord(row);                break;
            case 'edit-cancel': editCancel(row);                break;
            case 'delete':      deleteRecord(row.dataset.id);   break;
            case 'add-submit':  submitAdd(row);                 break;
            case 'add-cancel':  row.remove(); isAdding = false; break;
        }
    });

    //「📄Monthly Report」にポインターを置くとき、離すときの動作
    month_view.addEventListener('pointerover', () => {
        month_menu_area.hidden = false;
    });

    parent_area.addEventListener('pointerleave', () => {
        month_menu_area.hidden = true;
    });

    //menu-itemがクリックされたとき: ページ遷移せずその場で表示を切り替える
    menus.forEach((menu) => {
        menu.addEventListener('click', () => {
            month = menu.dataset.month;
            page  = 0;                      //月を切り替えたら先頭ページへ
            month_menu_area.hidden = true;
            render();
        });
    });

    // 5. 初回描画
    render();
});
