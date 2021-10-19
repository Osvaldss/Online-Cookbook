$(document).ready(function(){
    $('.sidenav').sidenav();
    checkWidth();
    $(window).resize(checkWidth);
  });

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