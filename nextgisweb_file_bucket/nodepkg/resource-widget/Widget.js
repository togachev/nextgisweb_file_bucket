import { observer } from "mobx-react-lite";
import { useMemo } from "react";

import { EdiTable } from "@nextgisweb/gui/edi-table";
import { Space, Button, message } from "@nextgisweb/gui/antd";
import { gettext } from "@nextgisweb/pyramid/i18n";
import { ActionToolbar } from "@nextgisweb/gui/action-toolbar";
import { FileUploaderButton } from "@nextgisweb/file-upload/file-uploader";
import { formatSize } from "@nextgisweb/gui/util/formatSize";

import ArchiveIcon from "@nextgisweb/icon/mdi/zip-box";
import ClearIcon from "@nextgisweb/icon/mdi/close";

import "./Widget.less";

function showError([status, msg]) {
    if (!status) message.error(msg);
}

const columns = [
    {
        key: "name",
        component: ({ value }) => value,
    },
    {
        key: "size",
        component: ({ value }) => (value ? formatSize(value) : <></>),
    },
];

export const Widget = observer(({ store }) => {
    const actions = useMemo(
        () => [
            <FileUploaderButton
                key="file"
                multiple={true}
                onChange={(value) => {
                    if (!value) return;
                    showError(store.appendFiles(value));
                }}
                uploadText={gettext("Add files")}
            />,
            <FileUploaderButton
                key="archive"
                accept=".zip"
                onChange={(value) => {
                    if (!value) return;
                    showError(store.fromArchive(value));
                }}
                uploadText={gettext("Import from ZIP archive")}
            />,
        ],
        []
    );

    return (
        <div className="ngw-file-bucket-resource-widget">
            {store.archive ? (
                <div className="archive">
                    <Space>
                        {gettext("Files will be imported from:")}
                        <ArchiveIcon />
                        {store.archive.name}
                        <Button
                            onClick={() => store.fromArchive(null)}
                            icon={<ClearIcon />}
                            type="text"
                            shape="circle"
                        />
                    </Space>
                </div>
            ) : (
                <>
                    <ActionToolbar actions={actions} />
                    <EdiTable
                        {...{ store, columns }}
                        rowKey="id"
                        showHeader={false}
                        parentHeight
                    />
                </>
            )}
        </div>
    );
});

Widget.title = gettext("File bucket");
Widget.activateOn = { update: true };
