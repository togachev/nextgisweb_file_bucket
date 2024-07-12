import { makeAutoObservable } from "mobx";

export type SetValue<T> = ((prevValue: T) => T) | T;

export class ResourceFileStore {
    id: number;
    resourceFileGroup = false; 
    resourceFile: string[] = []; 
    defaultItems: string[] = []; 
    isOpen = false;

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

    setData = (id: number) => {
        this.id = id;
    };

    setResourceFileGroup = (resourceFileGroup: boolean) => {
        this.resourceFileGroup = resourceFileGroup;
    };

    setResourceFile = (resourceFile: SetValue<string>) => {
        this.setValue("resourceFile", resourceFile);
    };

    setDefaultItems = (defaultItems: SetValue<string>) => {
        this.setValue("defaultItems", defaultItems);
    };

    setIsOpen = (isOpen: boolean) => {
        this.isOpen = isOpen;
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