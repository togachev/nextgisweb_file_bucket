import { useEffect, useState, useMemo, useRef } from "react";
import { SearchOutlined } from "@ant-design/icons";
import { route, routeURL } from "@nextgisweb/pyramid/api";
import { Checkbox, ConfigProvider, Select } from "@nextgisweb/gui/antd";
import { gettext } from "@nextgisweb/pyramid/i18n";

import { observer } from "mobx-react-lite";

import { ResourceFileStore } from "./ResourceFileStore";
import "./ResourceFile.less";
import { useSource } from "./hook/useSource";

export const ResourceFile = observer(({ id }) => {
    const [store] = useState(() => new ResourceFileStore({
        id: id,
    }));
    console.log(id);
    
    const { ListFile, ListResourceFile, createItem, deleteItem, deleteItems } = useSource();

    useEffect(() => {
        store.setId(id);
        ListResourceFile(store.id)
            .then(item => {
                console.log(item);
            })
    }, []);

    useEffect(() => {
        store.setId(id);
        ListResourceFile(store.id)
            .then(item => {
                console.log(item);
            })
    }, [id]);

    return (
        <>
            <ConfigProvider
                theme={{
                    token: {
                    },
                    components: {
                    },
                }}
            >
                test
            </ConfigProvider >
        </>
    )
});