odoo.define("website_booking.browser", function (require) {
    "use strict";

    /* global moment, Materialize, $, location, odoo, gapi, FullCalendar */

    var core = require("web.core");
    var ajax = require("web.ajax");
    var rpc = require("web.rpc");
    var Session = require("web.Session");
    var Widget = require("web.Widget");
    var time = require("web.time");

    var qweb = core.qweb;

    ajax.loadXML("/website_booking/static/src/xml/browser.xml", qweb);

    var CalendarWidget = Widget.extend({
        template: "website_booking.browser_calendar",

        get_fc_init_options: function () {
            return {
                timeZone: "local",
                themeSystem: "bootstrap5",
                header: {
                    left: "prev",
                    center: "title,today",
                    right: "next",
                },
                weekNumbers: true,
                eventLimit: true, // Allow "more" link when too many events
                locale: "fr",
                height: 755,
                initialView: "resourceTimeGridDay",
                slotMinTime: "08:00:00",
                slotMaxTime: "22:00:00",
                titleFormat: {
                    // Will produce something like "Tuesday, September 18, 2018"
                    month: "long",
                    day: "numeric",
                    weekday: "long",
                },
                /* Header : {
                 left:   'prev',
                 center: 'title,today',
                 right:  'next'
             },
            plugins: [ 'dayGrid', 'timeGrid', 'list', 'bootstrap', 'resourceTimeGrid' ],
            themeSystem : 'bootstrap',
    		allDaySlot : false,
    		locale: moment.locale,
    		timezone: "local",
    		editable: false,
    		height: 755,
    		locale: 'fr',
    		titleFormat: 'dddd D MMMM YYYY',
    		defaultDate: moment(),
    		defaultView: 'resourceTimeGridDay',
    		minTime: "08:00:00",
    		maxTime: "22:00:00",
    		navLinks: true, // can click day/week names to navigate views
    		eventLimit: true, // allow "more" link when too many events
    		refetchResourcesOnNavigate : false,*/
                resourceRender: function (resourceObj, labelTds, bodyTds) {
                    if (
                        resourceObj.booking_policy === "preserved" ||
                        resourceObj.booking_policy === "out"
                    ) {
                        labelTds.css("background", "#cccccc");
                    }
                },
            };
        },

        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);

            // This.calendar = new FullCalendar.Calendar(this.$el, this.get_fc_init_options());

            this.calendar = new FullCalendar.Calendar(
                this.el,
                this.get_fc_init_options()
            );

            this.calendar.render();

            return def;
        },

        refetch_events: function () {
            if (this.calendar) {
                this.calendar.refetchEvents();
            }
        },
    });

    var Schedule = CalendarWidget.extend({
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.date = parent.date;
            this.user = parent.user;
            this.asset_id = false;
        },

        get_fc_init_options: function () {
            var self = this;
            return $.extend(this._super(), {
                header: {
                    left: "",
                    center: "",
                    right: "",
                },
                defaultDate: this.date,
                height: 350,
                events: self.fetch_events.bind(this),
                allDaySlot: false,
                dayClick: self.day_click.bind(this),
            });
        },

        day_click: function (date, jsEvent, view) {
            this.trigger_up("click_scheduler", {
                date: date,
                jsEvent: jsEvent,
                view: view,
            });
        },

        fetch_events: function (fetchInfo, successCallback, failureCallback) {
            var self = this;
            var start = fetchInfo.start;
            var end = fetchInfo.end;
            // Ambuigus time moment are confusing for Odoo, needs UTC
            try {
                if (!start.hasTime()) {
                    start = moment(start).toDate();
                }
                if (!end.hasTime()) {
                    end = moment(end).toDate();
                }
            } catch (e) {}
            if (self.asset_id) {
                self.events = [];
                rpc.query({
                    route: "/booking/events",
                    params: {
                        asset_id: this.asset_id,
                        start: time.datetime_to_str(start.toDate()),
                        end: time.datetime_to_str(end.toDate()),
                    },
                }).then((events) => {
                    events.forEach(function (evt) {
                        self.events.push({
                            start: moment.utc(evt.start).toDate(),
                            end: moment.utc(evt.stop).toDate(),
                            title: /* evt.partner_id[1] + " - " +*/ evt.name,
                            allDay: evt.allday,
                            id: evt.id,
                            resourceId: evt.room_id[0],
                            resourceName: evt.room_id[1],
                            color: "#FA8FB1",
                            user_id: evt.user_id[0],
                        });
                    });
                    // Console.log([start, end, events])
                    successCallback(self.events);
                });
            }
        },

        set_asset_id: function (asset_id) {
            this.asset_id = asset_id;
            this.refetch_events();
        },
    });

    var DetailsDialog = Widget.extend({
        template: "website_booking.details_dialog",

        init: function (parent, options) {
            this.event = options.event;
            console.log(this.event);
        },
    });

    var NewBookingDialog = Widget.extend({
        template: "website_booking.new_booking_dialog",

        events: {
            "click .cancel-modal": function (event) {
                var self = this;
                self.parent.main_modal.modal("close");
            },
            "click .request-booking": function (event) {
                var self = this;
                var fromTime = self.$("#from_hour").timepicker("getTime");
                var toTime = self.$("#to_hour").timepicker("getTime");
                var start = moment(self.date)
                    .local()
                    .set("hour", fromTime.getHours())
                    .set("minutes", fromTime.getMinutes())
                    .set("seconds", 0);
                var stop = moment(self.date)
                    .local()
                    .set("hour", toTime.getHours())
                    .set("minutes", toTime.getMinutes())
                    .set("seconds", 0);
                var roomId = parseInt(self.$("select.select-asset-id").val());
                var event_type = "school_student_event_type";
                if (self.user.in_group_15) {
                    event_type = "school_teacher_event_type";
                }
                if (self.user.in_group_14) {
                    event_type = "school_management_event_type";
                }
                rpc.query({
                    model: "ir.model.data",
                    method: "get_object_reference",
                    args: ["school_booking", event_type],
                }).then((categ) => {
                    if (self.edit_mode) {
                        rpc.query({
                            model: "calendar.event",
                            method: "write",
                            args: [
                                [parseInt(self.event.id)],
                                {
                                    name: self.$("#description").val(),
                                    start: start.utc().format("YYYY-MM-DD HH:mm:ss"),
                                    stop: stop.utc().format("YYYY-MM-DD HH:mm:ss"),
                                    room_id: roomId,
                                    categ_ids: [[4, categ[1]]],
                                },
                            ],
                        })
                            .then((id) => {
                                self.trigger_up("updateEvent", {id: id});
                                self.parent.main_modal.modal("close");
                            })
                            .catch((error) => {
                                Materialize.toast(error.message.data.message, 4000);
                                self.parent.main_modal.modal("close");
                            });
                    } else {
                        rpc.query({
                            model: "calendar.event",
                            method: "create",
                            args: [
                                {
                                    name: self.$("#description").val(),
                                    start: start.utc().format("YYYY-MM-DD HH:mm:ss"),
                                    stop: stop.utc().format("YYYY-MM-DD HH:mm:ss"),
                                    room_id: roomId,
                                    categ_ids: [[4, categ[1]]],
                                },
                            ],
                        })
                            .then((id) => {
                                self.trigger_up("newEvent", {id: id});
                                self.parent.main_modal.modal("close");
                            })
                            .catch((error) => {
                                Materialize.toast(error.message.data.message, 4000);
                                self.parent.main_modal.modal("close");
                            });
                    }
                });
            },
            "click .delete-booking": function (event) {
                var self = this;
                rpc.query({
                    model: "calendar.event",
                    method: "unlink",
                    args: [parseInt(self.event.id)],
                }).then(function () {
                    self.trigger_up("deleteEvent", self.event.id);
                    self.parent.main_modal.modal("close");
                });
            },
            "change .select-asset-id": function (event) {
                this.schedule.set_asset_id(
                    parseInt(this.$("select.select-asset-id").val())
                );
                this.updateSendButton();
            },
            "change #from_hour": function (event) {
                var self = this;
                var fromTime = self.$("#from_hour").timepicker("getTime", this.date);
                var events = this.schedule.events;
                self.$("#from_hour").removeClass("invalid");
                self.$("#from_hour").addClass("valid");
                for (event in events) {
                    if (
                        moment(events[event].start).isBefore(fromTime) &&
                        moment(events[event].end).isAfter(fromTime)
                    ) {
                        self.$("#from_hour").removeClass("valid");
                        self.$("#from_hour").addClass("invalid");
                        break;
                    }
                }
                self.hasChanged = true;
                self.updateRoomList();
                self.updateSendButton();
            },
            "change #to_hour": function (event) {
                var self = this;
                var fromTime = self.$("#from_hour").timepicker("getTime", this.date);
                var toTime = self.$("#to_hour").timepicker("getTime", this.date);
                var events = this.schedule.events;
                self.$("#to_hour").removeClass("invalid");
                self.$("#to_hour").addClass("valid");
                for (event in events) {
                    if (
                        moment(events[event].start).isBefore(toTime) &&
                        moment(events[event].end).isAfter(toTime)
                    ) {
                        self.$("#to_hour").removeClass("valid");
                        self.$("#to_hour").addClass("invalid");
                        break;
                    }
                }
                if (!self.user.in_group_14 && !self.user.in_group_15) {
                    if (
                        fromTime.getHours() + fromTime.getMinutes() / 60 >
                        toTime.getHours() + toTime.getMinutes() / 60 - 0.5
                    ) {
                        self.$("#to_hour").removeClass("valid");
                        self.$("#to_hour").addClass("invalid");
                    }
                    if (
                        fromTime.getHours() + fromTime.getMinutes() / 60 <
                        toTime.getHours() + toTime.getMinutes() / 60 - 2
                    ) {
                        self.$("#to_hour").removeClass("valid");
                        self.$("#to_hour").addClass("invalid");
                    }
                } else {
                    self.$("#to_hour").removeClass("invalid");
                    self.$("#to_hour").addClass("valid");
                }
                self.hasChanged = true;
                self.updateRoomList();
                self.updateSendButton();
            },
        },

        custom_events: {
            click_scheduler: "click_scheduler",
        },

        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.user = parent.session.user;
            if (options && options.event) {
                this.ressources = parent.cal.ressources;
                this.date = options.event.start;
                this.event = options.event;
                this.edit_mode = true;
            } else {
                this.ressources = parent.cal.ressources;
                this.date = parent.cal.calendar.getDate();
                this.edit_mode = false;
            }
        },

        renderElement: function () {
            this._super.apply(this, arguments);
            var self = this;
            // Fill navigation panel
            self.schedule = new Schedule(this);
            self.schedule.appendTo(this.$(".schedule"));
        },

        start: function () {
            this._super.apply(this, arguments);
            var self = this;
            self.$("select.select-asset-id").material_select();
            self.$("#from_hour").timepicker({
                timeFormat: "H:i",
                minTime: "8:00",
                maxTime: "21:30",
                step: 60,
            });
            self.$("#from_hour").on("change", function () {
                var newTime = self.$("#from_hour").timepicker("getTime");
                self.$("#to_hour").timepicker("option", "minTime", newTime);
            });
            self.$("#to_hour").timepicker({
                timeFormat: "H:i",
                minTime: "8:30",
                maxTime: "22:00",
                showDuration: true,
                step: 60,
            });
            if (self.edit_mode) {
                self.$("#from_hour").val(moment(self.event.start).format("H:mm"));
                self.$("#from_hour").removeClass("invalid");
                self.$("#from_hour").addClass("valid");
                self.$("#to_hour").val(moment(self.event.end).format("H:mm"));
                self.$("#to_hour").removeClass("invalid");
                self.$("#to_hour").addClass("valid");
                self.$("#description").val(self.event.title);
                self.updateRoomList();
                self.$("select.select-asset-id").val(self.event.resourceId).change();
                self.$("select.select-asset-id").material_select();
                self.$(".delete-booking").show();
                self.hasChanged = false;
            } else {
                self.$("#description").val(self.parent.session.user.name);
            }
            Materialize.updateTextFields();
            self.hasChanged = false;
        },

        click_scheduler: function (event) {
            var requested_date = event.data.date;
            session.user_context.tz;
            var id = time;
            this.$("#from_hour").timepicker("setTime", requested_date.format("HH:mm"));
            this.$("#to_hour").timepicker(
                "option",
                "minTime",
                requested_date.format("HH:mm")
            );
            requested_date.add(1, "hours");
            this.$("#to_hour").timepicker("setTime", requested_date.format("HH:mm"));
            var events = this.schedule.events;
            for (event in events) {
                if (
                    moment(events[event].start).stripZone().isBefore(requested_date) &&
                    moment(events[event].end).stripZone().isAfter(requested_date)
                ) {
                    requested_date.add(-0.5, "hours");
                    this.$("#to_hour").timepicker(
                        "setTime",
                        requested_date.format("HH:mm")
                    );
                    break;
                }
            }
            this.$("#from_hour").removeClass("invalid");
            this.$("#to_hour").removeClass("invalid");
            this.$("#from_hour").addClass("valid");
            this.$("#to_hour").addClass("valid");
            this.updateRoomList();
        },

        updateRoomList: function () {
            var self = this;
            var fromTime = self.$("#from_hour").timepicker("getTime");
            var toTime = self.$("#to_hour").timepicker("getTime");
            if (fromTime && toTime) {
                var start = moment(self.date)
                    .local()
                    .set("hour", fromTime.getHours())
                    .set("minutes", fromTime.getMinutes())
                    .set("seconds", 0);
                var stop = moment(self.date)
                    .local()
                    .set("hour", toTime.getHours())
                    .set("minutes", toTime.getMinutes())
                    .set("seconds", 0);
                rpc.query({
                    route: "/booking/rooms",
                    params: {
                        start: start.format("YYYY-MM-DD HH:mm:ss"),
                        end: stop.format("YYYY-MM-DD HH:mm:ss"),
                        self_id: self.event ? parseInt(self.event.id) : "",
                    },
                }).then((rooms) => {
                    var roomSelect = self.$("select.select-asset-id").empty().html(" ");
                    for (var room_idx in rooms) {
                        var room = rooms[room_idx];
                        // Add new value
                        roomSelect.append(
                            $("<option></option>")
                                .attr("value", room.id)
                                .text(room.name)
                        );
                    }
                    roomSelect.removeAttr("disabled");
                    roomSelect.material_select();
                    Materialize.updateTextFields();
                    self.updateSendButton();
                });
            }
        },

        updateSendButton: function () {
            if (this.$(".invalid").length > 0) {
                this.$(".request-booking").attr("disabled", "");
            } else {
                this.$(".request-booking").removeAttr("disabled");
            }
        },
    });

    var NavigationCard = Widget.extend({
        template: "website_booking.browser_navigation_card",

        events: {
            "click .cat_button": function (event) {
                event.preventDefault();
                var self = this;
                self.parent.$(".navbar-card.active").removeClass("active");
                self.$(event.currentTarget).addClass("active");
                var category_id = self.$(event.currentTarget).data("category-id");
                if (self.to_parent) {
                    self.trigger_up("up_category", {category: self.category});
                } else {
                    self.trigger_up("click_category", {category: self.category});
                }
            },
        },

        init: function (parent, category, to_parent, is_active) {
            this._super(parent);
            this.category = category;
            this.parent = parent;
            this.to_parent = to_parent;
            this.is_active = is_active;
        },

        set_active: function () {
            this.$("a").addClass("active");
        },
    });

    var Navigation = Widget.extend({
        template: "website_booking.browser_navigation",

        custom_events: {
            click_category: "click_category",
            up_category: "up_category",
        },

        init: function (parent) {
            this._super.apply(this, arguments);
            this.state = parent._current_state;
        },

        renderElement: function () {
            this._super.apply(this, arguments);
            var self = this;
            if (self.state.category_id && self.state.category_id > 0) {
                rpc.query({
                    route: "/booking/category",
                    params: {
                        id: self.state.category_id,
                    },
                }).then((category) => {
                    if (category[0].is_leaf) {
                        self.selected_category = category[0];
                        rpc.query({
                            route: "/booking/category",
                            params: {
                                id: self.selected_category.parent_id[0],
                            },
                        }).then((category) => {
                            self.display_category = category[0];
                            if (self.display_category.parent_id) {
                                rpc.query({
                                    route: "/booking/category",
                                    params: {
                                        id: self.display_category.parent_id[0],
                                    },
                                }).then((category) => {
                                    self.parent_category = category[0];
                                    self.renderCategories();
                                    self.trigger_up("switch_category", {
                                        category: self.selected_category,
                                    });
                                });
                            } else {
                                self.parent_category = self.create_root();
                                self.renderCategories();
                                self.trigger_up("switch_category", {
                                    category: self.selected_category,
                                });
                            }
                        });
                    } else {
                        self.selected_category = false;
                        self.display_category = category[0];
                        if (self.display_category.parent_id) {
                            rpc.query({
                                route: "/booking/category",
                                params: {
                                    id: self.display_category.parent_id[0],
                                },
                            }).then((category) => {
                                self.parent_category = category[0];
                                self.renderCategories();
                                self.trigger_up("switch_category", {
                                    category: self.selected_category,
                                });
                            });
                        } else {
                            self.parent_category = self.create_root();
                            self.renderCategories();
                            self.trigger_up("switch_category", {
                                category: self.selected_category,
                            });
                        }
                    }
                });
            } else {
                self.display_category = self.create_root();
                self.selected_category = false;
                self.parent_category = false;
                self.renderCategories();
            }
        },

        create_root: function () {
            return {
                id: 0,
                name: "Root",
                isRoot: true,
            };
        },

        renderCategories: function () {
            var self = this;
            if (this.display_category) {
                if (this.display_category.isRoot) {
                    rpc.query({
                        route: "/booking/categories",
                        params: {
                            root: 1,
                        },
                    }).then((categories) => {
                        self.$(".categories").empty();
                        categories.forEach(function (category) {
                            var card = new NavigationCard(
                                self,
                                category,
                                false,
                                category.id == self.selected_category.id
                            );
                            card.appendTo(self.$(".categories"));
                        });
                    });
                } else {
                    rpc.query({
                        route: "/booking/categories",
                        params: {
                            parent_id: this.display_category.id,
                        },
                    }).then((categories) => {
                        self.$(".categories").empty();
                        categories.forEach(function (category) {
                            var card = new NavigationCard(
                                self,
                                category,
                                false,
                                category.id == self.selected_category.id
                            );
                            card.appendTo(self.$(".categories"));
                        });
                        if (self.parent_category) {
                            var card = new NavigationCard(
                                self,
                                self.parent_category,
                                true
                            );
                            card.appendTo(self.$(".categories"));
                        }
                    });
                }
            }
        },

        click_category: function (event) {
            var cat = event.data.category;
            if (cat.is_leaf) {
                this.selected_category = cat;
                this.$(".active").removeClass("active");
                event.target.set_active();
                this.trigger_up("switch_resource", {resource: cat});
            } else {
                this.parent_category = this.display_category;
                this.display_category = cat;
                this.renderCategories();
                this.trigger_up("switch_category", {category: cat});
            }
        },

        up_category: function (event) {
            var self = this;
            if (self.parent_category.isRoot) {
                this.display_category = this.create_root();
                this.selected_category = false;
                this.parent_category = false;
                self.renderCategories();
            } else if (self.parent_category.parent_id) {
                rpc.query({
                    route: "/booking/category",
                    params: {
                        id: self.parent_category.parent_id[0],
                    },
                }).then((category) => {
                    self.display_category = self.parent_category;
                    self.parent_category = category;
                    self.selected_category = false;
                    self.renderCategories();
                });
            } else {
                self.display_category = self.parent_category;
                self.parent_category = this.create_root();
                self.selected_category = false;
                self.renderCategories();
            }
            self.trigger_up("switch_category", {category: self.display_category});
        },
    });

    var Calendar = CalendarWidget.extend({
        get_fc_init_options: function () {
            var self = this;
            return $.extend(this._super(), {
                events: self.fetch_events.bind(this),
                resources: self.fetch_resources.bind(this),
                /* ViewRender: function(view,element){
    		     self.trigger_up('switch_date', {'date' : self.calendar.getDate()});
    		},*/
                eventClick: function (calEvent, jsEvent, view) {
                    var now = moment();
                    var event = calEvent.event;
                    if (
                        self.parent.session.user.in_group_14 ||
                        self.parent.session.uid == event.user_id
                    ) {
                        if (moment(event.start) > now) {
                            var dialog = new NewBookingDialog(self.parent, {
                                event: event,
                            });
                            dialog.appendTo(self.parent.main_modal.empty());
                            self.parent.main_modal.modal("open");
                        } else {
                            Materialize.toast(
                                "You cannot edit booking in the past",
                                2000
                            );
                        }
                    } else {
                        var details_dialog = new DetailsDialog(self.parent, {
                            event: event,
                        });
                        details_dialog.appendTo(self.parent.details_modal.empty());
                        self.parent.details_modal.modal("open");
                    }
                },
                header: {
                    left: "prev",
                    center: "title,today",
                    right: "next",
                },
            });
        },

        init: function (parent, value) {
            this._super(parent);
            this.parent = parent;
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.init_state = self.parent._current_state;
                if (self.init_state.date) {
                    self.calendar.gotoDate(moment(self.init_state.date).toDate());
                } else {
                    self.calendar.gotoDate(moment().toDate());
                }
            });
        },

        fetch_resources: function (fetchInfo, successCallback, failureCallback) {
            var self = this;
            self.ressources = [];

            rpc.query({
                route: "/booking/assets",
                params: {
                    category_id: self.category_id,
                },
            }).then((assets) => {
                assets.forEach(function (asset) {
                    self.ressources.push({
                        id: asset.id,
                        title: asset.name,
                        booking_policy: asset.booking_policy,
                    });
                });
                successCallback(self.ressources);
                self.trigger_up("switch_ressources", {ressources: self.ressources});
            });
        },

        fetch_events: function (fetchInfo, successCallback, failureCallback) {
            var self = this;
            var start = moment(fetchInfo.start);
            var end = moment(fetchInfo.end);
            // Ambuigus time moment are confusing for Odoo, needs UTC
            try {
                if (!start.hasTime()) {
                    start = moment(start.format());
                }
                if (!end.hasTime()) {
                    end = moment(end.format());
                }
            } catch (e) {}
            rpc.query({
                route: "/booking/events",
                params: {
                    category_id: self.category_id,
                    start: time.datetime_to_str(start.toDate()),
                    end: time.datetime_to_str(end.toDate()),
                },
            }).then((events) => {
                self.events = [];
                events.forEach(function (evt) {
                    var color = "#ff4355";
                    if (evt.categ_ids.includes(9)) {
                        color = "#00bcd4";
                    } else if (evt.categ_ids.includes(7)) {
                        color = "#2962ff";
                    } else if (evt.categ_ids.includes(8)) {
                        color = "#e65100";
                    } else {
                        /* If (session.uid == evt.user_id[0]) {
        	    	                color = '#ffc107';
        	    	            }*/
                        color = "#ffc107";
                    }
                    self.events.push({
                        start: moment.utc(evt.start).toDate(),
                        end: moment.utc(evt.stop).toDate(),
                        title: /* evt.partner_id[1] + " - " +*/ evt.name,
                        allDay: evt.allday,
                        id: evt.id,
                        resourceId: evt.room_id[0],
                        resourceName: evt.room_id[1],
                        color: color,
                        user_id: evt.user_id[0],
                    });
                });
                // Console.log([start, end, events])
                successCallback(self.events);
            });
        },

        switch_category: function (category) {
            this.category_id = category.id;
            this.calendar.refetchResources();
        },

        switch_resource: function (resource) {
            this.category_id = resource.id;
            this.calendar.refetchResources();
            this.calendar.refetchEvents();
        },

        goto_date: function (d) {
            this.calendar.gotoDate(d);
        },
    });

    var Toolbar = Widget.extend({
        template: "website_booking.toolbar",

        events: {
            "click #login-button": function (event) {
                rpc.query({
                    route: "/booking/login_providers",
                    params: {
                        redirect: "/booking#category_id=16",
                    },
                }).then((providers) => {
                    if (providers.length > 0) {
                        var provider = providers[0];
                        window.location.replace(provider.auth_link);
                    }
                });
            },
            "click #help-booking-button": function (event) {
                window.open(
                    "http://www.crlg.be/2018/03/15/musique-horizon-booking",
                    "_blank",
                    ""
                );
            },
            "click #logout-booking-button": function (event) {
                var self = this;
                self.is_logged = false;
                self.uid = false;
                self.avatar_src = false;
                self.$el.html(
                    qweb.render("website_booking.toolbar_nolog", {widget: self})
                );
                rpc.query({
                    route: "/web/session/destroy",
                    params: {},
                }).then(function () {
                    window.open(
                        "http://accounts.google.com/logout",
                        "something",
                        "width=550,height=570"
                    );
                    location.reload();
                });
            },
        },

        init: function (parent) {
            this._super.apply(this, arguments);
            var self = this;
            self.parent = parent;
            var session = new Session(undefined, undefined, {use_cors: false});
            session.session_bind().then(function () {
                if (session.uid) {
                    self.is_logged = true;
                    self.uid = session.uid;
                    self.parent.session = session;
                    rpc.query({
                        model: "res.users",
                        method: "search_read",
                        args: [
                            [["id", "=", session.uid]],
                            ["id", "name", "in_group_14", "in_group_15", "in_group_16"],
                        ],
                        context: session.context,
                    }).then(function (user_ids) {
                        session.user = user_ids[0];
                        self.user = session.partner;
                    });
                    rpc.query({
                        model: "res.partner",
                        method: "search_read",
                        args: [[["id", "=", session.partner_id]], ["id", "name"]],
                        context: session.context,
                    }).then(function (partner_ids) {
                        session.partner = partner_ids[0];
                        self.partner = session.partner;
                    });
                    self.avatar_src = session.url("/web/image", {
                        model: "res.users",
                        field: "image_small",
                        id: session.uid,
                    });
                    self.$el.html(
                        qweb.render("website_booking.toolbar_log", {widget: self})
                    );
                    self.$el.openFAB();
                } else {
                    self.$el.html(
                        qweb.render("website_booking.toolbar_nolog", {widget: self})
                    );
                }
            });
        },
    });

    var Browser = Widget.extend({
        template: "website_booking.browser",

        events: {
            "click #add-booking-button": function (event) {
                var self = this;
                event.preventDefault();
                var dialog = new NewBookingDialog(this);
                dialog.appendTo(self.main_modal.empty());
                self.main_modal.modal("open");
            },

            "click #goto-date-button": function (event) {
                var self = this;
                this.cal.goto_date(moment(this.$("#datepicker").val()).toDate());
            },
        },

        custom_events: {
            switch_resource: "switch_resource",
            switch_category: "switch_category",
            switch_ressources: "switch_ressources",
            switch_date: "switch_date",
            newEvent: function (event) {
                this.cal.refetch_events();
            },
            deleteEvent: function (event) {
                this.cal.refetch_events();
            },
            updateEvent: function (event) {
                this.cal.refetch_events();
            },
        },

        init: function (parent) {
            this._super.apply(this, arguments);
            /* TODO : why this.$('#main-modal') does not work ? */
            this._current_state = $.deparam(window.location.hash.substring(1));
        },

        renderElement: function () {
            this._super.apply(this, arguments);
            // Manage modals
            this.main_modal = this.$("#main-modal-content").parent().modal();
            this.details_modal = this.$("#modal-details-content").parent().modal();
            // Fill toolbar
            this.tb = new Toolbar(this);
            this.tb.appendTo(this.$(".booking_toolbar"));
            // Fill navigation panel
            this.nav = new Navigation(this);
            this.nav.appendTo(this.$(".navbar"));
            // Fill calendar panel
            this.cal = new Calendar(this);
            this.cal.appendTo(this.$(".calendar"));
            this.cal.tb = this.tb;
            this.$(".collapsible").collapsible();
        },

        switch_category: function (event) {
            this.do_push_state({
                category_id: event.data.category.id,
            });
            this.cal.switch_category(event.data.category);
        },

        switch_resource: function (event) {
            this.do_push_state({
                category_id: event.data.resource.id,
            });
            this.cal.switch_resource(event.data.resource);
        },

        switch_ressources: function (event) {
            var self = this;
            if (event.data.ressources.length == 0) {
                self.$("#add-booking-button").addClass("hide");
                self.$(".calendar_header").removeClass("active");
                self.$(".collapsible").collapsible({accordion: true});
                self.$(".collapsible").collapsible({accordion: false});
            } else {
                self.$("#add-booking-button").removeClass("hide");
                self.$(".calendar_header").addClass("active");
                self.$(".collapsible").collapsible();
                self.cal.do_show();
            }
        },

        switch_date: function (event) {
            this.do_push_state({
                date: event.data.date.format("YYYY-MM-DD"),
            });
        },

        do_push_state: function (state) {
            state = $.extend(this._current_state, state);
            var url = "#" + $.param(state);
            this._current_state = $.deparam($.param(state), false); // Stringify all values
            $.bbq.pushState(url);
            this.trigger("state_pushed", state);
        },
    });

    core.action_registry.add("website_booking.browser", Browser);

    return Browser;
});
