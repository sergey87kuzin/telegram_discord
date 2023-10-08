$(document).on("click", "#telegram-nick-confirm", function (e) {
  e.preventDefault();
  var telegram = $("#telegram-nickname").val();
  var data = {
    telegram: telegram
  };
  var url = '/api/users/telegram/confirm/';
  $.ajax({
    url: url,
    method: "post",
    contentType: "application/json",
    data: JSON.stringify(data),
    success: function success(data) {
      $(".code-confirm-form").slideDown(200);
      $("#code-confirm").prop("required", true).focus();
      $("#register-submit-button").prop('disabled', false);
      $("#telegram-error").fadeOut(200).text();
      $(".error-telegram").text('');
      var dif = Math.round((new Date(data.resend_available).getTime() - new Date().getTime()) / 1000);
      getLoyaltyTimer(dif);
    },
    error: function error(_error2) {
      console.error(_error2);
      $("#telegram-error").fadeIn(200).text(_error2.responseJSON.confirmation_code[0]);
    }
  });
});

$(document).on('click', '#login-modal-button', function (e) {
  e.preventDefault();
  var data = {telegram: $("#telegram").val()};
  var url = '/api/users/telegram/confirm/';
  $.ajax({
    url: url,
    data: data,
    method: "post",
    success: function success(data) {
      if (!!data.error) {
        var tpl = data.tpl;
        $(".modal-login__extended").html(tpl);
      } else {
        window.location.href = data.url;
      }
    },
    error: function error(data) {
      alert("Error on authorization");
    }
  });
});

$(".menu-btn-open").on("click", function() {
    $(".burger").addClass("active");
    $("body").addClass("no-scroll");
    if ($(window).width() >= 992) {
        $(".modal-overlay").addClass("active");
    } else {
        $(this).parent().addClass("close");
        $(".header").addClass("burger-open");
        setTimeout(() => {
            $(".header__icons-search").addClass("header__icons-search_show");
        }, 50)
    }
});

$(document).on("click", ".menu-btn-close, .modal-overlay.active", function() {
    $(".burger, .modal-overlay").removeClass("active");
    $("body").removeClass("no-scroll");
    if ($(window).width() < 992) {
        $(this).parent().removeClass("close");
        $(".header__icons-search").removeClass("header__icons-search_show");
        if ($(".header").hasClass("burger-open")) {
            $(".header").removeClass("burger-open")
        }
    }
    $(".burger__submenu").fadeOut(200);
});

$(".auth_open").click(function (e) {
  $(".modal-login").addClass("active");

  if (!$('.modal-overlay').hasClass('active') && $(window).innerWidth() > 991) {
    $('.modal-overlay').addClass('active');
  }
});
$(document).on("click", ".modal-login__close, .modal-overlay.active, .modal-login.active", function (e) {
  if ($(".modal-login__content").has(e.target).length === 0) {
    $(".modal-login").removeClass("active");
    $('.modal-login__title-box, .modal-login__link-box, .modal-login__group').show();
    $('.modal-login__title_recover, .modal-login__col_recover, .modal-login__col, .modal-login__title, .modal-login__link, .modal-overlay').removeClass('active');
    $('.modal-login__col[data-tab="login"], .modal-login__title[data-tab="login"], .modal-login__link[href="sign"]').addClass('active');
  }
});
$('.modal-login__tab-link').click(function (e) {
  e.preventDefault();

  if (!$('.modal-overlay').hasClass('active') && $(window).innerWidth() > 991) {
    $('.modal-overlay').addClass('active');
  }

  if (!$("body").hasClass("no-scroll")) {
    $("body").addClass("no-scroll");
  }

  var id = $(this).attr('href'),
      content = $('.modal-login__col[data-tab="' + id + '"]'),
      title = $('.modal-login__title[data-tab="' + id + '"]'),
      thisLink = $('.modal-login__link[href="' + id + '"]');
  $('.modal-login__col').removeClass('active');
  $('.modal-login__title').removeClass('active');
  content.addClass('active');
  title.addClass('active');
  $('.modal-login__tab-link').addClass('active');

  if (thisLink.hasClass('active')) {
    thisLink.removeClass('active');
  }
});
$('.modal-login__link-recover').click(function (e) {
  e.preventDefault();
  $('.modal-login__title_recover, .modal-login__col_recover').addClass('active');
  $('.modal-login__title-box, .modal-login__link-box, .modal-login__group').hide();
});