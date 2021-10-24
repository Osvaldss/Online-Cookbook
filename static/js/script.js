$(document).ready(function(){
    $('.sidenav').sidenav();
    $('select').formSelect();
    checkWidth();
    $(window).resize(checkWidth);
    addIngList();
    removeIngListItem();
  });

// listen to window resize and changes position of recipe thumbnail  
function checkWidth() {
  var detImgCont = $(".image-container").detach();

  if($(window).width() < 600) { 
    detImgCont;
    $(".card-content.short-desc").prepend(detImgCont);
  } else {
    detImgCont;
    $(".rm-bottom-gap").append(detImgCont);
  }
};

// btn to add ingridient item to ingredients_list
function addIngList() {
  $('.add_list_item').click(function() {
    var ingrediantInput = $('#ingrediants').val();
      if (ingrediantInput != ""){
        var ingrediantItem = '<li>' + ingrediantInput + '</li>';
        var list_count = $('.ingr_list li').length;  
          if(list_count <= 20){
            $('.ingr_list').append(ingrediantItem);
          } else {
            $(".add_list_item").addClass("disabled")
          }          
      }
  })
}

// btn to remove last ingredient item from ingredients_list
function removeIngListItem() {
  $('.remove_list_item').click(function() {
    $('.ingr_list li:last-child').remove();
    var list_count = $('.ingr_list li').length;
    if(list_count <= 19){
      $(".add_list_item").removeClass("disabled")
    } else {
      $(".add_list_item").addClass("disabled")
    }  
  })
}

