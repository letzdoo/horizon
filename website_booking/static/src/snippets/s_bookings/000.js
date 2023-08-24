/** @odoo-module **/

import publicWidget from 'web.public.widget';
import { datetime_to_str } from 'web.time';

const CalendarWidget = publicWidget.Widget.extend({
        
    get_fc_init_options: function() {
        return {
            timeZone: 'local',
            themeSystem: 'bootstrap5',
            header: {
                left:   'prev',
                center: 'title,today',
                right:  'next'
            },
            weekNumbers: true,
            eventLimit: true, // allow "more" link when too many events
            locale: 'fr',
            height: 855,
            initialView: 'resourceTimeGridDay',
            slotMinTime: "08:00:00",
    		slotMaxTime: "22:00:00",
    		titleFormat: { // will produce something like "Tuesday, September 18, 2018"
                month: 'long',
                day: 'numeric',
                weekday: 'long'
            },
            /*header : {
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
    		resourceRender: function(resourceObj, labelTds, bodyTds) {
    		    if(resourceObj.booking_policy === 'preserved' || resourceObj.booking_policy === 'out') {
    		        labelTds.css('background', '#cccccc');    
    		    }
            },
        }
    },
    
    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);
        
        //this.calendar = new FullCalendar.Calendar(this.$el, this.get_fc_init_options());
    
        this.calendar = new FullCalendar.Calendar(this.el, this.get_fc_init_options());
    
        this.calendar.render();

        return def;
    },
    
    refetch_events: function() {
        if(this.calendar) {
            this.calendar.refetchEvents();
        }
    },

});

var NavigationCard = publicWidget.Widget.extend({
    template: 'website_booking.browser_navigation_card',
    
    events: {
        "click .cat_button": function (event) {
            event.preventDefault();
            var self = this;
            self.parent.$('.navbar-card.active').removeClass('active');
            self.$(event.currentTarget).addClass('active');
            var category_id = self.$(event.currentTarget).data('category-id');
            if(self.to_parent) {
                self.trigger_up('up_category', {'category' : self.category});
            } else {
                self.trigger_up('click_category', {'category' : self.category});
            }
        },
    },
    
    init: function(parent, category, to_parent, is_active) {
        this._super(parent);
        this.category = category;
        this.parent = parent;
        this.to_parent = to_parent;
        this.is_active = is_active;
    },
    
    set_active: function() {
        this.$('a').addClass('active');  
    },
});

const Navigation = publicWidget.Widget.extend({
    template: 'website_booking.browser_navigation',

    custom_events: {
        'click_category' : 'click_category',
        'up_category' : 'up_category',
    },
    
    init: function(parent) {
        this._super.apply(this, arguments);
        this.state = parent._current_state;
    },
    
    start: function() {
        this._super.apply(this, arguments);
        var self = this;
        if(self.state.category_id && self.state.category_id > 0) {
            this._rpc({
                route: "/booking/category",
                params: {
                    'id' : self.state.category_id
                },
            }).then(category => {
                if(category[0].is_leaf) {
                    self.selected_category = category[0];
                    this._rpc({
                        route: "/booking/category",
                        params: {
                            'id' : self.selected_category.parent_id[0]
                        },
                    }).then(category => {
                        self.display_category = category[0];
                        if(self.display_category.parent_id) {
                            this._rpc({
                                route: "/booking/category",
                                params: {
                                    'id' : self.display_category.parent_id[0]
                                },
                            }).then(category => {
                                self.parent_category = category[0];
                                self.renderCategories();
                                self.trigger_up('switch_category', {'category' : self.selected_category});
                            });
                        } else {
                            self.parent_category = self.create_root();
                            self.renderCategories();
                            self.trigger_up('switch_category', {'category' : self.selected_category});
                        }
                    });
                } else {
                    self.selected_category = false;
                    self.display_category = category[0];
                    if(self.display_category.parent_id) {
                        this._rpc({
                            route: "/booking/category",
                            params: {
                                'id' : self.display_category.parent_id[0]
                            },
                        }).then(category => {
                            self.parent_category = category[0];
                            self.renderCategories();
                            self.trigger_up('switch_category', {'category' : self.selected_category});
                        });
                    } else {
                        self.parent_category = self.create_root();
                        self.renderCategories();
                        self.trigger_up('switch_category', {'category' : self.selected_category});
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
    
    create_root : function(){
        return {
            'id' : 0,
            'name' : 'Root',
            'isRoot' : true,
        }
    },
    
    renderCategories: function() {
        var self = this;
        if(this.display_category) {
            if(this.display_category.isRoot) {
                this._rpc({
                    route: "/booking/categories",
                    params: {
                        'root' : 1
                    },
                }).then(categories => {
                    self.$(".categories").empty();
                    categories.forEach(function(category) {
                        var card = new NavigationCard(self, category, false, category.id == self.selected_category.id);
                        card.appendTo(self.$(".categories"));
                    });
                });
            } else {
                this._rpc({
                    route: "/booking/categories",
                    params: {
                        'parent_id' : this.display_category.id
                    },
                }).then(categories => {
                    self.$(".categories").empty();
                    categories.forEach(function(category) {
                        var card = new NavigationCard(self, category, false, category.id == self.selected_category.id);
                        card.appendTo(self.$(".categories"));
                    });
                    if(self.parent_category) {
                        var card = new NavigationCard(self, self.parent_category, true);
                        card.appendTo(self.$(".categories"));
                    }
                });
            }
        }
    },

    click_category : function(event) {
        var cat = event.data.category;
        if(cat.is_leaf) {
            this.selected_category = cat;
            this.$('.active').removeClass('active');
            event.target.set_active();
            this.trigger_up('switch_resource', {'resource' : cat});
        } else {
            this.parent_category = this.display_category;
            this.display_category = cat;
            this.renderCategories();
            this.trigger_up('switch_category', {'category' : cat});
        }
    },
    
    up_category : function(event) {
        var self = this;
        if(self.parent_category.isRoot) {
            this.display_category = this.create_root();
            this.selected_category = false;
            this.parent_category = false;
            self.renderCategories();
        } else {
            if (self.parent_category.parent_id) {
                this._rpc({
                    route: "/booking/category",
                    params: {
                        'id' : self.parent_category.parent_id[0]
                    },
                }).then(category => {
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
        }
        self.trigger_up('switch_category', {'category' : self.display_category});
    },
    
});

const Calendar = CalendarWidget.extend({
    template : 'website_booking.browser_calendar',

    get_fc_init_options: function() {
        var self = this;
        return $.extend(this._super(),{
            events: self.fetch_events.bind(this),
    		resources: self.fetch_resources.bind(this),
    		/*viewRender: function(view,element){
    		     self.trigger_up('switch_date', {'date' : self.calendar.getDate()});
    		},
    		eventClick: function(calEvent, jsEvent, view) {
    		    var now = moment();
    		    var event = calEvent.event;
    		    if(self.parent.session.user.in_group_14 || self.parent.session.uid == event.user_id) {
    		        if (moment(event.start) > now) {
            		    var dialog = new NewBookingDialog(self.parent, {'event' : event});
                        dialog.appendTo(self.parent.main_modal.empty());
                        self.parent.main_modal.modal('open');
    		        } else {
    		            Materialize.toast('You cannot edit booking in the past', 2000);
    		        }
    		    } else {
    		        var details_dialog = new DetailsDialog(self.parent, {'event' : event});
    		        details_dialog.appendTo(self.parent.details_modal.empty());
    		        self.parent.details_modal.modal('open');
    		    }
            },*/
            header : {
                left:   'prev',
                center: 'title,today',
                right:  'next'
            },
        });
    },
    
    init: function (parent, value) {
        this._super(parent);
        this.parent = parent;
    },
    
    start: function() {
        var self = this;
        return this._super.apply(this, arguments).then(function() {
            self.init_state = self.parent._current_state;
            if(self.init_state.date) {
                self.calendar.gotoDate(moment(self.init_state.date).toDate());
            } else {
                self.calendar.gotoDate(moment().toDate());
            }
        });
    },
           
    fetch_resources: function(fetchInfo, successCallback, failureCallback) {
        var self = this;
        self.ressources = [];
        
        this._rpc({
            route: "/booking/assets",
            params: {
                'category_id':self.category_id
            },
        }).then(assets => {
                assets.forEach(function(asset) {
                    self.ressources.push({
                        'id' : asset.id,
                        'title' : asset.name,
                        'booking_policy' : asset.booking_policy,
                    });
                });
                successCallback(self.ressources);
                self.trigger_up('switch_ressources', {'ressources' : self.ressources});
            }
        );
    },
    
    fetch_events: function(fetchInfo, successCallback, failureCallback) {
        var self = this;
        var start = moment(fetchInfo.start);
        var end = moment(fetchInfo.end);
		// Ambuigus time moment are confusing for Odoo, needs UTC
        try {
            if(!start.hasTime()) {
                start = moment(start.format())        
            }
            if(!end.hasTime()) {
                end = moment(end.format())        
            }
        } catch(e) {}
        this._rpc({
            route: "/booking/events",
            params: {
    		    'category_id':self.category_id,
				'start' : datetime_to_str(start.toDate()),
				'end' : datetime_to_str(end.toDate()),
	    	},
        }).then(events => {
                self.events = [];
	    	    events.forEach(function(evt) {
                    var color = '#ff4355';
    	    	    if (evt.categ_ids.includes(9)) {
    	    	        color = '#00bcd4';
    	    	    } else {
    	    	        if(evt.categ_ids.includes(7)) {
    	    	            color = '#2962ff';
    	    	        } else {
    	    	            if(evt.categ_ids.includes(8)) {
        	    	            color = '#e65100';
        	    	        } else {
        	    	            /*if (session.uid == evt.user_id[0]) {
        	    	                color = '#ffc107';
        	    	            }*/
        	    	            color = '#ffc107';
        	    	        }
    	    	        }
    	    	    } 
                    self.events.push({
                        'start': moment.utc(evt.start).toDate(),
                        'end': moment.utc(evt.stop).toDate(),
                        'title': /*evt.partner_id[1] + " - " +*/ evt.name,
                        'allDay': evt.allday,
                        'id': evt.id,
                        'resourceId':evt.room_id[0],
                        'resourceName':evt.room_id[1],
                        'color': color,
                        'user_id' : evt.user_id[0],
                    });
                });
                //console.log([start, end, events])
                successCallback(self.events);
            }
        );
    },
    
    switch_category : function(category) {
        this.category_id = category.id;
        this.calendar.refetchResources();
    },
    
    switch_resource : function(resource) {
        this.category_id = resource.id;
        this.calendar.refetchResources();
        this.calendar.refetchEvents();
    },
    
    goto_date : function(d) {
        if(d){
            this.calendar.gotoDate(d);
        }
    },
    
});

publicWidget.registry.snippetBookings = publicWidget.Widget.extend({
    selector: 'section.s_bookings',
    disabledInEditableMode: false,

    events: {
        "click #add-booking-button": function (event) {
            var self = this;
            event.preventDefault();
            var dialog = new NewBookingDialog(this);
            dialog.appendTo(self.main_modal.empty());
            self.main_modal.modal('open');
        },
        
        "click #goto-date-button": function (event) {
            var self = this;
            this.cal.goto_date(moment(this.$('#datepicker').val()).toDate());
        },
        
    },
    
    custom_events: {
        'switch_resource' : 'switch_resource',
        'switch_category' : 'switch_category',
        'switch_ressources' : 'switch_ressources',
        'switch_date' : 'switch_date',
        'newEvent': function(event) {
            this.cal.refetch_events();
        },
        'deleteEvent': function(event) {
            this.cal.refetch_events();
        },
        'updateEvent': function(event) {
            this.cal.refetch_events();
        },
    },

    init: function(parent) {
        this._super.apply(this, arguments);
        /* TODO : why this.$('#main-modal') does not work ? */
        this._current_state = $.deparam(window.location.hash.substring(1));
        if(!this._current_state.category_id) {
            this._current_state.category_id = 16;
        }
    },
    
    start: function() {
        this._super.apply(this, arguments);
        // Fill navigation panel
        this.nav = new Navigation(this);
        this.nav.appendTo(this.$(".s_bookings_navbar"));
        // Fill calendar panel
        this.cal = new Calendar(this);
        this.cal.appendTo(this.$(".s_bookings_calendar"));
        this.cal.tb = this.tb;
        //this.$('.collapsible').collapsible();
        this.$("#datepicker").val(moment().format('YYYY-MM-DD'));
    },
    
    switch_category: function(event) {
        this.do_push_state({
            'category_id' : event.data.category.id,
        });
        this.cal.switch_category(event.data.category);
    },
    
    switch_resource: function(event) {
        this.do_push_state({
            'category_id' : event.data.resource.id,
        });
        this.cal.switch_resource(event.data.resource);
    },
    
    switch_ressources: function(event) {
        var self = this;
        if(event.data.ressources.length == 0) {
            self.$('#add-booking-button').addClass('hide');
            self.$('.calendar_header').removeClass('active');
            //self.$(".collapsible").collapsible({accordion: true});
            //self.$(".collapsible").collapsible({accordion: false});
        } else {
            self.$('#add-booking-button').removeClass('hide');
            self.$('.calendar_header').addClass('active');
            //self.$(".collapsible").collapsible();
            self.cal.do_show()
        }
    },
    
    switch_date: function(event) {
        this.do_push_state({
            'date' : event.data.date.format("YYYY-MM-DD"),
        });   
    },
    
    do_push_state: function(state) {
        state = $.extend(this._current_state, state);
        var url = '#' + $.param(state);
        this._current_state = $.deparam($.param(state), false); // stringify all values
        $.bbq.pushState(url);
        this.trigger('state_pushed', state);
    },
});

export default {
    snippetBookings : publicWidget.registry.snippetBookings,
};