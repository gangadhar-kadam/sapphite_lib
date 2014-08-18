cur_frm.cscript.generate_message = function(doc, dt ,dn){
	wn.call({
		method:"core.doctype.notification_setting.credit_days_notification.check_period",
		callback:function(r){
			console.log("done")
		}
	})
}

cur_frm.cscript.interval = function(doc, dt ,dn){
	wn.call({
		method:"core.doctype.notification_setting.notification_setting.interval",
		args:{interval:doc.interval},
		callback:function(r){
			console.log(r)
			refresh_field('execution_time')
		}
	})
}
