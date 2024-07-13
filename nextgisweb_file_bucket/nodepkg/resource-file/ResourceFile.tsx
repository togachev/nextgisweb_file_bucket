import { useEffect, useState, useMemo } from "react";
import { routeURL } from "@nextgisweb/pyramid/api";
import { Checkbox, Collapse, ConfigProvider, Table } from "@nextgisweb/gui/antd";
import type { CheckboxProps, CollapseProps } from "@nextgisweb/gui/antd";
import { gettext } from "@nextgisweb/pyramid/i18n";
import { observer } from "mobx-react-lite";
import { SvgIconLink } from "@nextgisweb/gui/svg-icon";
import { ResourceFileStore } from "./ResourceFileStore";
import "./ResourceFile.less";
import { useSource } from "./hook/useSource";

export const ResourceFile = observer(({ visibleFile, id, onValueChecked }) => {
    const [store] = useState(() => new ResourceFileStore({
        visibleFile: visibleFile
    }));

    const { listResourceFile } = useSource();

    useEffect(() => {
        store.setVisibleFile(visibleFile);
        listResourceFile(id)
            .then(items => {
                store.setDefaultItems(items.result);
                store.setDefaultArray(items.group);
            })
    }, [id])

    const columns = [
        {
            title: gettext("Name"),
            dataIndex: "name",
            key: "name",
            render: (name, item) => <a className="link-file" target="_blank" href={routeURL("resource.file_download", item.file_bucket_id, item.name)}>{item.name}</a>,
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

    const finalArray = store.defaultItems.map(obj => Object.assign(obj, { key: obj.id }))

    var groupBy = (items, key) => {
        return items.reduce((result, item) => {
            if (item[key] !== "default value from resources") {
                (result[item[key]] = result[item[key]] || []).push(item);
            }
            return result;
        }, {});
    };

    var itemsGroup = groupBy(finalArray, "res_name");

    const onChange: CheckboxProps["onChange"] = (e) => {
        onValueChecked(e.target.checked);
        store.setVisibleFile(e.target.checked);
    };

    const itemsFileList: CollapseProps["items"] = [];
    const onChangeCollapse = (key: string | string[]) => {
        console.log(key);
    };
    const genExtra = (items) => (
        <span
            className="icon-file-resource"
            onClick={(event) => {
                event.stopPropagation();
            }}>
            <SvgIconLink
                title={gettext("Info")}
                href={routeURL("resource.show", items[0].file_bucket_id)}
                icon="material-info"
                target="_blank"
                fill="currentColor"
            />
        </span>
    );

    Object.keys(itemsGroup).map((key, index) => {
        const items = itemsGroup[key];
        itemsFileList.push({
            key: index,
            label: key,
            children: <Table
                className="table-content"
                bordered
                pagination={false}
                columns={columns}
                dataSource={items}
            />,
            extra: genExtra(items),
        });
    })

    const VisibleFiles = gettext("Show/hide layer files");
    const EditLayerFiles = gettext("Edit layer files");

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
                    <Checkbox checked={store.visibleFile} onChange={onChange}>{VisibleFiles}</Checkbox>
                    {store.visibleFile && (<span title={VisibleFiles} className="icon-file-resource">
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
                {store.visibleFile && store.defaultArray.length > 0 && (
                    <Collapse
                        className="collapse-content"
                        size="small"
                        bordered={false}
                        defaultActiveKey={store.defaultArray}
                        onChange={onChangeCollapse}
                        // expandIconPosition={expandIconPosition}
                        items={itemsFileList}
                    />
                )}
            </ConfigProvider >
        </div>
    )
});