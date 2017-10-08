

function ControlText(name, properties){
	ControlBase.call(this, name, properties);
};
ControlText.prototype = Object.create(ControlBase.prototype);


////////////////////////////////////////////////////////////////////////////////

ControlText.prototype.init_control = function(){
	var html = "<div id='"+this.place_id()+"' class='field ControlText' >"
	if(this.properties.include_label) html += "<label>"+this.properties.label+"</label>";
	html += "<input placeholder='"+this.properties.label+"' type='text' name='"+this.name+"' id='"+this.control_id()+"' value='' />";
	html += "</div>";
	this.jquery_place().replaceWith(html);

	this.set_value(this.properties.value);

	var self = this;
	this.jquery().change(function(){
		self.basewidget.fire_event( this.name, 'changed_event' );
	});

	
	if(!this.properties.enabled){
		this.jquery().attr('disabled', '');
	}else{
		this.jquery().removeAttr('disabled');
	};
	
	if(this.properties.error) this.jquery_place().addClass('error'); else this.jquery_place().removeClass('error'); 

	if(!this.properties.visible) this.hide(undefined, true);
};

////////////////////////////////////////////////////////////////////////////////
