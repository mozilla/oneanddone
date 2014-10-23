(function() {
    var site = {
        platform: 'windows'
    };

    if(navigator.platform.indexOf("Win32") != -1 ||
       navigator.platform.indexOf("Win64") != -1) {
        site.platform = 'windows';
    }
    else if (navigator.platform.indexOf("armv7l") != -1) {
        site.platform = 'android';
    }
    else if(navigator.platform.indexOf("Linux") != -1) {
        site.platform = 'linux';
    }
    else if (navigator.userAgent.indexOf("Mac OS X") != -1) {
        site.platform = 'osx';
    }
    else if (navigator.userAgent.indexOf("MSIE 5.2") != -1) {
        site.platform = 'osx';
    }
    else if (navigator.platform.indexOf("Mac") != -1) {
        site.platform = 'mac';
    }
    else {
        site.platform = 'other';
    }

    function init() {
        // Add the platform as a classname on the html-element immediately to
        // avoid lots of flickering.
        var h = document.documentElement;
        h.className = h.className.replace("windows", site.platform);

        // Add class to reflect javascript availability for CSS
        h.className = h.className.replace(/\bno-js\b/,'js');
    }

    init();
    window.site = site;
})();

// To support datepicker fields with jQuery-ui datepicker
$(function() {
  $(".datepicker").datepicker(
    {
      dateFormat: 'yy-mm-dd',
      buttonImage: '/static/img/calendar.gif',
      showOn: 'both'
    });
});

// To support modal messages
$(function() {
  $(".modal-message").dialog({
    modal: true,
    buttons: {
      Ok: function() {
        $( this ).dialog( "close" );
      }
    }
  });
});

// To show and hide activity detail
$(function() {
  $(document).on('click', '.activity-listing th.toggle', function () {
    $(this).toggleClass('opened');
    if ($(this).hasClass('opened')) {
      $('.activity-item td.toggle').addClass('opened');
      $('.activity-listing .activty-detail').show();
    } else {
      $('.activity-item td.toggle').removeClass('opened');
      $('.activity-listing .activty-detail').hide();
    }
    return false;
  });

  $(document).on('click', '.activity-item td.toggle', function () {
    $(this).toggleClass('opened');
    $(this).parent().next('tr').toggle();
    return false;
  });
});

// For dynamic formset of invalidation criteria in tasks.import
$(function () {
  var totalFormsField = $("#id_criterion-TOTAL_FORMS");

  $("#add_criterion").click(function () {
    var numForms = totalFormsField.val();
    if (parseInt(numForms) >= 10){
      $("#criterion_error_message").show();
      $("#criterion_error_message").fadeOut(3000);
      return;
    }
    var newForm = $("#empty_criterion_form").html().replace(/__prefix__/g, numForms);
    $("#criterion_formset_table tr:last").after(newForm);
    totalFormsField.val(parseInt(numForms) + 1);
    $("#del_criterion-" + numForms).click(delCriterion);
  });

  $("span[id|='del_criterion']").click(delCriterion);

  function delCriterion(event) {
    var currentRow = $("#" + event.target.id).parents("tr.extra-criterion");
    var rowsBelow = currentRow.nextAll();
    currentRow.remove();
    var numForms = parseInt(totalFormsField.val()) - 1;
    totalFormsField.val(numForms);
    var lastIndex = numForms - rowsBelow.length;
    rowsBelow.each(function (index, element) {
        var newIndex = lastIndex + index;
        updateIndexes($(this).find("[id]"), "id", newIndex);
        updateIndexes($(this).find("[name]"), "name", newIndex);
    });
  }

  function updateIndexes(elements, attribute, index) {
    elements.each(function () {
        var newValue = $(this).attr(attribute).replace(/criterion-\d+/, "criterion-"   + index);
        $(this).attr(attribute, newValue);
    });
  }
});

// To support datatables for metrics
$(function() {
  $('.dataTable.metrics-listing').DataTable(
    {
      bSortCellsTop: true,
      info: false,
      order: [ 2, 'desc' ],
      orderClasses: true,
      paging: false,
      scrollY: 400
    }
  );
});
