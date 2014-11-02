<table class="pure-table pure-table-horizontal" style="width: 100%">
    <thead>
        <tr>
            <th style="width: 5%">#</th>
            <th style="width: 75%">Наименование</th>
            <th style="width: 25%">Тип MIME</th>
            <th style="width: 0%; white-space: nowrap;">Размер, КБ</th>
        </tr>
    </thead>
    %for idx, fobj in enumerate(obj.files, start=1):
        <tr>
            <td>${idx}</td>
            <td>
                <a href="${request.route_url('file_bucket.file_download', id=obj.id, name=fobj.name)}">
                ${fobj.name}
                </a>
            </td>
            <td>${fobj.mime}</td>
            <td>${fobj.size / 1024}</td>
        </tr>
    %endfor
</table>