//	Avoids the 'event.layerX and event.layerY' warnings in Chrome
//	http://stackoverflow.com/questions/7825448/webkit-issues-with-event-layerx-and-event-layery
(function(){
    // remove layerX and layerY
    var all = $.event.props,
        len = all.length,
        res = [];
    while (len--) {
      var el = all[len];
      if (el != 'layerX' && el != 'layerY') res.push(el);
    }
    $.event.props = res;
}());

// Boilerplate to add CSRF protection headers, taken from https://docs.djangoproject.com/en/1.3/ref/contrib/csrf/
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

function trim(stringToTrim) {
	return stringToTrim.replace(/^\s+|\s+$/g,"");
}
function ltrim(stringToTrim) {
	return stringToTrim.replace(/^\s+/,"");
}
function rtrim(stringToTrim) {
	return stringToTrim.replace(/\s+$/,"");
}

function newCodeObject($a){
	if($a){
		if(typeof _gaq !== 'undefined'){ _gaq.push(['_trackEvent', 'New Code Object', $a.data('wiki_type')]); }
		url = '/' + $a.data('wiki_type') + 's/new/choose_template/?ajax=1';
		if ( $a.data('sourcescraper') ) {
			url += "&sourcescraper=" + $a.data('sourcescraper');
		}

		$.get(url, function(data){
	        $.modal('<div id="template_popup">'+data+'</div>', {
	            overlayClose: true,
	            autoResize: true,
	            overlayCss: { cursor:"auto" },
				onOpen: function(dialog) {
					dialog.data.show();
					dialog.overlay.fadeIn(200);
					dialog.container.fadeIn(200);
				},
				onShow: function(dialog){
					$('#simplemodal-container').css('height', 'auto');
				},
				onClose: function(dialog) {
					dialog.container.fadeOut(200);
					dialog.overlay.fadeOut(200, function(){
						$.modal.close();
					});
				}
	        });
	    });


	} else {
		alert('no anchor element provided');
	}
}

function newUserMessage(url){

	if(url == undefined){
		alert('No message url specified');
	} else {
//    	if(typeof _gaq !== 'undefined'){ _gaq.push(['_trackEvent', 'Profile buttons', 'Send Message']); }
    	$.get(url, function(data){
	        $.modal('<div id="message_popup">'+data+'</div>', {
	            overlayClose: true,
	            autoResize: true,
	            overlayCss: { cursor:"auto" },
				onOpen: function(dialog) {
					dialog.data.show();
					dialog.overlay.fadeIn(200);
					dialog.container.fadeIn(200);
				},
				onShow: function(dialog){
					$('#simplemodal-container').css('height', 'auto');
					$('h1', dialog.data).append(' to ' + $('.profilebio h3').text());
					$('textarea', dialog.data).focus();
					$(':submit', dialog.data).bind('click', function(e){
						e.preventDefault();
					//	var action = location.href + '/message/';
						var action = $('form', dialog.data).attr('action');
						var data = $('form', dialog.data).serialize();
						$.ajax({
							type: 'POST',
							url: action,
							data: data,
							success: function(data){
								if(data.status == 'ok'){
									if(typeof _gaq !== 'undefined'){ _gaq.push(['_trackEvent', 'Profile buttons', 'Send Message (message sent!)']); }
									$('h1', dialog.data).after('<p class="success">Message sent!</p>');
									$('form', dialog.data).remove();
									var t = setTimeout(function(){
										$('#simplemodal-overlay').trigger('click');
									}, 1000);
								} else {
									$('p.last', dialog.data).before('<p class="error">' + data.error + '</p>');
								}
							},
							dataType: 'json'
						});
					});
				},
				onClose: function(dialog) {
					dialog.container.fadeOut(200);
					dialog.overlay.fadeOut(200, function(){
						$.modal.close();
					});
				}
	        });
	    });
	}
}

//	Creates a pretty orange Alert bar at the top of the window.
//	Uses the same HTML as web/templates/frontend/messages.html
//	htmlcontent (string) -> the textual content of the alert (can include html tags and entities)
//	level (string) -> either 'error' or 'info' (null is treated as error)
//	actions (array) -> array of buttons (each with a url/action, text and optional 'secondary' object)
//	duration (number/string) -> how long slide animation lasts (set to null for no animation)
function newAlert(htmlcontent, level, actions, duration, onclose){
	if(typeof(level) != 'string'){ level = 'error'; }
	$alert_outer = $('<div>').attr('id','alert_outer').addClass(level);
	$alert_inner = $('<div>').attr('id','alert_inner').html('<span class="message">' + htmlcontent + '</span>');
	if(typeof(actions) == 'object'){
		var $a = $('<a>').html(actions.text);
		if(typeof(actions.url) != 'undefined'){
			$a.attr('href', actions.url);
		}
		if(typeof(actions.secondary) != 'undefined'){
			$a.addClass('secondary');
		}
		if(typeof(actions.onclick) != 'undefined'){
			$a.bind('click', actions.onclick);
		}
		$alert_inner.append($a);
	}
	$('<a>').attr('id','alert_close').bind('click', function(){
		if(typeof(onclose) != 'undefined'){
			onclose();
		}
		$('#alert_outer').slideUp(250);
		$('#nav').animate({marginTop:0}, 250);
	}).appendTo($alert_inner);
	if(typeof(duration) == 'string' || typeof(duration) == 'number'){
		$('#nav').animate({'marginTop': $alert_outer.outerHeight()}, duration);
		$alert_outer.hide().insertBefore($('#nav'));
		$alert_outer.append($alert_inner).animate({
			height: "show",
			marginTop: "show",
		    marginBottom: "show",
		    paddingTop: "show",
		    paddingBottom: "show"
		}, {
			step: function(now, fx){
				$('#nav').css('margin-top', $(fx.elem).outerHeight());
			}, complete: function(){
				$('#nav').css('margin-top', $('#alert_outer').outerHeight());
			},
			duration: duration
		});
	} else {
		$alert_outer.append($alert_inner).insertBefore($('#nav'));
		$('#nav').css('margin-top', $alert_outer.outerHeight());
	}

}

$(function(){
    // If you ever find this comment and you're adding a new page
    // add a new regular expression here and make sure it selects
    // the right .supernav tab :-)
    var urls = {
        '/(about|events|contact)/' : 'about',
        '/status/' : 'admin',
        '/profiles/' : 'user',
        '/login/' : 'login',
        '.*' : 'code'
    }
    $.each(urls, function(index, value){
        var regexp = RegExp(index);
        if(document.URL.match(regexp)){
            $('.supernav li.' + value).addClass('active default');
            $('.subnav.' + value).show();
            return false;
        }
    });


    $loginbutton = $('<a>Log In</a>').bind('click', function(){
        $(this).parents('form').find(':submit').trigger('click');
    });
    $('li.login_submit :submit').hide().after($loginbutton).parents('form').find(':text, :password').bind('keyup', function(e){
        if((e.keyCode || e.which) == 13){
			$(this).parents('form').find(':submit').trigger('click');
		}
    });
    $('form.subnav.login li.username, form.subnav.login li.password').bind('click', function(){
        $(this).children('input').focus();
    });

    if($('#nav .search input.text').val() == 'Search code...'){
        $('#nav .search input.text').val('').before('<span class="placeholder">Search code...</span>');
    } else {
        $('#nav .search input.text').before('<span class="placeholder" style="display:none">Search code...</span>');
    }

    $('#nav .search input.text, #nav .login input.text').bind('focus', function(){
        $(this).parent().addClass('focussed');
        if($(this).val() === ''){
            $(this).prev().show().css('opacity', 0.5);
        }
    }).bind('blur', function(){
        $(this).parent().removeClass('focussed');
        if($(this).val() === ''){
            $(this).prev().show().css('opacity', 1);
        }
    }).bind('keyup', function(e){
        if($(this).val() === '') {
		    $(this).prev().show().css({opacity: 0.5});
		} else {
		    $(this).prev().hide();
		}
    });

    setTimeout(function(){
        // clever hack removes the yellow background on auto-filled inputs in Chrome
        if (navigator.userAgent.toLowerCase().indexOf("chrome") >= 0) {
            $('#nav .login input:-webkit-autofill').each(function(){
                var $o = $(this);
                var $n = $o.clone(true);
                $o.siblings('label').hide();
                $o.after($n).remove();
            });
        }

        if ($('#nav .login input.text').val() != '') {
            $('#nav .login label').hide();
        }
    }, 500);

    $('a.editor_view, div.network .view a, a.editor_scraper').click(function(e) {
		e.preventDefault();
		newCodeObject($(this));
    });

	$('a.submit_link').each(function(){
		id = $(this).siblings(':submit').attr('id');
		$(this).addClass(id + '_link')
	}).bind('click', function(e){
		e.preventDefault();
		$(this).siblings(':submit').trigger('click');
	}).siblings(':submit').hide();

	$('#fourohfoursearch').val($('body').attr('class').replace("scrapers ", "").replace("views ", "").replace(" fourohfour", ""));

	function clean_up_users_popover($popover){
		$popover.filter(':visible').fadeOut(400, function(){
			$('li.error', $popover).remove();
			$('a.add_user', $popover).show();
			$('.new_user', $popover).hide().find('input:text').val('');
		});
		$('html').unbind('click');
	}


	$('body.vaults .transfer_ownership input:text').autocomplete({
		minLength: 2,
		source: function( request, response ) {
			$.ajax({
				url: $('#id_api_base').val() + "scraper/usersearch",
				dataType: "jsonp",
				data: {
					format:"jsondict",
					maxrows:10,
					searchquery:request.term
				},
				success: function( data ) {
					response( $.map( data, function( item ) {
						return {
							label: item.profilename + ' (' + item.username + ')',
							value: item.username
						}
					}));
				}
			});
		},
		select: function( event, ui ) {
			// submit the name
			$(this).next('input').attr('disabled',false);
		}
	}).next().bind('click', function(){
		var url = $(this).parent().prev().attr('href') + $(this).prev().val() + '/';
		var button = $(this).val('Transferring\u2026');
		$.ajax({
			url: url,
			dataType: 'json',
			success: function(data) {
				if(data.status == 'ok'){
					window.location.reload();
				} else if(data.status == 'fail'){
					button.after('<em class="error">Error: ' + data.error + '</em>');
					button.val('Transfer!');
				}
			},
			error: function(data){
				button.after('<em class="error">Error: ' + data.error + '</em>');
				button.val('Transfer!');
			}
		});
	}).attr('disabled', true);

	if($('#alert_outer').length && (!$('#alert_close').length)){
		$('<a>').attr('id','alert_close').bind('click', function(){
			$('#alert_outer').slideUp(250);
			$('#nav').animate({marginTop:0}, 250);
		}).appendTo('#alert_inner');
		$('#nav').css('margin-top', $('#alert_outer').outerHeight());
	}

	$('#compose_user_message').bind('click', function(e){
		e.preventDefault();
		newUserMessage($(this).attr('href'));
	});

	if($('#compose_user_message').length && window.location.hash == '#message'){
		$('#compose_user_message').trigger('click');
	}

	$('#liberatesomedata').bind('click', function(e){
		e.preventDefault();
		var viewurl = $(this).attr('href');
		$.ajax({
			url: viewurl,
			dataType: 'jsonp',
			success: function(data){
				var div = $('<div id="liberate_popup">');
				div.append('<h1>Liberate some data!</h1>');
				div.append('<h2 class="vote">Vote for other people&rsquo;s suggestions&hellip;</h2>');
				div.append('<ul></ul>');

				function populate_list(data, viewurl){
					if(data.length){
						$('ul', div).empty();
						$.map(data, function(val, i){
							var li = $('<li>');
							li.append('<span class="place">#' + (i+1) + '</span>');
							li.append('<a href="' + val.url + '" class="url">' + val.url.replace(/https?:\/\//i, "") + '</strong>');
							li.append('<span class="why">' + val.why + '</span>');
							$('<span class="vote" title="Vote for this">Vote</span>').bind('click', function(){
								$(this).addClass('loading').unbind('click');
								$.ajax({
									url: viewurl + '?vote=' + encodeURIComponent(val.url),
									dataType: 'jsonp',
									success: function(data){
										populate_list(data, viewurl);
									}
								});
							}).appendTo(li);
							$('ul', div).append(li);
						});
					} else {
						$('ul', div).html('<li><span class="place">?</span> <span class="url">No suggestions yet</span> <span class="why">Why not suggest a dataset below?</span></li>');
					}
				}

				populate_list(data, viewurl);

				var form = $('<form>');

				$('<h2 class="suggest">&hellip;Or suggest something new</h2>').appendTo(form);
				$('<p class="url"><label for="url">At what URL can we find the data?</label><input type="text" id="url" /></p>').appendTo(form);
				$('<p class="why"><label for="why">Why do you want it liberated?</label><input type="text" id="why" /></p>').appendTo(form);
				$('<p class="submit"><input type="submit" value="Liberate this data!" /></p>').bind('click', function(e){
					e.preventDefault();
					$.ajax({
						url: viewurl + '?add=' + encodeURIComponent($('#url').val()) + '&why=' + encodeURIComponent($('#why').val()),
						dataType: 'jsonp',
						success: function(data){
							populate_list(data, viewurl);
							$('#why, #url').val('');
							$('h2.suggest').nextAll('p').animate({"height": "hide", "marginTop": "hide", "marginBottom": "hide", "paddingTop": "hide", "paddingBottom": "hide"},{
							duration: 250,
							step: function(now, fx) {
							    $.modal.setPosition();
							}});
						}
					});
				}).appendTo(form);
				div.append(form);


				$.modal(div, {
		            overlayClose: true,
		            autoResize: true,
		            overlayCss: { cursor:"auto" },
					onOpen: function(dialog) {
						dialog.data.show();
						dialog.overlay.fadeIn(200);
						dialog.container.fadeIn(200);
					},
					onShow: function(dialog){
						$('#simplemodal-container').css('height', 'auto');
						$('h2.suggest', dialog.data).bind('click', function(){
							if($(this).next().is(':visible')){
								$(this).nextAll('p').animate({"height": "hide", "marginTop": "hide", "marginBottom": "hide", "paddingTop": "hide", "paddingBottom": "hide"},{
								duration: 250,
								step: function(now, fx) {
								    $.modal.setPosition();
								}});
							} else {
								$(this).nextAll('p').animate({"height": "show", "marginTop": "show", "marginBottom": "show", "paddingTop": "show", "paddingBottom": "show"},{
								duration: 250,
								step: function(now, fx) {
								    $.modal.setPosition();
								}});
							}
						});
					},
					onClose: function(dialog) {
						dialog.container.fadeOut(200);
						dialog.overlay.fadeOut(200, function(){
							$.modal.close();
						});
					}
		        });
			}
		});

	});


});
