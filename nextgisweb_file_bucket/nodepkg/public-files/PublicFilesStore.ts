import { action, observable } from "mobx";

export interface FileProps {
    id: number;
    file_bucket_id: number;
    fileobj_id: number;
    name: string;
    mime_type: string;
    size: number;
    res_name: string;
}

export class PublicFilesStore {
    @observable.shallow accessor defaultItems: FileProps[] = [];

    constructor({ ...props }) {
        for (const key in props) {
            const k = key;
            const prop = (props)[k];
            if (prop !== undefined) {
                Object.assign(this, { [k]: prop });
            }
        }
    }

    @action
    setDefaultItems(defaultItems: FileProps[]) {
        this.defaultItems = defaultItems;
    };
}