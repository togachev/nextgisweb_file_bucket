import { makeAutoObservable, toJS } from "mobx";
import { gettext } from "@nextgisweb/pyramid/i18n";

let idSeq = 0;

class File {
    name = undefined;
    size = undefined;
    mime_type = undefined;
    file = undefined;

    constructor(store, { name, size, mime_type, file }) {
        makeAutoObservable(this);
        this.store = store;
        this.id = ++idSeq;
        this.name = name;
        this.size = size;
        this.mime_type = mime_type;
        this.file = file;
    }
}

export class Store {
    identity = "file_bucket";

    files = null;
    archive = null;
    dirty = false;

    constructor() {
        makeAutoObservable(this, { identity: false });
        this.files = [];
    }

    load(value) {
        this.files = value.files.map((data) => new File(this, data));
        this.archive = null;
        this.dirty = false;
    }

    dump() {
        if (!this.dirty) return undefined;
        const result = {};
        if (this.archive) {
            result.archive = this.archive;
        } else {
            // eslint-disable-next-line no-unused-vars
            result.files = this.files.map(({ store, id, file, ...rest }) =>
                file ? { id: file.id, ...rest } : rest
            );
        }
        return toJS(result);
    }

    get isValid() {
        return true;
    }

    appendFiles(files) {
        const updated = [...this.files];
        for (const file of files) {
            const { name, size, mime_type } = file;
            const existing = updated.find((c) => c.name === name);
            if (existing) updated.splice(updated.indexOf(existing), 1);
            updated.push(new File(this, { name, size, mime_type, file }));
        }
        this.files = updated;
        this.dirty = true;
        return [true, null];
    }

    fromArchive(archive) {
        const { name } = archive || {};
        if (name && !name.toLowerCase().endsWith(".zip")) {
            return [false, gettext("ZIP archive required")];
        }

        this.archive = archive;
        this.dirty = true;
        return [true, null];
    }

    // EdiTable

    get rows() {
        return this.files;
    }

    deleteRow(row) {
        this.rows.splice(this.rows.indexOf(row), 1);
        this.dirty = true;
    }
}
