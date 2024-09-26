import { useState, useEffect } from "react";
import { route, routeURL } from "@nextgisweb/pyramid/api";
import { errorModal } from "@nextgisweb/gui/error";
import "./FileResource.less";
import { gettext } from "@nextgisweb/pyramid/i18n";
import Select from 'react-select';
import getSelectStyle from "./selectStyle";
import makeAnimated from 'react-select/animated';
import { Table } from "@nextgisweb/gui/antd";
import { SvgIconLink } from "@nextgisweb/gui/svg-icon";
import "./details.less";

const animatedComponents = makeAnimated();

export function FileResource(props) {
    const [items, setItems] = useState([]);
    const [defaultItems, setDefault] = useState([]);

    useEffect(() => {
        let isSubscribed = true;
        const getData = async () => {
            const allFile = props.fileList;
            const results = Object.values(props.fileList).filter(({ id: id1 }) => Object.values(props.fileItem).some(({ id: id2 }) => id2 === id1));

            if (isSubscribed) {
                setItems(allFile);
                setDefault(results);
            };
        }
        getData().catch(console.error);
        return () => {isSubscribed = false};
    }, []);

    const createItem = async (fid) => {
        try {
            await route("file_resource.create", props.id, fid).get();
        }
        catch (err) {
            errorModal(err);
        }
    }
    const deleteItem = async (fid) => {
        try {
            await route("file_resource.delete", props.id, fid).get();
        }
        catch (err) {
            errorModal(err);
        }
    }

    const deleteItems = async () => {
        try {
            await route("file_resource.delete_all", props.id).get();
        }
        catch (err) {
            errorModal(err);
        }
    }

    const onChange = (value, context) => {
        setDefault(value);
        if (context.action === "remove-value") {
            deleteItem(context.removedValue.id)
        }
        else if (context.action === "clear") {
            deleteItems()
        }
        else {
            createItem(context.option.id, context.option.name)
        }
    };
    
    const columns = [
        {
            title: gettext("Name"),
            dataIndex: 'name',
            key: 'name',
            render: (name, item) => <a className="link-file" target="_blank" href={routeURL('resource.file_download', item.file_bucket_id, item.name)} download>{item.name}</a>,
        },
        {
            title: gettext("MIME type"),
            dataIndex: 'mime_type',
            key: 'mime_type',
        },
        {
            title: gettext("Size, KB"),
            dataIndex: 'size',
            key: 'size',
            render: (size) => {
                return size >= 1024 ? (size / 1024).toFixed(1) : (size / 1024.0).toFixed(1)
            },
        },
    ];

    const selectBlock = <Select
        key={items}
        getOptionLabel={e => e.res_name + ': ' + e.name}
        getOptionValue={e => e.id}
        defaultValue={defaultItems}
        options={items}
        onChange={onChange}
        isMulti
        className="select-block"
        styles={getSelectStyle()}
        components={animatedComponents}
        closeMenuOnSelect={false}
        distance={4}
    />;

    const finalArray = defaultItems.map(obj => Object.assign(obj, {key: obj.id}))

    var groupBy = (items, key) => {
        return items.reduce((result, item) => {
            if (item[key] !== 'default value from resources') {
                (result[item[key]] = result[item[key]] || []).push(item);
            }
            return result;
        }, {});
    };

    var itemsGroup = groupBy(finalArray, 'res_name');
    console.log(itemsGroup);
    const [isOpen, setIsOpen] = useState('');
    
    useEffect(async () => {
        setIsOpen(true);
    }, [])

    return (
        <>
            {selectBlock}
            {            
                Object.keys(itemsGroup).map((key, value) => {
                    var items = itemsGroup[key];
                    var GroupObj = {}
                    GroupObj.res_name = key;
                    return (
                        <div key={value} className="groupDetails">
                            <details open={isOpen}>
                                <summary>
                                    <span className="summaryBlock">
                                        {GroupObj.res_name}
                                        <SvgIconLink
                                            href={routeURL('resource.show', items[0].file_bucket_id)}
                                            icon="material-info"
                                            target="_self"
                                            fill="currentColor"
                                        />
                                    </span>
                                </summary>
                                <Table
                                    className="table-striped-rows"
                                    pagination={false}
                                    columns={columns}
                                    dataSource={items}
                                />
                            </details>
                        </div>
                    )
                })
            }
        </>
    )
}


