import { useEffect, useState, useMemo, useRef } from "react";
import { SearchOutlined } from "@ant-design/icons";
import { route, routeURL } from "@nextgisweb/pyramid/api";
import { Checkbox, ConfigProvider, Select } from "@nextgisweb/gui/antd";
import { gettext } from "@nextgisweb/pyramid/i18n";

import { observer } from "mobx-react-lite";

import { ResourceFileStore } from "./ResourceFileStore";
import "./ResourceFile.less";
import { useSource } from "./hook/useSource";

export const ResourceFile = observer(({ styleId }) => {
    const [store] = useState(() => new ResourceFileStore({
        id: styleId,
    }));
    console.log(styleId);
    
    const { ListFile, ListResourceFile, createItem, deleteItem, deleteItems } = useSource();

    useEffect(() => {
        ListResourceFile(styleId)
            .then(item => {
                console.log(item);
            })
    }, []);

    useEffect(() => {
        ListResourceFile(styleId)
            .then(item => {
                console.log(item);
            })
    }, [styleId]);

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