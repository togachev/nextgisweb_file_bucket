import { makeAutoObservable } from "mobx";

export type SetValue<T> = ((prevValue: T) => T) | T;

export class ResourceFileStore {
    id: number;
    sourceGroup = false; 
    listMaps: string[] = []; 

    constructor({ id, ...props }) {
        this.id = id
        for (const key in props) {
            const k = key;
            const prop = (props)[k];
            if (prop !== undefined) {
                Object.assign(this, { [k]: prop });
            }
        }

        makeAutoObservable(this, {});
    }

    setId = (id: number) => {
        this.id = id;
    };

    setSourceGroup = (sourceGroup: boolean) => {
        this.sourceGroup = sourceGroup;
    };

    setListMaps = (listMaps: SetValue<string>) => {
        this.setValue("listMaps", listMaps);
    };

    private setValue<T>(property: keyof this, valueOrUpdater: SetValue<T>) {
        const isUpdaterFunction = (
            input: unknown
        ): input is (prevValue: T) => T => {
            return typeof input === "function";
        };

        const newValue = isUpdaterFunction(valueOrUpdater)
            ? valueOrUpdater(this[property] as T)
            : valueOrUpdater;

        Object.assign(this, { [property]: newValue });
    }
}