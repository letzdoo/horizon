/* global odoo, _ */
odoo.define("deliberation.DeliberationView", function (require) {
    "use strict";

    var BasicView = require("web.BasicView");
    var view_registry = require("web.view_registry");
    var DeliberationController = require("deliberation.DeliberationController");
    var DeliberationModel = require("deliberation.DeliberationModel");
    var DeliberationRenderer = require("deliberation.DeliberationRenderer");

    var Pager = require("web.Pager");

    var DeliberationView = BasicView.extend({
        display_name: "Deliberation",
        icon: "fa-pagelines",
        cssLibs: ["/school_deliberation_base/static/src/css/deliberation.css"],
        config: _.extend({}, BasicView.prototype.config, {
            Model: DeliberationModel,
            Controller: DeliberationController,
            Renderer: DeliberationRenderer,
        }),
        viewType: "deliberation",
        withControlPanel: false,
        groupable: false,
        init: function () {
            this._super.apply(this, arguments);
        },
    });
    view_registry.add("deliberation", DeliberationView);
    return DeliberationView;
});
