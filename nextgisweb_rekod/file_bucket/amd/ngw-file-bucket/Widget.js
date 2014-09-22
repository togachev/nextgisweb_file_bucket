define([
    "dojo/_base/declare",
    "dojo/_base/lang",
    "dojo/_base/array",
    "dijit/layout/ContentPane",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "ngw-resource/serialize",
    // resource
    "dojo/text!./template/Widget.html",
    // template
    "ngw/form/UploaderList"
], function (
    declare,
    lang,
    array,
    ContentPane,
    _TemplatedMixin,
    _WidgetsInTemplateMixin,
    serialize,
    template
) {
    return declare([ContentPane, serialize.Mixin, _TemplatedMixin, _WidgetsInTemplateMixin], {
        templateString: template,
        title: "Набор файлов",
        serializePrefix: "file_bucket",

        postCreate: function () {
            this.inherited(arguments);
        },

        serializeInMixin: function (data) {
            if (data.file_bucket === undefined) { data.file_bucket = {}; }
            data.file_bucket.files = this.wFiles.get("value")['upload_meta'];
        }

    });
});