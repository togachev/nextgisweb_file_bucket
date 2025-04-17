import { useEffect, useState } from "react";
import { routeURL } from "@nextgisweb/pyramid/api";
import { Checkbox, Collapse, ConfigProvider, Table } from "@nextgisweb/gui/antd";
import type { CheckboxProps, CollapseProps } from "@nextgisweb/gui/antd";
import { gettext } from "@nextgisweb/pyramid/i18n";
import { observer } from "mobx-react-lite";
import { SvgIconLink } from "@nextgisweb/gui/svg-icon";
import { ResourceFileStore } from "./ResourceFileStore";

import "./ResourceFile.less";
import { useSource } from "./hook/useSource";

export const ResourceFile = observer(({ value, id, onChange }) => {
    const { listResourceFile } = useSource();
    const [store] = useState(() => new ResourceFileStore({
        visibleFile: value
    }));

    useEffect(() => {
        store.setVisibleFile(value);
        listResourceFile(id)
            .then(items => {
                store.setDefaultItems(items);
            })
    }, [id])

    const columns = [
        {
            title: gettext("Name"),
            dataIndex: "name",
            key: "name",
            render: (name, item) => <a className="link-file" target="_blank" href={routeURL("resource.file_download", item.file_bucket_id, item.name)} download>{item.name}</a>,
        },
        {
            title: gettext("MIME type"),
            dataIndex: "mime_type",
            key: "mime_type",
        },
        {
            title: gettext("Size, KB"),
            dataIndex: "size",
            key: "size",
            render: (size) => {
                return size >= 1024 ? (size / 1024).toFixed(1) : (size / 1024.0).toFixed(1)
            },
        },
    ];

    const onValueChecked: CheckboxProps["onChange"] = (e) => {
        onChange(e.target.checked);
        store.setVisibleFile(e.target.checked);
    };

    const genExtra = (id) => {
        return (
            <span
                className="icon-file-resource"
                onClick={(event) => {
                    event.stopPropagation();
                }}>
                <SvgIconLink
                    href={routeURL("resource.show", id)}
                    icon="material-info"
                    target="_blank"
                    fill="currentColor"
                />
            </span>
        )
    };

    const EditLayerFiles = gettext("Edit attached files");
    const msgVisibleResoureFile = store.visibleFile ? gettext("Hide attached Files") : gettext("Show attached files");

    return (
        <div className="resource-file-component">
            <ConfigProvider
                theme={{
                    token: {
                    },
                    components: {
                        Table: {
                            cellPaddingBlock: 2,
                            cellPaddingInline: 5,
                        },
                    },
                }}
            >
                <div className="file-visible">
                    <Checkbox checked={store.visibleFile} onChange={onValueChecked}>{msgVisibleResoureFile}</Checkbox>
                    {store.visibleFile && (<span className="icon-file-resource">
                        <SvgIconLink
                            href={routeURL("file_resource.settings", id)}
                            icon="material-edit"
                            target="_blank"
                            fill="currentColor"
                        >
                            <span className="name-style" title={EditLayerFiles}>{EditLayerFiles}</span>
                        </SvgIconLink>
                    </span>)}
                </div>
                {store.visibleFile && Object.entries(store.defaultItems).map((item, index) => {
                    const label = item[0];
                    const data = item[1];
                    const id = data[0].file_bucket_id;
                    const itemsFileList: CollapseProps["items"] = [];
                    const defaultActiveKey: number[] = [];
                    defaultActiveKey.push(index)
                    itemsFileList.push({
                        key: index,
                        label: label,
                        children: <Table
                            className="table-content"
                            bordered
                            pagination={false}
                            columns={columns}
                            dataSource={data}
                        />,
                        extra: genExtra(id),
                    })

                    return (
                        <Collapse
                            key={index}
                            className="collapse-content"
                            size="small"
                            bordered={false}
                            defaultActiveKey={store.isOpen ? defaultActiveKey : undefined}
                            items={itemsFileList}
                        />
                    )
                })}
            </ConfigProvider >
        </div>
    )
});