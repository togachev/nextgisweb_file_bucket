import { action, observable } from "mobx";

export class ResourceFileStore {
    @observable.shallow accessor defaultItems: string[] = [];
    @observable.shallow accessor defaultArray: number[] = [];
    @observable.ref accessor isOpen: boolean = true;
    @observable.ref accessor visibleFile: boolean = false;

    constructor({ visibleFile, ...props }) {
        this.visibleFile = visibleFile;
        for (const key in props) {
            const k = key;
            const prop = (props)[k];
            if (prop !== undefined) {
                Object.assign(this, { [k]: prop });
            }
        }
    }

    @action
    setDefaultItems(defaultItems: string[]) {
        this.defaultItems = defaultItems;
    };

    @action
    setDefaultArray(defaultArray: number[]) {
        this.defaultArray = defaultArray;
    };

    @action
    setIsOpen(isOpen: boolean) {
        this.isOpen = isOpen;
    };

    @action
    setVisibleFile(visibleFile: boolean) {
        this.visibleFile = visibleFile;
    };
}