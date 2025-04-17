import { useMemo, useState } from "react";
import { route, routeURL } from "@nextgisweb/pyramid/api";
import { gettext } from "@nextgisweb/pyramid/i18n";
import { errorModal } from "@nextgisweb/gui/error";
import { Collapse, ConfigProvider, Select, Table } from "@nextgisweb/gui/antd";
import { observer } from "mobx-react-lite";
import type { CollapseProps, TableProps } from "@nextgisweb/gui/antd";
import { CaretRightOutlined } from '@ant-design/icons';
import { SvgIconLink } from "@nextgisweb/gui/svg-icon";
import "./PublicFiles.less";
import { PublicFilesStore } from "./PublicFilesStore";

const createItem = async (id, fid) => {
    try {
        await route("file_resource.create", id, fid).get();
    }
    catch (err) {
        errorModal(err);
    }
}

const deleteItem = async (id, fid) => {
    try {
        await route("file_resource.delete", id, fid).get();
    }
    catch (err) {
        errorModal(err);
    }
}

const deleteItems = async (id) => {
    try {
        await route("file_resource.delete_all", id).get();
    }
    catch (err) {
        errorModal(err);
    }
}

export const PublicFiles = observer((props) => {
    const [store] = useState(() => new PublicFilesStore({
        defaultItems: props.fileList.filter((item) => props.fileItem.some((id2) => id2 === item.id))
    }));
    
    const items = props.fileList;

    const fileColumns: TableProps["items"] = [
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

    const finalArray = store.defaultItems.map(obj => Object.assign(obj, { key: obj.id }))

    const groupBy = (items, key) => {
        return items.reduce((result, item) => {
            (result[item[key]] = result[item[key]] || []).push(item);
            return result;
        }, {});
    };

    const itemsGroup = groupBy(finalArray, "res_name");
    
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

    const itemsCollapse = useMemo(() => {
        const items: CollapseProps["items"] = [];
        const defaultActiveKey: string[] = [];

        Object.keys(itemsGroup).map((key, value) => {
            const file_bucket_id = itemsGroup[key][0].file_bucket_id;
            defaultActiveKey.push(value.toString())
            items.push({
                key: value,
                label: key,
                children: (
                    <Table
                        className="table-rows"
                        pagination={false}
                        columns={fileColumns}
                        dataSource={itemsGroup[key].sort((a, b) => (a.name || "").localeCompare(b.name || ""))}
                        size="small"
                    />
                ),
                extra: genExtra(file_bucket_id)
            })
        })

        return (
            <Collapse
                key={store.defaultItems.length}
                items={items.sort((a, b) => (a.label || "").localeCompare(b.label || ""))}
                bordered={false}
                ghost
                defaultActiveKey={defaultActiveKey}
                expandIcon={({ isActive }) => <CaretRightOutlined rotate={isActive ? 90 : 0} />}
                className="collapse-content"
            />
        );
    }, [store.defaultItems]);

    const onChange = (e) => {
        store.setDefaultItems(items.filter((item) => e.some((s) => s.value === item.id)));
    };

    const onDeselect = (e) => {
        deleteItem(props.id, e.value);
        store.setDefaultItems(store.defaultItems.filter((item) => item.id !== e.value));
    }

    const onSelect = (e) => {
        createItem(props.id, e.value);
    }

    const onClear = () => {
        deleteItems(props.id);
    }

    const filterOption = (input: string, option?: { label: string; value: string; desc: string }) => {
        if ((option?.label ?? "").toLowerCase().includes(input.toLowerCase()) ||
            (option?.desc ?? "").toLowerCase().includes(input.toLowerCase()))
            return true
    }

    const filterSort = (optionA, optionB) => (optionA?.label ?? '').toLowerCase().localeCompare((optionB?.label ?? '').toLowerCase())

    return (
        <div className="public-files-component">
            <ConfigProvider
                theme={{
                    token: {
                    },
                    components: {
                        Collapse: {
                            headerPadding: "2px 8px",
                            contentPadding: "0px 0px",
                            paddingSM: "6px"
                        },
                    },
                }}
            >
                <Select
                    defaultValue={store.defaultItems}
                    style={{ width: "100%" }}
                    onChange={onChange}
                    onDeselect={onDeselect}
                    onSelect={onSelect}
                    onClear={onClear}
                    options={items}
                    mode="multiple"
                    labelInValue
                    maxTagCount={1}
                    filterOption={filterOption}
                    filterSort={filterSort}
                    allowClear
                />
                {itemsCollapse}
            </ConfigProvider >
        </div >
    )
});