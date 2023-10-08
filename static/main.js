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
  var data = {
      telegram: $("#id_username").val(),
      password: $("#id_password").val()
  };
  var url = '/auth/ajax-login/';
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

$(document).on("click", "#profile_update_btn", function(e) {
    const name = $("#name").val();
    const surname = $("#surname").val();
    const email = $("#email").val();
    const url = "/api/users/profile/update/";
    var token = "{{ csrf_token }}"
    const data = {
        first_name: name,
        last_name: surname,
        email: email,
    };
    let msg = "Профиль обновлен";
    $.ajax({
        url: url,
        method: "post",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(data),
        headers : {
            'CSRFToken' : "{{ csrf_token }}"
        },
        success: (data) => {
            $(".updprof-error").css("color", "green").text(msg);
            /*
            $("#notificationMainBackground").css({ "background-color": "green" }).fadeIn();
            $("#notificationMainMessage").text(msg);
            $("#notificationMainClose").css({ "color": "white" });
            $("#notificationMainMessage").css({ "color": "white" });
            setTimeout(function() {
                $("#notificationMainBackground").fadeOut();
            }, 6000);
             */
        },
        error: (data) => {
            var key;
            for (var k in data.responseJSON) {
                key = data.responseJSON[k];
                break;
            }
            $(".updprof-error").css("color", "red").text(key);
                // "Ошибка во время обновления профиля, попробуйте снова");
            /*
            $("#notificationMainBackground").css({ "background-color": "red" }).fadeIn();
            $("#notificationMainMessage").text(data.responseJSON[key]);
            $("#notificationMainClose").css({ "color": "white" });
            $("#notificationMainMessage").css({ "color": "white" });
            setTimeout(function() {
                $("#notificationMainBackground").fadeOut();
            }, 6000);
             */
        }
    });
})
// change_password() {
//     const old_password = document.getElementById("password_old") ? document.getElementById("password_old").value : null;
//     const new_password = document.getElementById("password_new").value;
//     const password_new_confirm = document.getElementById("password_new_confirm").value;
//     if (old_password) {
//         var data = {
//             old_password: old_password,
//             new_password: new_password
//         };
//     } else {
//         var data = {
//             new_password: new_password
//         };
//     }
//     ;
//     $("#passwordOldError").text(null);
//     $("#passwordNewError").text(null);
//     $("#passwordNewConfirmError").text(null);
//     $(".updprof-error").fadeOut();
//     if (password_new_confirm !== new_password) {
//         $("#passwordNewConfirmError").text("Пароли не совпадают");
//         return;
//     }
//     const url = $("#profile").data("user-change-password");
//     $.ajax({
//         url: url,
//         method: "put",
//         contentType: "application/json; charset=utf-8",
//         data: JSON.stringify(data),
//         success: (data) => {
//             $(".updprof-error").css("display", "block");
//             $("#password_old").val(null);
//             $("#password_new").val(null);
//             $("#password_new_confirm").val(null);
//         },
//         error: (data) => {
//             $("#passwordOldError").text(data.responseJSON.old_password);
//             $("#passwordOldError").text(data.responseJSON.non_field_errors);
//             $("#passwordNewError").text(data.responseJSON.new_password);
//         }
//     });
// }