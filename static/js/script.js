$(document).ready(function () {
  $('.sidenav').sidenav();
  $('select').formSelect();
  // $(window).resize(checkWidth);
  addIngList();
  removeIngrInput();
  check_image_checkbox();

  validateMaterializeSelect();

  function validateMaterializeSelect() {
    let classValid = {
      "border-bottom": "1px solid #4caf50",
      "box-shadow": "0 1px 0 0 #4caf50"
    };
    let classInvalid = {
      "border-bottom": "1px solid #f44336",
      "box-shadow": "0 1px 0 0 #f44336"
    };
    if ($("select.validate").prop("required")) {
      $("select.validate").css({
        "display": "block",
        "height": "0",
        "padding": "0",
        "width": "0",
        "position": "absolute"
      });
    }
    $(".select-wrapper input.select-dropdown").on("focusin", function() {
      $(this).parent(".select-wrapper").on("change", function () {
        if ($(this).children("ul").children("li.selected:not(.disabled)").on("click", function () {})) {
          $(this).children("input").css(classValid);
        }
      });
    }).on("click", function () {
      if ($(this).parent(".select-wrapper").children("ul").children("li.selected:not(.disabled)").css("background-color") === "rgba(0, 0, 0, 0.03)") {
        $(this).parent(".select-wrapper").children("input").css(classValid);
      } else {
        $(".select-wrapper input.select-dropdown").on("focusout", function() {
          if ($(this).parent(".select-wrapper").children("select").prop("required")) {
            if ($(this).css("border-bottom") != "1px solid rgb(76, 175, 80)") {
              $(this).parent(".select-wrapper").children("input").css(classInvalid);
            }
          }
        });
      }
    });
  }
});

// btn to add ingridient item to ingredients_list
function addIngList() {
  $('.add_list_item').click(function () {
    var ingredients_val = $('#ingredients').val();
    var ingrd_input_count = $(".ingr_input_cont").find("input");
    var input_html = '';
    input_html += '<div class="input-field s12">'
    input_html += '<input type="text" name="ingredients" class="validate ingr-items" value="' + ingredients_val + '" required>';
    input_html += '</div>'
    input_html += '<div class="input-field s12 right">'
    input_html += '<button id="remove_ingr_input" type="button" class="btn-floating move-btn-up right">X</button>';
    input_html += '</div>'
    if ($('#ingredients').val() != "" && ingrd_input_count.length <= 20) {
      $('.ingr_input_cont').append(input_html);
    } else if (ingrd_input_count.length > 20) {
      M.toast({
        html: 'You can add maximum of 20 ingredients'
      })
    } else {
      M.toast({
        html: 'Ingredient field is empty'
      })
    }
  })
}

// btn to remove last ingredient item from ingredients_list
function removeIngrInput() {
  $(document).on('click', '#remove_ingr_input', function () {
    $(this).parent().prev('div').remove();
    $(this).closest('div').remove();
  });
}

function check_image_checkbox() {
  $('#check_to_upload_image').on('click', function(){                  
     $('#image_upload_btn, #image_upload_input').attr('disabled', $(this).is(':checked'));       
});
}


// function count_list_item(){
//   $(".ingr-items").each(function(index) {
//     list_number = $(this).prepend(index + 1);
//  })
// }