import { observer } from "mobx-react-lite";
import { useMemo } from "react";

import { FileUploaderButton } from "@nextgisweb/file-upload/file-uploader";
import { ActionToolbar } from "@nextgisweb/gui/action-toolbar";
import { Button, Space } from "@nextgisweb/gui/antd";
import { EdiTable } from "@nextgisweb/gui/edi-table";
import type { EdiTableColumn } from "@nextgisweb/gui/edi-table/type";
import { formatSize } from "@nextgisweb/gui/util/formatSize";
import { gettext } from "@nextgisweb/pyramid/i18n";
import { layoutStore } from "@nextgisweb/pyramid/layout";
import type { EditorWidget } from "@nextgisweb/resource/type";

import type { ResourceFile, Store } from "./Store";

import ClearIcon from "@nextgisweb/icon/mdi/close";
import ArchiveIcon from "@nextgisweb/icon/mdi/zip-box";

import "./Widget.less";

function showError([status, msg]: [boolean, string | undefined | null]) {
    if (!status) {
        layoutStore.message?.error(msg);
    }
}

const columns: EdiTableColumn<ResourceFile>[] = [
    {
        key: "name",
        component: ({ value }) => <>{value}</>,
    },
    {
        key: "size",
        component: ({ value }) =>
            typeof value === "number" ? formatSize(value) : <></>,
    },
];

export const ResourceWidget: EditorWidget<Store> = observer(({ store }) => {
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
        [store]
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
                    <ActionToolbar pad borderBlockEnd actions={actions} />
                    <EdiTable
                        store={store}
                        columns={columns}
                        rowKey="id"
                        showHeader={false}
                        parentHeight
                    />
                </>
            )}
        </div>
    );
});

ResourceWidget.displayName = "ResourceWidget";
ResourceWidget.title = gettext("File bucket");
ResourceWidget.activateOn = { update: true };
