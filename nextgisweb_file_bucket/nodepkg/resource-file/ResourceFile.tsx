import { useEffect, useState, useMemo, useRef } from "react";
import { SearchOutlined } from "@ant-design/icons";
import { route, routeURL } from "@nextgisweb/pyramid/api";
import { Checkbox, ConfigProvider, Select, Table } from "@nextgisweb/gui/antd";
import { gettext } from "@nextgisweb/pyramid/i18n";
// import Select from "react-select";
// import getSelectStyle from "./selectStyle";
import makeAnimated from 'react-select/animated';
import { observer } from "mobx-react-lite";
import { SvgIconLink } from "@nextgisweb/gui/svg-icon";
import { ResourceFileStore } from "./ResourceFileStore";
import "./ResourceFile.less";
import { useSource } from "./hook/useSource";

const animatedComponents = makeAnimated();

export const ResourceFile = observer(({ styleId }) => {
    const [store] = useState(() => new ResourceFileStore({
        id: styleId
    }));
    // console.log(styleId);

    const { createItem, listFile, listResourceFile, deleteItem, deleteItems, ResourceFile } = useSource();

    useMemo(() => {
        listFile()
            .then(items => {
                store.setResourceFile(items);
            })
        listResourceFile(styleId)
            .then(items => {
                console.log(items);
                
                store.setDefaultItems(items);
            })
    }, [styleId]);
    console.log(store.resourceFile, store.defaultItems);
    // useEffect(() => {
    //     ResourceFile(styleId)
    //         .then(item => {
    //             console.log(item);
    //         })
    // }, [styleId]);

    // const onChange = (value, context) => {
    //     store.setDefaultItems(value);
    //     if (context.action === "remove-value") {
    //         deleteItem(styleId, context.removedValue.id)
    //     }
    //     else if (context.action === "clear") {
    //         deleteItems(styleId)
    //     }
    //     else {
    //         createItem(styleId, context.option.id)
    //     }
    // };
    
    // const columns = [
    //     {
    //         title: gettext("Name"),
    //         dataIndex: 'name',
    //         key: 'name',
    //         render: (name, item) => <a className="link-file" target="_blank" href={routeURL('resource.file_download', item.file_bucket_id, item.name)}>{item.name}</a>,
    //     },
    //     {
    //         title: gettext("MIME type"),
    //         dataIndex: 'mime_type',
    //         key: 'mime_type',
    //     },
    //     {
    //         title: gettext("Size, KB"),
    //         dataIndex: 'size',
    //         key: 'size',
    //         render: (size) => {
    //             return size >= 1024 ? (size / 1024).toFixed(1) : (size / 1024.0).toFixed(1)
    //         },
    //     },
    // ];
    // console.log(store.defaultItems);
    
    // const selectBlock = <Select
    //     key={store.resourceFile}
    //     getOptionLabel={e => e.res_name + ': ' + e.name}
    //     getOptionValue={e => e.id}
    //     defaultValue={store.defaultItems}
    //     options={store.resourceFile}
    //     onChange={onChange}
    //     isMulti
    //     className="select-block"
    //     styles={getSelectStyle()}
    //     components={animatedComponents}
    //     closeMenuOnSelect={false}
    //     distance={4}
    // />;

    // const finalArray = store.defaultItems.map(obj => Object.assign(obj, {key: obj.id}))

    // var groupBy = (items, key) => {
    //     return items.reduce((result, item) => {
    //         if (item[key] !== 'default value from resources') {
    //             (result[item[key]] = result[item[key]] || []).push(item);
    //         }
    //         return result;
    //     }, {});
    // };

    // var itemsGroup = groupBy(finalArray, 'res_name');

    // useEffect(async () => {
    //     store.setIsOpen(true);
    // }, [])


    return (
        <div className="resource-file-component">
            <ConfigProvider
                theme={{
                    token: {
                    },
                    components: {
                    },
                }}
            >
            {/* {selectBlock}
            {            
                Object.keys(itemsGroup).map((key, value) => {
                    var items = itemsGroup[key];
                    var GroupObj = {}
                    GroupObj.res_name = key;
                    return (
                        <div key={value} className="groupDetails">
                            <details open={store.isOpen}>
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
            } */}
            </ConfigProvider >
        </div>
    )
});