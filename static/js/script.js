
function buyers(sel){
    var relationship_manager = sel.value;
    $('div#buyers').html("<img style='display:block;margin:auto;' src='https://loading.io/spinners/bars/index.progress-bar-facebook-loader.gif' />");
                  $.ajax({
                      url: '../../../../../ajax/relationship_manager_buyers',
                      type: "get",
                      data: {'relationship_manager':relationship_manager},
                      success: function(data) {
                       
                        $('div#buyers').html(data.relationship_manager_snippet);
                      },
                      error: function(err) {
                        console.log('error', err);
                      }
                    })
                 

}

$(document).ready(function(){
    $('.button-left').click(function(){
        $('.sidebar').toggleClass('flip');
    });

 });

 $(document).ready(function() {
    $('#example').DataTable();
} );

$(document).ready(function() {
   $('#salestable').DataTable();
} );

$(document).ready(function() {
   $('#purchasestable').DataTable();
} );


$(document).ready(function () {
    $('tbody.dealbuyer tr')
    .find('td')
    //.append('<input type="button" value="Delete" class="del"/>')
    .parent() //traversing to 'tr' Element
    .append('<td><a href="#" class="delrow">x</a></td>');

// For select all checkbox in table
$('#checkedAll').click(function (e) {
	//e.preventDefault();
    $(this).closest('#tblAddRow').find('td input:checkbox').prop('checked', this.checked);
});

// Add row the table
$('#btnAddRow').on('click', function() {
    var lastRow = $('#tblAddRow tbody tr:last').html();
    //alert(lastRow);
    $('#tblAddRow tbody').append('<tr>' + lastRow + '</tr>');
    $('#tblAddRow tbody tr:last input').val('');
});

// Delete last row in the table
$('#btnDelLastRow').on('click', function() {
    var lenRow = $('#tblAddRow tbody tr').length;
    //alert(lenRow);
    if (lenRow == 1 || lenRow <= 1) {
        alert("Can't remove all row!");
    } else {
        $('#tblAddRow tbody tr:last').remove();
    }
});

// Delete row on click in the table
$('#tblAddRow').on('click', 'tr a.delrow', function(e) {
    var lenRow = $('#tblAddRow tbody tr').length;
    e.preventDefault();
    if (lenRow == 1 || lenRow <= 1) {
        alert("Atleast One Product is Required");
    } else {
        $(this).parents('tr').remove();
    }
});

// Delete selected checkbox in the table
$('#btnDelCheckRow').click(function() {
	var lenRow		= $('#tblAddRow tbody tr').length;
    var lenChecked	= $("#tblAddRow input[type='checkbox']:checked").length;
    var row	= $("#tblAddRow tbody input[type='checkbox']:checked").parent().parent();
    //alert(lenRow + ' - ' + lenChecked);
    if (lenRow == 1 || lenRow <= 1 || lenChecked >= lenRow) {
        alert("Can't remove all row!");
    } else {
        row.remove();
    }
});
});




 $(document).on("click",".sales_history",function(){ 
    //alert(jQuery(this).data("id"));
    var item_id = ($(this).data('id'));
    //$.get("https://www.rawble.com/rfq/userrfq/ajaxestimatelist?item_id="+item_id, function(data, status){
    //alert(data);
    $('.sales-'+item_id).find('.modal-body').html("<img style='display:block;margin:auto;' src='https://loading.io/spinners/magnify/index.searching-for-loading-icon.gif' />");
    $.ajax({
        url: '../../../../../ajax/sales_history',
        type: "get",
        data: {'slug': item_id},

        success: function(data) {
          $('.sales-'+item_id).modal('show');
          $('.sales-'+item_id).find('.modal-body').html(data.product_snippet);
        },
        error: function(err) {
          console.log('error', err);
        }
      })
    //});
    });
  $(document).on("click",".purchase_history",function(){ 
        //alert(jQuery(this).data("id"));
        var item_id = ($(this).data('id'));
        //$.get("https://www.rawble.com/rfq/userrfq/ajaxestimatelist?item_id="+item_id, function(data, status){
        //alert(data);
        $('.purchase-'+item_id).find('.modal-body').html("<img style='display:block;margin:auto;' src='https://loading.io/spinners/magnify/index.searching-for-loading-icon.gif' />");
        $.ajax({
            url: '../../../../../ajax/purchase_history',
            type: "get",
            data: {'slug': item_id},
            success: function(data) {
              $('.purchase-'+item_id).modal('show');
              $('.purchase-'+item_id).find('.modal-body').html(data.product_snippet);
            },
            error: function(err) {
              console.log('error', err);
            }
          })
        //});
        });
    $(document).on("click",".recent_deals",function(){ 
        //alert(jQuery(this).data("id"));
        var item_id = ($(this).data('id'));
        //$.get("https://www.rawble.com/rfq/userrfq/ajaxestimatelist?item_id="+item_id, function(data, status){
        //alert(data);
        $('.recent-'+item_id).find('.modal-body').html("<img style='display:block;margin:auto;' src='https://loading.io/spinners/magnify/index.searching-for-loading-icon.gif' />");
        $.ajax({
            url: '../../../../../ajax/recent_deals',
            type: "get",
            data: {'slug': item_id},
            success: function(data) {
              $('.recent-'+item_id).modal('show');
              $('.recent-'+item_id).find('.modal-body').html(data.product_snippet);
            },
            error: function(err) {
              console.log('error', err);
            }
          })
        //});
        });

        $(document).on("click",".graph",function(){ 
          //alert(jQuery(this).data("id"));
          var item_id = ($(this).data('id'));
          //$.get("https://www.rawble.com/rfq/userrfq/ajaxestimatelist?item_id="+item_id, function(data, status){
          //alert(data);
          $('.graph-'+item_id).find('.modal-body').html("<img style='display:block;margin:auto;' src='https://loading.io/spinners/wedges/index.rotate-pie-preloader-gif.gif' />");
          $.ajax({
              url: '../../../../../ajax/graph',
              type: "get",
              data: {'slug': item_id},
              success: function(data) {
                $('.graph-'+item_id).modal('show');
                $('.graph-'+item_id).find('.modal-body').html(data.product_snippet);
              },
              error: function(err) {
                console.log('error', err);
              }
            })
          //});
          });
          $(document).on("click",".coaview",function(){ 
            //alert(jQuery(this).data("id"));
            var item_id = ($(this).data('id'));
            //$.get("https://www.rawble.com/rfq/userrfq/ajaxestimatelist?item_id="+item_id, function(data, status){
            //alert(data);
            $('.coaview-'+item_id).find('.modal-body').html("<img style='display:block;margin:auto;' src='https://loading.io/spinners/ripple/index.ripple-radio-preloader.gif' />");
            $.ajax({
                url: '../../../../../ajax/coa_view',
                type: "get",
                data: {'slug': item_id},
                success: function(data) {
                  $('.coaview-'+item_id).modal('show');
                  $('.coaview-'+item_id).find('.modal-body').html(data.product_snippet);
                },
                error: function(err) {
                  console.log('error', err);
                }
              })
            //});z
            });
            $(document).on("click",".googlechartsapp",function(){ 
              //alert(jQuery(this).data("id"));
              var item_id = ($(this).data('id'));
              //$.get("https://www.rawble.com/rfq/userrfq/ajaxestimatelist?item_id="+item_id, function(data, status){
              //alert(data);
              $('.googlechartsapp-'+item_id).find('.modal-body').html("<img style='display:block;margin:auto;' src='https://loading.io/spinners/blocks/index.rotating-squares-preloader-gif.gif' />");
              $.ajax({
                  url: '../../../../../ajax/googlechartsapp',
                  type: "get",
                  data: {'slug': item_id},
                  success: function(data) {
                    $('.googlechartsapp-'+item_id).modal('show');
                    $('.googlechartsapp-'+item_id).find('.modal-body').html(data.product_snippet);
                  },
                  error: function(err) {
                    console.log('error', err);
                  }
                })
              //});
              });
              
              $(document).on("click",".single-vendor-dealform",function(){ 
                //alert(jQuery(this).data("id"));
                //var item_id = ($(this).data('id'));
                //$.get("https://www.rawble.com/rfq/userrfq/ajaxestimatelist?item_id="+item_id, function(data, status){
                //alert(data);
                $('.single-vendor').find('.modal-body').html("<img style='display:block;margin:auto;' src='https://loading.io/spinners/flickr/index.orbit-balls-loading-gif.gif' />");
                $.ajax({
                    url: '../../../../../ajax/single-vendor-dealform',
                    type: "get",
                    data: {},
                    success: function(data) {
                      $('.single-vendor').modal('show');
                      $('.single-vendor').find('.modal-body').html(data.form_snippet);
                    },
                    error: function(err) {
                      console.log('error', err);
                    }
                  })
                //});
                });
                
                $(document).on("click",".js-vendor-deal-edit",function(){ 
                  var deal_id = ($(this).data('id'));
                  //alert(jQuery(this).data("id"));
                  //var item_id = ($(this).data('id'));
                  //$.get("https://www.rawble.com/rfq/userrfq/ajaxestimatelist?item_id="+item_id, function(data, status){
                  //alert(data);
                  $('.edit-'+deal_id).find('.modal-body').html("<img style='display:block;margin:auto;' src='https://loading.io/spinners/flickr/index.orbit-balls-loading-gif.gif' />");
                  $.ajax({
                      url: '../../../../../ajax/vendor-deal/edit',
                      type: "get",
                      data: {'slug':deal_id},
                      success: function(data) {
                        $('.edit-'+deal_id).modal('show');
                        $('.edit-'+deal_id).find('.modal-body').html(data.form_snippet);
                      },
                      error: function(err) {
                        console.log('error', err);
                      }
                    })
                  //});
                  });
                
                $(document).on("click",".js-vendor-deal-view",function(){ 
                  //alert(jQuery(this).data("id"));
                  var deal_id = ($(this).data('id'));
                  //$.get("https://www.rawble.com/rfq/userrfq/ajaxestimatelist?item_id="+item_id, function(data, status){
                  //alert(data);
                  $('.view'+deal_id).find('.modal-body').html("<img style='display:block;margin:auto;' src='https://loading.io/spinners/flickr/index.orbit-balls-loading-gif.gif' />");
                  $.ajax({
                      url: '../../../../../ajax/vendor-deal/view',
                      type: "get",
                      data: {'slug':deal_id},
                      success: function(data) {
                        $('.view-'+deal_id).modal('show');
                        $('.view-'+deal_id).find('.modal-body').html(data.deal_snippet);
                      },
                      error: function(err) {
                        console.log('error', err);
                      }
                    })
                  //});
                  });
                  $(document).on("click",".js-vendor-deal-delete",function(){ 
                    //alert(jQuery(this).data("id"));
                    var deal_id = ($(this).data('id'));
                    
                    //$.get("https://www.rawble.com/rfq/userrfq/ajaxestimatelist?item_id="+item_id, function(data, status){
                    //alert(data);
                    $('.delete-'+deal_id).find('.modal-body').html("<img style='display:block;margin:auto;' src='https://loading.io/spinners/flickr/index.orbit-balls-loading-gif.gif' />");
                    $.ajax({
                        url: '../../../../../ajax/vendor-deal/delete',
                        type: "get",
                        data: {'slug':deal_id},
                        success: function(data) {
                          $('.delete-'+deal_id).modal('show');
                          $('.delete-'+deal_id).find('.modal-body').html(data.deal_snippet);
                        },
                        error: function(err) {
                          console.log('error', err);
                        }
                      })
                    //});
                    });
              
                $(".modal-single-vendor").on("submit", ".js-single-vendor-form", function () {
                  alert("dlasldlals");
                  var form = $(this);
                  $.ajax({
                    url:form.attr("action"),
                    data: form.serialize(),
                    type: "post",
                    dataType: 'json',
                    success: function (data) {
                      if (data.form_is_valid) {
                        alert("Book created!");  // <-- This is just a placeholder for now for testing
                      }
                      else {
                        $("#modal-book .modal-content").html(data.html_form);
                      }
                    }
                  });
                });
        $(document).ready(function(){
          $('.js-example-basic-single-search').select2();
        });
        $(document).ready(function () {

            $(".js-upload-photos").click(function () {
              $("#fileupload").click();

            });
          
            $("#fileupload").fileupload({
              dataType: 'json',
              sequentialUploads: true, 
               /* 1. SEND THE FILES ONE BY ONE */
              start: function (e) {  /* 2. WHEN THE UPLOADING PROCESS STARTS, SHOW THE MODAL */
                $("#modal-progress").modal("show");
              },
              stop: function (e) {  /* 3. WHEN THE UPLOADING PROCESS FINALIZE, HIDE THE MODAL */
                $("#modal-progress").modal("hide");
              },
              progressall: function (e, data) {  /* 4. UPDATE THE PROGRESS BAR */
                var progress = parseInt(data.loaded / data.total * 100, 10);
                var strProgress = progress + "%";
                $(".progress-bar").css({"width": strProgress});
                $(".progress-bar").text(strProgress);
              },
              done: function (e, data) {
                
                if (data.result.is_valid) {
                  $("#gallery tbody").prepend(
                    "<tr><td ><a class='btn btn-outline-primary btn-block' href='" + data.result.url + "'>" + data.result.name + "</a></td><td>"+data.result.uploaded_at+"</td><td>"+data.result.uploaded_by+"</td></tr>"
                  )
                }
              }
              
            
          
            });
          
          });
          $(document).ready(function(){
              $('select.product').change(function(){
                var make = $(this.options[this.selectedIndex]).attr('data-make');
                console.log(make);
              });

              
        });
          
       $(document).ready(function(){
     $(window).scroll(function () {
            if ($(this).scrollTop() > 50) {
                $('#back-to-top').fadeIn();
            } else {
                $('#back-to-top').fadeOut();
            }
        });
        // scroll body to 0px on click
        $('#back-to-top').click(function () {
            $('#back-to-top').tooltip('hide');
            $('body,html').animate({
                scrollTop: 0
            }, 800);
            return false;
        });
        
        $('#back-to-top').tooltip('show');

});

$(function() {


  // This function gets cookie with a given name
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
  var csrftoken = getCookie('csrftoken');

  /*
  The functions below will create a header with csrftoken
  */

  function csrfSafeMethod(method) {
      // these HTTP methods do not require CSRF protection
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }
  function sameOrigin(url) {
      // test that a given url is a same-origin URL
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

  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
              // Send the token to same-origin, relative URLs only.
              // Send the token only if the method warrants CSRF protection
              // Using the CSRFToken value acquired earlier
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });

});