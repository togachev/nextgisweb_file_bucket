import { makeAutoObservable } from "mobx";

export type SetValue<T> = ((prevValue: T) => T) | T;

export class ResourceFileStore {
    defaultItems: string[] = [];
    defaultArray: number[] = [];
    isOpen = true;
    visibleFile: boolean;

    constructor({ visibleFile, ...props }) {
        this.visibleFile = visibleFile;
        for (const key in props) {
            const k = key;
            const prop = (props)[k];
            if (prop !== undefined) {
                Object.assign(this, { [k]: prop });
            }
        }

        makeAutoObservable(this, {});
    }

    setDefaultItems = (defaultItems: SetValue<string[]>) => {
        this.setValue("defaultItems", defaultItems);
    };

    setDefaultArray = (defaultArray: number[]) => {
        this.defaultArray = defaultArray;
    };

    setIsOpen = (isOpen: boolean) => {
        this.isOpen = isOpen;
    };

    setVisibleFile = (visibleFile: boolean) => {
        this.visibleFile = visibleFile;
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