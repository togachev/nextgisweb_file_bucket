define([
    "dojo/_base/declare",
    "dojo/_base/lang",
    "dojo/_base/array",
    "dojo/dom-style",
    "dojo/dom-class",   
    "dojo/store/Memory",
    "dojo/store/Observable",
    "dijit/layout/LayoutContainer",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "dijit/form/Button",
    "dijit/ProgressBar",
    "dojox/form/Uploader",
    "dgrid/OnDemandGrid",
    "dgrid/Selection",
    "dgrid/editor",
    "dgrid/extensions/DijitRegistry",    
    "ngw/route",
    "ngw-resource/serialize",
    // resource
    "dojo/text!./template/Widget.html"
], function (
    declare,
    lang,
    array,
    domStyle,
    domClass,
    Memory,
    Observable,
    LayoutContainer,
    _TemplatedMixin,
    _WidgetsInTemplateMixin,
    Button,
    ProgressBar,
    Uploader,
    Grid,
    Selection,
    editor,
    DijitRegistry,
    route,
    serialize,
    template
) {
    // Uploader AMD workaround
    Uploader = dojox.form.Uploader;    

    var GridClass = declare([Grid, Selection, DijitRegistry], {
        selectionMode: "single",

        columns: [
            {
                field: "name",
                label: "Имя файла",
                sortable: true
            },

            {
                field: "mime",
                label: "Тип MIME",
                sortable: true
            },

            {
                field: "size",
                label: "Размер",
                sortable: true
            }
        ]
    });


    return declare([LayoutContainer, serialize.Mixin, _TemplatedMixin, _WidgetsInTemplateMixin], {
        templateString: template,
        title: "Набор файлов",
        serializePrefix: "file_bucket",

        constructor: function () {
            this.store = new Observable(new Memory({idProperty: "name"}));
        },

        buildRendering: function () {
            this.inherited(arguments);

            this.uploader = new Uploader({
                label: "Загрузить файлы",
                iconClass: "dijitIconNewTask",
                multiple: true,
                uploadOnSelect: true,
                url: route.file_upload.upload(),
                name: "file"
            }).placeAt(this.toolbar);

            this.uploader.on("complete", lang.hitch(this, function (data) {
                array.forEach(data.upload_meta, function (f) {
                    f.mime = f.mime_type; f.mime_type = undefined;
                    this.store.put(f);
                }, this);

                domStyle.set(this.progressbar.domNode, 'display', 'none');
            }));

            this.uploader.on("begin", lang.hitch(this, function () {
                domStyle.set(this.progressbar.domNode, 'display', 'block');
            }));

            this.uploader.on("progress", lang.hitch(this, function (evt) {
                if (evt.type == "progress") {
                    this.progressbar.set('value', evt.decimal * 100);
                }
            }));

            this.toolbar.addChild(new Button({
                label: "Удалить",
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

        deserializeInMixin: function (data) {
            var files = data.file_bucket.files,
                store = this.store;

            for (var key in files) {
                var value = files[key];
                store.add(value);
            }
        },       

        serializeInMixin: function (data) {
            if (data.file_bucket === undefined) { data.file_bucket = {}; }
            data.file_bucket.files = [];

            var files = data.file_bucket.files;
            this.store.query().forEach(function (f) { files.push(f) });
        }

    });
});