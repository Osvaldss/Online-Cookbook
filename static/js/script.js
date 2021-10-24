$(document).ready(function(){
    $('.sidenav').sidenav();
    $('select').formSelect();
    // $(window).resize(checkWidth);
    addIngList();
    removeIngrInput();
  });

// listen to window resize and changes position of recipe thumbnail  
// function checkWidth() {
//   var detImgCont = $(".image-container").detach();

//   if($(window).width() < 600) { 
//     detImgCont;
//     $(".short-desc").prepend(detImgCont);
//   } else {
//     detImgCont;
//     $(".rm-bottom-gap").append(detImgCont);
//   }
// };

// btn to add ingridient item to ingredients_list
function addIngList() {
  $('.add_list_item').click(function() {
    var ingredients_val = $('#ingredients').val();
    var ingrd_input_count = $(".ingr_input_cont").find("input");
    var input_html = '';
    input_html += '<div class="input-field s12">'
    input_html += '<input type="text" name="ingredients" class="validate ingr-items" value="'+ingredients_val+'" required>';
    input_html += '</div>'
    input_html += '<div class="input-field s12 right">'
    input_html += '<button id="remove_ingr_input" type="button" class="btn-floating move-btn-up right">X</button>';
    input_html += '</div>'
    if($('#ingredients').val() != "" && ingrd_input_count.length <= 20 ){
      $('.ingr_input_cont').append(input_html);
    } else if (ingrd_input_count.length > 20){
      M.toast({html: 'You can add maximum of 20 ingredients'})
    } else {
      M.toast({html: 'Ingredient field is empty'})
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

// function count_list_item(){
//   $(".ingr-items").each(function(index) {
//     list_number = $(this).prepend(index + 1);
//  })
// }