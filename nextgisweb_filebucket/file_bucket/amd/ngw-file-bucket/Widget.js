define([
    "dojo/_base/declare",
    "dojo/_base/lang",
    "dojo/_base/array",
    "dojo/dom-style",
    "dojo/dom-class",
    "dojo/dom-construct",
    "dojo/store/Memory",
    "dojo/store/Observable",
    "dijit/layout/LayoutContainer",
    "dijit/form/Button",
    "dijit/Toolbar",
    "dijit/ProgressBar",
    "dijit/Dialog",
    "dgrid/OnDemandGrid",
    "dgrid/Selection",
    "dgrid/editor",
    "dgrid/extensions/DijitRegistry",
    "ngw/route",
    "ngw-file-upload/FileUploader",
    "ngw-resource/serialize",
    "ngw-pyramid/i18n!file_bucket",
    // resource
    "xstyle/css!./resource/Widget.css",
    "ngw/dgrid/css"
], function (
    declare,
    lang,
    array,
    domStyle,
    domClass,
    domConstruct,
    Memory,
    Observable,
    LayoutContainer,
    Button,
    Toolbar,
    ProgressBar,
    Dialog,
    Grid,
    Selection,
    editor,
    DijitRegistry,
    route,
    Uploader,
    serialize,
    i18n
) {
    function fileSizeToString(size) {
        var units = ["B", "KB", "MB", "GB"];
        var i = 0;
        while (size >= 1024) {
            size /= 1024;
            ++i;
        }
        return size.toFixed(1) + " " + units[i];
    }


    var GridClass = declare([Grid, Selection, DijitRegistry], {
        selectionMode: "single",

        columns: [
            {
                field: "name",
                label: i18n.gettext("File name"),
                sortable: true
            },

            {
                field: "mime_type",
                label: i18n.gettext("MIME type"),
                sortable: true
            },

            {
                field: "size",
                label: i18n.gettext("Size"),
                sortable: true,
                formatter: fileSizeToString
            }
        ]
    });


    return declare([LayoutContainer, serialize.Mixin], {
        title: i18n.gettext("File bucket"),
        serializePrefix: "file_bucket",

        constructor: function () {
            this.store = new Observable(new Memory({idProperty: "name"}));
            this.archiveId = null;
        },

        buildRendering: function () {
            this.inherited(arguments);

            domClass.add(this.domNode, "ngw-file-bucket-widget");

            this.toolbar = new Toolbar({
                region: 'top'
            }).placeAt(this);

            this.uploaders = [];

            var fileUploader = new Uploader({
                label: i18n.gettext("Upload files"),
                iconClass: "dijitIconNewTask",
                multiple: true,
                uploadOnSelect: true,
                url: route.file_upload.upload(),
                name: "file"
            }).placeAt(this.toolbar);
            this.uploaders.push(fileUploader);

            fileUploader.on("complete", lang.hitch(this, function (data) {
                array.forEach(data.upload_meta, function (f) {
                    this.store.put(f);
                }, this);
            }));

            var ConfirmDialogClass = declare([Dialog], {
                title: i18n.gettext("Action confirmation"),
                style: "width: 400px",

                buildRendering: function () {
                    this.inherited(arguments);

                    this.contentArea = domConstruct.create("div", {
                        class: "dijitDialogPaneContentArea",
                        innerHTML: i18n.gettext("This operation will overwrite all resource files. Continue?")
                    }, this.containerNode);

                    this.actionBar = domConstruct.create("div", {
                        class: "dijitDialogPaneActionBar"
                    }, this.containerNode);

                    new Button({
                        label: i18n.gettext("OK"),
                        onClick: lang.hitch(this, function () {
                            this.hide();
                            this._callback(true);
                        })
                    }).placeAt(this.actionBar);

                    new Button({
                        label: i18n.gettext("Cancel"),
                        onClick: lang.hitch(this, function () {
                            this.hide();
                            this._callback(false);
                        })
                    }).placeAt(this.actionBar);
                },

                show: function (callback) {
                    this.inherited(arguments);
                    this._callback = callback;
                }
            });

            var _operation = this.composite.operation;
            var ArchiveUploaderClass = declare([Uploader], {
                label: i18n.gettext("Upload archive"),
                iconClass: "dijitIconDocuments",
                multiple: false,
                uploadOnSelect: true,
                url: route.file_upload.upload(),
                name: "file",
                _warned: false,
                _confirmDlg: ConfirmDialogClass(),
                upload: function () {
                    var args = arguments;
                    if (_operation === "create" || this._warned) {
                        this.inherited(args);
                    } else {
                        this._confirmDlg.show(lang.hitch(this, function (confirmed) {
                            this._warned = true;
                            if (confirmed) {
                                this.inherited(args);
                            } else {
                                this.reset();
                            }
                        }));
                    }
                }
            });

            var archiveUploader = ArchiveUploaderClass().placeAt(this.toolbar);
            this.uploaders.push(archiveUploader);

            archiveUploader.on("complete", lang.hitch(this, function (data) {
                this.store.query().forEach(function (f) { this.store.remove(f.name) }, this);
                this.archiveId = data.upload_meta[0].id;

                domClass.add(this.domNode, 'archive-loaded');
            }));

            this.uploaders.forEach(function(uploader) {
                uploader.on("complete", lang.hitch(this, function () {
                    domStyle.set(this.progressbar.domNode, 'display', 'none');
                }));
                uploader.on("begin", lang.hitch(this, function () {
                    domStyle.set(this.progressbar.domNode, 'display', 'block');
                }));
                uploader.on("progress", lang.hitch(this, function (evt) {
                    if (evt.type === "progress") {
                        this.progressbar.set('value', evt.decimal * 100);
                    }
                }));
            }, this);

            this.toolbar.addChild(new Button({
                label: i18n.gettext("Delete"),
                iconClass: "dijitIconDelete",
                onClick: lang.hitch(this, function () {
                    for (var key in this.grid.selection) {
                        this.store.remove(key);
                    }
                })
            }));

            this.progressbar = new ProgressBar({
                style: "float: right; margin-right: 4px; width: 10em; display: none;"
            }).placeAt(this.toolbar);

            this.grid = new GridClass({store: this.store});
            this.grid.region = "center";

            domClass.add(this.grid.domNode, "dgrid-border-fix");
            domStyle.set(this.grid.domNode, "border", "none");

            this.addChild(this.grid);
        },

        validateDataInMixin: function () {
            for (var i = 0; i < this.uploaders.length; i++) {
                if (this.uploaders[i].inProgress) {
                    return false;
                }
            }
            return true;
        },

        deserializeInMixin: function (data) {
            var files = data.file_bucket.files;
            for (var key in files) { this.store.add(files[key]) }
        },

        serializeInMixin: function (data) {
            if (data.file_bucket === undefined) { data.file_bucket = {}; }

            if (this.archiveId) {
                data.file_bucket.archive = {id: this.archiveId};

                this.archiveId = null;
            } else {
                data.file_bucket.files = [];

                var files = data.file_bucket.files;
                this.store.query().forEach(function (f) { files.push(f) });
            }
        }

    });
});
