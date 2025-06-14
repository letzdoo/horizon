/* global odoo */
odoo.define("deliberation.DeliberationModel", function (require) {
    "use strict";

    var BasicModel = require("web.BasicModel");

    var DeliberationModel = BasicModel.extend({
        /**
         * @override
         */
        init: function () {
            this.programValues = {};
            this.courseGroupValues = {};
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
            if (this.courseGroupValues[localID]) {
                result.courseGroupValues = this.courseGroupValues[localID];
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
                super_def
                    .then(function (results) {
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
                                const courseGroupPromise = self._rpc({
                                    model: "school.individual_course_group",
                                    method: "search_read",
                                    domain: [
                                        [
                                            "bloc_id",
                                            "=",
                                            self.localData[localID].data.id,
                                        ],
                                    ],
                                    fields: [
                                        "uid",
                                        "name",
                                        "display_name",
                                        "title",
                                        "year_id",
                                        "course_ids",
                                        "responsible_id",
                                        "final_result",
                                        "final_result_disp",
                                        "total_credits",
                                        "total_hours",
                                        "acquiered",
                                    ],
                                }).then(function (result) {
                                    self.courseGroupValues[localID] = result;
                                });

                                const coursePromise = self._rpc({
                                    model: "school.individual_course",
                                    method: "search_read",
                                    domain: [
                                        [
                                            "bloc_id",
                                            "=",
                                            self.localData[localID].data.id,
                                        ],
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
                                });

                                Promise.all([courseGroupPromise, coursePromise]).then(function () {
                                    resolve(localID);
                                });
                            });
                        } else {
                            self._rpc({
                                model: "school.individual_course_group",
                                method: "search_read",
                                domain: [
                                    [
                                        "program_id",
                                        "=",
                                        self.localData[localID].data.id,
                                    ],
                                ],
                                fields: [
                                    "uid",
                                    "name",
                                    "display_name",
                                    "title",
                                    "year_id",
                                    "course_ids",
                                    "responsible_id",
                                    "final_result",
                                    "final_result_disp",
                                    "total_credits",
                                    "total_hours",
                                    "acquiered",
                                ],
                            }).then(function (result) {
                                self.courseGroupValues[localID] = result;
                                resolve(localID);
                            });
                        }
                    })
                    .catch(reject);
            });
        },
    });
    return DeliberationModel;
});
