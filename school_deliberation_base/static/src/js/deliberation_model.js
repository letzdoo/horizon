/* global odoo, _ */
odoo.define("deliberation.DeliberationModel", function (require) {
    "use strict";

    var BasicModel = require("web.BasicModel");

    var DeliberationModel = BasicModel.extend({
        /**
         * @override
         */
        init: function () {
            this.programValues = {};
            this.courseValues = {};
            this._super.apply(this, arguments);
        },

        /**
         * @override
         */
        __get: function (localID) {
            var result = this._super.apply(this, arguments);
            if (this.programValues[localID]) {
                result.programValue = this.programValues[localID];
            }
            if (this.courseValues[localID]) {
                result.courseValues = this.courseValues[localID];
            }
            return result;
        },

        /**
         * @override
         * @returns {Promise}
         */
        __load: function () {
            return this._loadProgram(this._super.apply(this, arguments));
        },
        /**
         * @override
         * @returns {Promise}
         */
        __reload: function () {
            return this._loadProgram(this._super.apply(this, arguments));
        },

        /**
         * @private
         * @param {Promise} super_def a promise that resolves with a dataPoint id
         * @returns {Promise -> string} resolves to the dataPoint id
         */
        _loadProgram: function (super_def) {
            var self = this;
            return new Promise((resolve, reject) => {
                super_def.then(function (results) {
                    var localID = results;
                    if (self.loadParams.modelName == "school.individual_bloc") {
                        self._rpc({
                            model: "school.individual_program",
                            method: "read",
                            args: [
                                [
                                    self.localData[
                                        self.localData[localID].data.program_id
                                    ].data.id,
                                ],
                            ],
                        }).then(function (result) {
                            self.programValues[localID] = result[0];
                            self._rpc({
                                model: "school.individual_course",
                                method: "search_read",
                                domain: [
                                    ["bloc_id", "=", self.localData[localID].data.id],
                                ],
                                fields: [
                                    "course_group_id",
                                    "title",
                                    "teacher_id",
                                    "final_result",
                                    "final_result_disp",
                                ],
                            }).then(function (result) {
                                self.courseValues[localID] = result;
                                resolve(localID);
                            });
                        });
                    } else {
                        resolve(localID);
                    }
                });
            });
        },
    });
    return DeliberationModel;
});
