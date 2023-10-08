"use strict";

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArrayLimit(arr, i) { if (typeof Symbol === "undefined" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

(function () {
  setTimeout(function () {
    var vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', "".concat(vh, "px"));
    document.documentElement.style.setProperty('--vh_h', "".concat(vh, "px"));
    window.addEventListener('resize', function () {
      var vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', "".concat(vh, "px"));
    });
  }, 0);
})();

$(document).on('keyup change', '.custom_input', function (e) {
  this.setAttribute('data-val', this.value);
});
$("#nl_promo").on("change", function () {
  $("#change_subscription").submit();
});
$("#human_date").on("change", function () {
  var hVal = $(this).val();
  var tDate = new Date(hVal).getTime() / 1000;
  $("#dob").val(tDate);
});
$(document).ready(function () {
  var header = $(".header");
  var scrollPrev = 0;
  var height = header.outerHeight();
  $(window).scroll(function () {
    var scrolled = $(window).scrollTop();

    if ($(window).width() < 992) {
      if (scrolled > height && scrolled > scrollPrev) {
        header.addClass('slideDown');
      } else {
        header.removeClass('slideDown');
      }

      scrollPrev = scrolled;
    }

    if (scrolled > 0) {
      if ($(window).width() >= 992) {
        header.addClass("fixed");
      } else {
        $('.header_light').addClass('dark');
      }

      if ($("body").hasClass("show-topBar")) {
        $("body").removeClass("show-topBar");
      }
    } else {
      header.removeClass("fixed");

      if ($("body").hasClass("has-topBar")) {
        $("body").addClass("show-topBar");
      }

      if ($(window).width() < 992) {
        $('.header_light').removeClass('dark');
      }
    }
  });
});
$(document).on("click", ".search__close-btn, .modal-overlay.active", function () {
  $(".search").removeClass("active");
  $(".modal-overlay").removeClass("active");

  if ($(window).width() >= 992) {
    $("body").removeClass("no-scroll");
  }

  $(".search__form")[0].reset();
});
$('.custom_input_select').click(function () {
  $(".custom_options_select").slideToggle(150);
});
$('.custom_input_select').blur(function () {
  $(".custom_options_select").hide(150);
});
$(".custom_option input").on("change", function () {
  var val = $(".custom_option input:checked").val();
  var id = $(".custom_option input:checked").attr("id");
  $("#size-input").val(val).attr("data-id", id);
  $("#size-input").val(val);
  $(".custom_label_select").addClass("top");
  $(".custom_options_select").hide(150);
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
$(document).on("click", ".close-form, .close-ajax-cart, .modal-overlay.active", function (e) {
  e.preventDefault();
  $(".wrapper-ajax-cart, .modal-overlay").removeClass("active");
  $("html").css("overflow-y", "");
  $("body").css("overflow-y", "");
});
$(".profile__change-password").click(function () {
  $(".modal-overlay").addClass("active");
  $(".change-password").addClass("active");
  $("body").addClass("no-scroll");
});
$(document).on("click", ".change-password__close, .modal-overlay.active, .change-password.active", function (e) {
  if (!$(".change-password__content").is(e.target) && $(".change-password__content").has(e.target).length === 0) {
    $(".change-password").removeClass("active");
    $(".modal-overlay").removeClass("active");
    $("body").removeClass("no-scroll");
  }
});
$(".lexicon-open").click(function () {
  $(".lexicon-modal").slideToggle(200);
  $(".burger__scroll").stop().animate({
    scrollTop: 0
  }, 400);

  if ($(".lexicon-modal").css("display") === "block") {
    $(".lexicon-close").show();

    if ($(window).width() < 992) {
      setTimeout(function () {
        var height = $(".lexicon-modal").outerHeight();
        var top = $(".burger__menu_last").css("marginTop");
        top = Number(top.substr(0, top.length - 2));

        if (top > height) {
          $(".burger__menu_last").css("marginTop", top - height + 'px');
        } else {
          $(".burger__menu_last").css("marginTop", 0);
        }
      }, 200);
    }
  }

  setTimeout(function () {
    if ($(".lexicon-modal").css("display") !== "block" && $(window).width() < 992) {
      $(".lexicon-close").hide();
      $(".burger__menu_last").attr('style', '');
    }
  }, 230);
});
$(".lexicon-close").click(function () {
  $(".lexicon-modal").slideUp(200);
  $(".lexicon-close").hide();

  if ($(window).width() < 992) {
    setTimeout(function () {
      $(".burger__menu_last").attr('style', '');
    }, 200);
  }
});

$(document).on("click", ".modal-welcome__close, .modal-overlay.active, .modal-welcome.active", function (e) {
  if ($(".modal-welcome__box").has(e.target).length === 0) {
    closeModalWelcom();
  }
});
$("#go_to_registration").on("click", function () {
  closeModalWelcom();
});
$(".menu-btn-open").on("click", function () {
  $(".burger").addClass("active");
  $("body").addClass("no-scroll");

  if ($(window).width() >= 992) {
    $(".modal-overlay").addClass("active");
  } else {
    $(this).parent().addClass("close");
    $(".header").addClass("burger-open");
    setTimeout(function () {
      $(".header__icons-search").addClass("header__icons-search_show");
    }, 50);
  }
});
$(document).on("click", ".menu-btn-close, .modal-overlay.active", function () {
  $(".burger, .modal-overlay").removeClass("active");
  $("body").removeClass("no-scroll");

  if ($(window).width() < 992) {
    $(this).parent().removeClass("close");
    $(".header__icons-search").removeClass("header__icons-search_show");

    if ($(".header").hasClass("burger-open")) {
      $(".header").removeClass("burger-open");
    }
  }

  $(".burger__submenu").fadeOut(200);
});
$(".radio-custom").on("click", function () {
  $(this).toggleClass("active").siblings("var-delivery_item ").toggleClass("active");
});
$(".order-row_item").on("click", function () {
  if (!$(this).hasClass("active")) {
    $(this).addClass("active").siblings().removeClass("active");
  }
});
$(".photo-row_item").on("click", function () {
  if (!$(this).hasClass("active")) {
    $(this).addClass("active").siblings().removeClass("active");
  }
});
$(".instastore-row_item").on("click", function () {
  $(".wrapper-card").addClass("active");
});
$(".wrapper-card").on("click", function () {
  $(this).removeClass("active");
});
$(".slideshow_pic").on("click", function (e) {
  e.preventDefault();
  var $this = $(this),
      item = $this.closest(".tovar-preview"),
      container = $this.closest(".row"),
      display = container.find(".slideshow_display"),
      path = item.find("img").attr("src"),
      link = item.find("a").attr("href"),
      duration = 300;

  if (!item.hasClass(".active")) {
    item.addClass("active").siblings().removeClass("active");
    display.find("img").fadeOut(duration, function () {
      $(this).attr("src", path).fadeIn(duration);
    });
    display.find("a").fadeOut(duration, function () {
      $(this).attr("href", link).fadeIn(duration);
    });
  }
});

function initializeItiPhone(inputPhone, errorSelector) {
  var input = document.querySelector(inputPhone);
  var errorMsg = document.querySelector(errorSelector);
  var errorMap = ["Неверный номер", "Неверный код страны", "Слишком короткий", "Слишком длинный", "Неверный номер"];
  var errorEnMap = ["Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];

  if (input) {
    var iti = window.intlTelInput(input, {
      utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
      nationalMode: false,
      formatOnDisplay: true,
      autoHideDialCode: false,
      initialCountry: "ru",
      preferredCountries: ["ru", "by", "kz", "az", "uz", "am", "ge", "kg"],
      geoIpLookup: function geoIpLookup(callback) {
        $.get("//ipinfo.io", function () {}, "jsonp").always(function (resp) {
          var countryCode = resp && resp.country ? resp.country : "";
          callback(countryCode);
        });
      }
    });

    var reset = function reset() {
      input.classList.remove("error");
      errorMsg.innerHTML = "";
      errorMsg.classList.add("hide");
    };

    var handleChange = function handleChange() {
      $(inputPhone).data("phone-number", iti.getNumber());
      reset();
    };

    input.addEventListener('blur', function () {
      reset();

      if (input.value.trim()) {
        var re = /^[\d\+][\d\(\)\ -]{4,14}\d$/;
        var valid = re.test(input.value.trim());
        var errorCode = -1;

        if (valid && !iti.isValidNumber()) {
          errorCode = iti.getValidationError();
        }

        if (!valid || errorCode >= 0) {
          input.classList.add("error");
          var errorMsgText = window.location.href.includes("/en/") ? errorEnMap[errorCode] ? errorEnMap[errorCode] : "Enter a valid number" : errorMap[errorCode] ? errorMap[errorCode] : "Введите корректный номер";
          errorMsg.innerHTML = errorMsgText;
          errorMsg.classList.remove("hide");
        }
      }
    });
    input.addEventListener("change", handleChange);
    input.addEventListener("keyup", handleChange);
  }
}

$(document).on("click", ".n-product__present", function () {
  if ($("#present").css("display") === 'block') {
    setTimeout(function () {
      window.new_present.get_phone_input("#recipient_phone");
      window.new_present.initDadata();
    });
  }
});
$(document).ready(function () {
  setTimeout(function () {
    initializeItiPhone("#phone", "#phone-intl-error");
    initializeItiPhone("#loyalty-phone", "#loyalty-phone-intl-error");
  }, 2000);
});
$(document).on("click", "a.admission", function () {
  $("#size_subscribe input[name=size]").val("");
  $("#size_subscribe .regular").hide();
  $("#size_subscribe .admission").show();
});
$(document).on("click", "#size_subscribe .admission .size-item-wrapper", function () {
  var sz = $(this).find("input").val();
  $("#size_subscribe input[name=size]").val(sz);
});

$(document).ready(function () {
  if ($(".profile__promocodes") && localStorage.getItem('promocode')) {
    document.querySelectorAll(".promocodes__name").forEach(function (el) {
      if (el.innerText === localStorage.getItem('promocode')) {
        var btn = $(el).closest(".promocodes__item").find(".promocodes__btn");
        btn.addClass("us");
        setTimeout(function () {
          btn.next().fadeIn(250);
        }, 150);
      }
    });
  }

  $(".promocodes__btn").click(function () {
    var _this = this;

    var promo = $(this).closest(".promocodes__item").find(".promocodes__name").text();
    localStorage.setItem('promocode', promo);
    $(".promocodes__btn").removeClass("us");
    $(".promocodes__info").fadeOut(250);
    $(this).addClass("us");
    setTimeout(function () {
      $(_this).next().fadeIn(250);
    }, 150);
  });
}); // $(".custom_form-group_date input").on("focus keyup change", function() {
//     $(".label_datepicker").addClass("top");
// });
//
// $(".custom_form-group_date input").on("blur", function() {
//     if ($(this).val().length === 0) {
//         $(".label_datepicker").removeClass("top");
//     }
// });
//
// $(document).ready(function() {
//     if ($(".custom_form-group_date input").length && $(".custom_form-group_date input").val().length !== 0) {
//         $(".label_datepicker").addClass("top");
//     }
// });

$(document).on('click', '.avl-map-open', function () {
  var tab = $(this).data('tab');
  var content = $('.avl-map[data-tab="' + tab + '"]');
  $('.avl-map').removeClass('active');
  $('.avl-map-open').removeClass('active');
  content.addClass('active');
  $(this).addClass('active');

  if ($(window).width() < 992) {
    $('.avl-modal__map-box').addClass('active');
  }
});
$('.avl-modal__map-close').on('click', function () {
  $('.avl-modal__map-box').removeClass('active');
});
$(".btn-avl-open").click(function () {
  $(".avl-modal").fadeIn(200);
  $("body").addClass("no-scroll");

  if ($(window).width() >= 768) {
    $(".modal-overlay").addClass("active");
  }

  var url = $(".n-product__availability").data("fb-stock-url");
  $.ajax({
    url: url,
    method: "post",
    contentType: "application/json",
    data: JSON.stringify()
  });
});

function closeModalForOverlayAndBtn(overlay, btn, modal, e) {
  if (e.target.className === overlay || $(btn).has(e.target).length) {
    $(modal).fadeOut(200);
    $(".modal-overlay").removeClass("active");
    $("body").removeClass("no-scroll");
  }
}

$(document).on("click", ".avl-modal__container, .avl-modal__close", function (e) {
  closeModalForOverlayAndBtn("avl-modal__container", ".avl-modal__close", ".avl-modal", e);
});
$(document).on("click", ".hint-modal__container, .hint-modal__close", function (e) {
  closeModalForOverlayAndBtn("hint-modal__container", ".hint-modal__close", ".hint-modal", e);
});
$(document).on("click", ".present__container, .present__close", function (e) {
  closeModalForOverlayAndBtn("present__container", ".present__close", ".present", e);
});

if (document.querySelector('.n-product__preview-slider')) {
  var productSlider = new Swiper('.n-product__slider', {
    direction: "vertical",
    spaceBetween: 4,
    slidesPerView: 5,
    freeMode: true,
    watchSlidesVisibility: true,
    watchSlidesProgress: true
  });
  var productSliderPreview = new Swiper('.n-product__preview-slider', {
    speed: 400,
    loop: true,
    spaceBetween: 0,
    slidesPerView: 1,
    pagination: {
      el: '.n-product__pagination'
    },
    navigation: {
      nextEl: ".n-product__next",
      prevEl: ".n-product__prev"
    },
    thumbs: {
      swiper: productSlider
    }
  });
}

if (document.querySelector('.n-product__zoom-preview-slider') && document.documentElement.clientWidth < 992) {
  var productZoomSliderPreview = new Swiper('.n-product__zoom-preview-slider', {
    speed: 400,
    loop: true,
    spaceBetween: 0,
    slidesPerView: 1,
    pagination: {
      el: '.n-product__zoom-pagination'
    }
  });
} else if (document.querySelector('.n-product__zoom-preview-slider')) {
  $('.n-product__zoom-preview-slider').removeClass('swiper-container');
  $('.n-product__zoom-preview-col').removeClass('swiper-wrapper');
  $('.n-product__zoom-preview-slide').removeClass('swiper-slide');
}

$(".n-zoom-open").click(function () {
  var target = $('.scroll-anchor-target[data-scroll-target="' + $(this).data('zoom') + '"]');
  $('.n-product__zoom-media').each(function () {
    $(this).attr('src', $(this).data('src'));
    $(this).removeAttr('data-src');
  });
  $(".n-product__zoom-modal").addClass("active");
  $("body").addClass("no-scroll");
  $('.scroll-anchor-trigger[data-scroll-anchor="' + $(this).data('zoom') + '"]').addClass("active");
  $('.n-product__zoom-preview-slider').stop().animate({
    scrollTop: target.offset().top
  }, 0);
});

function closeZoomSlide() {
  $(".n-product__zoom-modal").removeClass("active");
  $("body").removeClass("no-scroll");
  setTimeout(function () {
    $('.n-product__zoom-media').each(function () {
      $(this).data('src', $(this).attr('src'));
      $(this).removeAttr('src');
    });
  }, 400);
}

$(".n-zoom-close").click(function () {
  closeZoomSlide();
});
$(".n-product__zoom-preview-slide").click(function () {
  if ($(window).width() >= 992) {
    closeZoomSlide();
  }
}); // скролл к карточке на странице товара

function initSmoothScroll() {
  var anchors = $('.scroll-anchor-trigger');
  if (!anchors.length) return;
  anchors.on('click', function () {
    anchors.removeClass('active');
    $(this).addClass('active');
  });

  for (var i = 0; i < anchors.length; i++) {
    var anchor = anchors[i];
    $(anchor).on('click', function () {
      var target = $('.scroll-anchor-target[data-scroll-target="' + $(this).data('scroll-anchor') + '"]');
      var new_position = target[0].offsetTop;
      $('.n-product__zoom-preview-slider').stop().animate({
        scrollTop: new_position
      }, 400);
    });
  }

  $('.n-product__zoom-preview-slider').scroll(function () {
    var anchorTargets = $('.scroll-anchor-target');

    for (var _i = 0; _i < anchorTargets.length; _i++) {
      var anchorTarget = anchorTargets[_i];
      var slidePosition = $(anchorTarget).offset().top - $(anchorTarget).height() * 0.3;
      var windowScrollPosition = $(window).scrollTop();
      var anchorActive = $('.scroll-anchor-trigger[data-scroll-anchor="' + $(anchorTarget).data('scroll-target') + '"]');

      if (slidePosition < windowScrollPosition) {
        $('.scroll-anchor-trigger').removeClass("active");
        anchorActive.addClass("active");
      }
    }
  });
}

initSmoothScroll(); //all colors на странице товара

$(".all-colors-open").on("click", function () {
  $(".all-colors").addClass("active");
  $("body").addClass("no-scroll");

  if ($(window).width() >= 768) {
    $(".modal-overlay").addClass("active");
  }
});
$(document).on("click", ".all-colors-close, .modal-overlay.active", function () {
  $(".all-colors").removeClass("active");
  $("body").removeClass("no-scroll");

  if ($(window).width() >= 768) {
    $(".modal-overlay").removeClass("active");
  }
}); // Collections

$(document).ready(function () {
  if ($('.collections').length && $(window).width() < 768) {
    $('.subscribe').addClass('border_none');
  }
});

function get_collection_products(vm) {
  $('.collection__products-row').addClass('loading');
  var url = vm.data('url');
  var col = vm.data('col');
  var row_id = vm.data('row');
  var class_obj = vm.data('class');
  var data = {
    col: col,
    row_id: row_id
  };
  $.ajax({
    url: url,
    data: data,
    method: 'post',
    success: function success(data) {
      // console.log(data.tpl);
      // console.log(vm.closest('.collection__row').find('.collection__products'));
      var container = vm.closest('.collection__row').find(".".concat(class_obj)).html(data.tpl);
    },
    error: function error(_error) {
      console.log('SOMETHING GOES WRONG');
    },
    complete: function complete(data) {
      $('body').removeClass('loading');
      $(".collection__products-row").removeClass('loading');
    }
  });
}

$(document).ready(function () {
  $('.collection__card').on('click', function () {
    if ($(this).find('.collection__btn').length) {
      var row = $(this).parents('.collection__row');
      var product = $(this).next('.collection__products');
      get_collection_products($(this));
      $(this).find('.collection__btn').toggleClass('open');
      product.slideToggle(180);

      if ($(window).width() >= 768) {
        if (row.find('.collection__btn').hasClass('open')) {
          row.find('.collection__btn').not($(this).find('.collection__btn')).removeClass('open');
          setTimeout(function () {
            row.find('.collection__products').not(product).slideUp(180);
          }, 80);
        }
      }
    }
  });
}); // subscribe

$('.subscribe__form input').focus(function () {
  $('.subscribe__submit').addClass('active');
  $('.subscribe__policy').addClass('active');
});
$('.subscribe__form input').blur(function () {
  $('.subscribe__submit').removeClass('active');
  $('.subscribe__policy').removeClass('active');
}); // animate emblem for product detail

function addLettersAnimation(el) {
  var indicator = el.children('.emblem-animate');
  setTimeout(function () {
    $(indicator).addClass('active');
  }, 0);
}

$(document).ready(function () {
  $('.emblem').mouseover(function () {
    addLettersAnimation($(this));
  });
  $(window).on('scroll', function () {
    if ($('.emblem') && $(window).width() < 992) {
      var blockPosition = $('.emblem').offset().top + $('.emblem').height();
      var windowScrollPosition = $(window).scrollTop() + $(window).height() - $('.n-product__fixed').height();

      if (blockPosition < windowScrollPosition) {
        addLettersAnimation($('.emblem'));
      }
    }
  });
});

var getLoyaltyTimer = function getLoyaltyTimer(resend_available) {
  $("#loyalty-timer").fadeIn(200);
  $("#loyalty-phone-confirm").attr('disabled', true);
  var seconds = $("#loyalty-timer-seconds");
  var secVal = parseInt(seconds.text());
  var timer = setTimeout(function tick() {
    if (secVal > 0) {
      seconds.text(--secVal);
      timer = setTimeout(tick, 1000);
    } else {
      $("#loyalty-timer").fadeOut(200);
      seconds.text(resend_available);
      $("#loyalty-phone-confirm").attr('disabled', false);
    }
  }, 1000);
};

$(document).on("click", "#loyalty-phone-confirm", function (e) {
  e.preventDefault();
  var phone = $("#loyalty-phone").val().replace(/[^+\d]/g, '');
  var data = {
    phone_number: phone
  };
  var url = '/api/users/loyalty/phone/confirm/';
  $.ajax({
    url: url,
    method: "post",
    contentType: "application/json",
    data: JSON.stringify(data),
    success: function success(data) {
      $(".code-confirm-form").slideDown(200);
      $("#code-confirm").prop("required", true).focus();
      $(".submit_loyalty_registration").prop('disabled', false);
      $("#loyalty-phone-error").fadeOut(200).text();
      $(".error-registration-phone").text('');
      var dif = Math.round((new Date(data.resend_available).getTime() - new Date().getTime()) / 1000);
      getLoyaltyTimer(dif);
    },
    error: function error(_error2) {
      console.error(_error2);
      $("#loyalty-phone-error").fadeIn(200).text(_error2.responseJSON.confirmation_code[0]);
    }
  });
});
$(document).on("submit", ".users-loyalty-register", function (e) {
  e.preventDefault();
  var formData = new FormData(this);
  var url = $(this).data("url");

  var data = _objectSpread(_objectSpread({}, Object.fromEntries(formData)), {}, {
    phone: $("#loyalty-phone").val().replace(/[^+\d]/g, '')
  });

  if (!data.first_name.length || !data.last_name.length) {
    $("#loyalty-submit-error").fadeIn(200);
    return;
  }

  $.ajax({
    url: url,
    method: "post",
    contentType: "application/json",
    data: JSON.stringify(data),
    success: function success(data) {
      if (data === null || data === void 0 ? void 0 : data.active) {
        location.reload();
      }
    },
    error: function error(_error3) {
      var _error3$responseJSON, _error3$responseJSON$, _error3$responseJSON$2, _error3$responseJSON2, _error3$responseJSON3;

      console.error(_error3);
      var errorMsg = ((_error3$responseJSON = _error3.responseJSON) === null || _error3$responseJSON === void 0 ? void 0 : (_error3$responseJSON$ = _error3$responseJSON.error_messages) === null || _error3$responseJSON$ === void 0 ? void 0 : (_error3$responseJSON$2 = _error3$responseJSON$.confirmation_code) === null || _error3$responseJSON$2 === void 0 ? void 0 : _error3$responseJSON$2[0]) || ((_error3$responseJSON2 = _error3.responseJSON) === null || _error3$responseJSON2 === void 0 ? void 0 : (_error3$responseJSON3 = _error3$responseJSON2.phone) === null || _error3$responseJSON3 === void 0 ? void 0 : _error3$responseJSON3[0]);

      if (errorMsg) {
        $("#loyalty-phone-error").fadeIn(200).text(errorMsg);
      }
    }
  });
});
$(document).on("keydown", "#loyalty-phone", function () {
  var value = $(this).val().replace(/[^+\d]/g, '');

  if (value.length > 9) {
    $("#loyalty-phone-confirm").attr("disabled", false);
  } else {
    $("#loyalty-phone-confirm").attr("disabled", true);
  }
});
$(document).ready(function () {
  if ($("#loyalty-phone") && $("#loyalty-phone").val() && $("#loyalty-phone").val().replace(/[^+\d]/g, '').length > 9) {
    $("#loyalty-phone-confirm").attr("disabled", false);
  }
});

var getNoun = function getNoun(number, one, two, five) {
  var n = Math.abs(number);
  n %= 100;

  if (n >= 5 && n <= 20) {
    return five;
  }

  n %= 10;

  if (n === 1) {
    return one;
  }

  if (n >= 2 && n <= 4) {
    return two;
  }

  return five;
};

var getDate = function getDate(value) {
  var options = {
    day: 'numeric',
    month: 'numeric',
    year: 'numeric'
  };
  var date = new Date(value);
  return date.toLocaleString('ru', options);
};

if (document.querySelector(".loyalty-bonus-amount")) {
  var listBonusAmount = document.querySelectorAll(".loyalty-bonus-amount");
  listBonusAmount.forEach(function (bonus) {
    var amountBons = bonus.getAttribute("data-bonus-amount");
    var value;

    if (window.location.href.includes("/en/")) {
      value = getNoun(amountBons, 'point', 'points', 'points');
    } else {
      value = getNoun(amountBons, 'балл', 'балла', 'баллов');
    }

    bonus.nextElementSibling.innerHTML = value;
  });
}

if (document.querySelector(".loyalty-bonus-date")) {
  var listBonusDate = document.querySelectorAll(".loyalty-bonus-date");
  listBonusDate.forEach(function (date) {
    var dateBons = date.innerHTML;
    var dataDate = dateBons.split(' ');

    if (dataDate[1]) {
      date.innerHTML = getDate(dataDate[0]) + ' ' + dataDate[1].slice(0, -3);
    } else {
      date.innerHTML = getDate(dateBons);
    }
  });
}

$(document).on("change", "#is_sign_loyalty", function () {
  var value = $(this).prop('checked');

  if (value) {
    $(".modal-login__loyalty").slideDown(200);
  } else {
    $(".modal-login__loyalty").slideUp(200);
  }

  $("#birthday_sign").prop("required", value);
  $("#loyalty-phone").prop("required", value);
}); // // // // // // // // // // // // // // //
// ФАЙЛ НОВОГО JS ДЛЯ РЕФАКТОРИНГА СТАРОГО //
// // // // // // // // // // // // // // //

$(document).ready(function () {
  var location = window.location.href;
  var ru = "ru";
  var en = "/en/";

  if (navigator.language.includes(ru) && location.includes(en) && localStorage["myKey"] !== "1") {
    detectRuUserLanguage();
  } else if (!navigator.language.includes(ru) && !location.includes(en) && localStorage["myKey"] !== "1") {
    detectEnUserLanguage();
  }
});

function detectRuUserLanguage() {
  window.location.replace(window.location.origin + window.location.pathname.slice(3));
  localStorage["myKey"] = "1";
}

function detectEnUserLanguage() {
  window.location.replace(window.location.origin + '/en' + window.location.pathname);
  localStorage["myKey"] = "1";
}

$(document).ready(function () {
  // AJAX FIX
  $.ajaxSetup({
    beforeSend: function beforeSend(xhr, settings) {
      function getCookie(name) {
        var cookieValue = null;

        if (document.cookie && document.cookie !== "") {
          var cookies = document.cookie.split(";");

          for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]); // Does this cookie string begin with the name we want?

            if (cookie.substring(0, name.length + 1) === name + "=") {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }

        return cookieValue;
      }

      if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
      }
    }
  });
  $(document).on("click", ".select-city__modal-btn", function (e) {
    e.preventDefault();
    var city_name = $("#autodetect-city").text();
    var url = $(this).data("url");
    $.ajax({
      url: url,
      method: "post",
      data: {
        "city": city_name
      },
      success: function success(data) {
        if (data.success === true) {
          location.reload();
        } else {
          alert("Ошибка при выборе города");
        }
      },
      error: function error(data) {
        alert("Ошибка при выборе города");
      }
    });
  });
  $(document).on("click", ".select-city__cities-value", function (e) {
    e.preventDefault();
    var city_name = $(this).text();
    var url = $(this).data("url");
    $.ajax({
      url: url,
      method: "post",
      data: {
        "city": city_name
      },
      success: function success(data) {
        if (data.success === true) {
          window.location.reload(true);
        } else {
          alert("Ошибка при выборе города");
        }
      },
      error: function error(data) {
        alert("Ошибка при выборе города");
      }
    });
  }); // Подсказки города
  // Замените на свой API-ключ

  var token = "c66ecbfcebf9ebf518852462d38deb0b1b9ce87d";
  var defaultFormatResult = $.Suggestions.prototype.formatResult;

  function formatResult(value, currentValue, suggestion, options) {
    var newValue = suggestion.data.city;
    suggestion.value = newValue;
    return defaultFormatResult.call(this, newValue, currentValue, suggestion, options);
  }

  function formatSelected(suggestion) {
    return suggestion.data.city;
  }

  var lang = window.location.href.includes("/en/") ? "en" : "ru";
  $(".select-city__cities-input").suggestions({
    token: token,
    type: "ADDRESS",
    deferRequestBy: 350,
    minChars: 3,
    hint: false,
    language: lang,
    bounds: "city",
    constraints: {
      locations: {
        city_type_full: "город",
        country: "*"
      }
    },
    formatResult: formatResult,
    formatSelected: formatSelected,
    onSelect: function onSelect(suggestion) {
      var city_name = suggestion.data.city;
      var url = $(".select-city__cities-input").data("url");
      $.ajax({
        url: url,
        method: "post",
        data: {
          "city": city_name
        },
        success: function success(data) {
          if (data.success === true) {
            location.reload();
          } else {
            alert("Ошибка при выборе города, данного города нет в базе, выберите ближайший");
          }
        },
        error: function error(data) {
          alert("Ошибка при выборе города, данного города нет в базе, выберите ближайший");
        }
      });
    }
  });
  $(document).on('submit', '.ajax-login-form', function (e) {
    e.preventDefault();
    var data = $(this).serialize();
    var url = $(this).data("url");
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

  function clear_error_fields(element_array) {
    element_array.forEach(function (error_fild) {
      $(error_fild).text("");
    });
  }

  if (window.ApplePaySession) {
    //проверка устройства
    var merchantIdentifier = 'CloudPayments_4048608';
    var promise = ApplePaySession.canMakePaymentsWithActiveCard(merchantIdentifier);
    promise.then(function (canMakePayments) {
      if (canMakePayments) {
        $('#apple-pay').show(); //кнопка Apple Pay
      }
    });
  }

  function display_sizes(class_name) {
    var block = $(class_name);

    if (!!block && block.length > 0) {
      $.post(block.data("url")).then(function (data) {
        block.html(data);
      });
    }
  }

  display_sizes(".ajax-get-sizes");
  $(document).on('click', '#apple-pay', function () {
    var product_id = $(this).data("product-id");
    var product_name = $(this).data("product-name");
    var is_en = window.location.href.includes("/en/");
    var size_id = $(".size-item-wrapper.active").find("input").val();

    if (!size_id) {
      if ($(".n-product__fixed").hasClass("show")) {
        display_sizes(".ajax-fixed-sizes");
        $(".n-product__fixed-size").addClass("show");
        $(".n-product__fixed").addClass("shadow");
        $("body").addClass("no-scroll");
      }

      return;
    }

    var size_name = $(".size-item-wrapper.active").find("label").text().replace(/\s/g, "");
    var shippingOption = "";
    var product_price = parseInt($(this).data("price"));
    var delivery_price = 0;

    function get_apple_pay_total() {
      return product_price + delivery_price;
    }

    var total_price = get_apple_pay_total;

    function getShippingOptions(shippingCountry) {
      if (shippingCountry === "RU") {
        shippingOption = [{
          label: 'СДЭК',
          amount: delivery_price,
          'identifier': 'cdek'
        }];
      } else {
        shippingOption = [{
          label: 'DHL',
          amount: delivery_price,
          'identifier': 'dhl'
        }];
      }
    }

    var country_code = is_en ? "USA" : "RU";
    var currency = is_en ? "USD" : "RUB";
    var request = {
      requiredShippingContactFields: ['email', 'postalAddress', 'phone', 'name'],
      countryCode: country_code,
      currencyCode: currency,
      supportedNetworks: ['visa', 'masterCard'],
      merchantCapabilities: ['supports3DS'],
      lineItems: [{
        label: "".concat(product_name, " - ").concat(size_name),
        amount: product_price
      }, {
        label: 'Доставка',
        amount: delivery_price
      }],
      //Назначение платежа указывайте только латиницей!
      total: {
        label: "\u041E\u043F\u043B\u0430\u0442\u0430 \u0437\u0430\u043A\u0430\u0437\u0430",
        amount: total_price().toFixed('2')
      } //назначение платежа и сумма

    };
    var session = new ApplePaySession(1, request); // обработчик события для создания merchant session.

    session.onvalidatemerchant = function (event) {
      var data = {
        validationUrl: event.validationURL
      }; // отправьте запрос на ваш сервер, а далее запросите API CloudPayments
      // для запуска сессии

      $.post("/api/orders/apple-pay/start/", data).then(function (result) {
        session.completeMerchantValidation(result.Model);
      });
    }; // обработчик смены адреса доставки


    session.onshippingcontactselected = function (event) {
      $.post("/api/orders/apple-pay/delivery/", {
        product: product_id,
        country_code: event.shippingContact.countryCode,
        city: event.shippingContact.locality,
        postal_code: event.shippingContact.postalCode
      }).then(function (result) {
        delivery_price = parseFloat(result.delivery_price);
        getShippingOptions(event.shippingContact.countryCode);
        var status = ApplePaySession.STATUS_SUCCESS;
        var newTotal = {
          type: 'final',
          label: 'Оплата заказа',
          amount: get_apple_pay_total()
        };
        var newLineItems = [{
          type: 'final',
          label: product_name,
          amount: product_price
        }, {
          type: 'final',
          label: 'Доставка',
          amount: delivery_price
        }];
        session.completeShippingContactSelection(status, [], newTotal, newLineItems);
      });
    }; // обработчик события авторизации платежа


    session.onpaymentauthorized = function (event) {
      //var email = event.payment.shippingContact.emailAddress; //если был запрошен адрес e-mail
      //var phone = event.payment.shippingContact.phoneNumber; //если был запрошен телефон
      //все варианты смотрите на сайте https://developer.apple.com/reference/applepayjs/paymentcontact
      var data = {
        cryptogram: JSON.stringify(event.payment.token),
        email: event.payment.shippingContact.emailAddress,
        phone: event.payment.shippingContact.phoneNumber,
        product: product_id,
        size: size_id,
        first_name: event.payment.shippingContact.givenName,
        last_name: event.payment.shippingContact.familyName,
        locale: is_en ? 'en' : 'ru',
        address: event.payment.shippingContact.addressLines.join(),
        index: event.payment.shippingContact.postalCode,
        city: event.payment.shippingContact.locality,
        cost: product_price,
        delivery_cost: delivery_price,
        country_iso: event.payment.shippingContact.countryCode
      }; //передайте полученный токен на бэкэнд сервера и оттуда выполните
      //запрос  оплаты по криптограмме https://developers.cloudpayments.ru/#oplata-po-kriptogramme,
      //используя этот токен в параметре CardCryptogramPacket

      $.post("/api/orders/apple-pay/pay/", data).then(function (result) {
        if (!result.is_error) {
          session.completePayment(ApplePaySession.STATUS_SUCCESS);
          location.href = result.redirect_url;
        } else {
          session.completePayment(ApplePaySession.STATUS_FAILURE);
        }
      });
    }; // Начало сессии Apple Pay


    session.begin();
  }); // ajax registration

  $(document).on("submit", ".ajax-registration-form", function (e) {
    e.preventDefault();
    var is_loyalty = $("#is_sign_loyalty").prop('checked');

    var formData = _objectSpread(_objectSpread({}, Object.fromEntries(new FormData(this))), {}, {
      register_in_loyalty: is_loyalty
    });

    if (!is_loyalty) {
      delete formData.phone;
      delete formData.confirmation_code;
    } else if (formData.phone.length < 9) {
      if (window.location.href.includes("/en/")) {
        $(".error-registration-phone").text('Phone needs to be verified');
      } else {
        $(".error-registration-phone").text('Необходимо подтвердить телефон');
      }

      return;
    }

    var data = new URLSearchParams(formData).toString();
    var url = $(this).data("url");
    var element_errors_array = [".error-messages-registration", ".error-registration-firstname", ".error-registration-lastname", ".error-registration-date_of_birth", ".error-registration-email", ".error-registration-phone", ".error-registration-password1", ".error-registration-password2", ".error-registration-confirmation_code"];
    clear_error_fields(element_errors_array);
    $.ajax({
      url: url,
      data: data,
      method: "post",
      success: function success(data) {
        if (!!data.error) {
          Object.entries(data.error_messages).forEach(function (_ref) {
            var _ref2 = _slicedToArray(_ref, 2),
                key = _ref2[0],
                value = _ref2[1];

            switch (key) {
              case '__all__':
                $(".error-messages-registration").text(value[0]);
                return;

              case 'first_name':
                $(".error-registration-firstname").text(value[0]);
                return;

              case 'last_name':
                $(".error-registration-lastname").text(value[0]);
                return;

              case 'date_of_birth':
                $(".error-registration-date_of_birth").text(value[0]);
                return;

              case 'email':
                $(".error-registration-email").text(value[0]);
                return;

              case 'phone':
                $(".error-registration-phone").text(value[0]);
                return;

              case 'password1':
                $(".error-registration-password1").text(value[0]);
                return;

              case 'password2':
                $(".error-registration-password2").text(value[0]);
                return;

              case 'confirmation_code':
                $(".error-registration-confirmation_code").text(value[0]);
                return;
            }
          });
        } else {
          $(".ajax-registration-form  ").text(data.success_messages);
        }
      },
      error: function error(data) {
        alert("Ошибка при авторизации! Попробуйте позже.");
      }
    });
  });
  $(document).on("submit", ".change-password__form", function (e) {
    e.preventDefault();
    var data = {};
    data.old_password = $("#password_old").val();
    data.new_password = $("#password_new").val();
    data.new_password_confirm = $("#password_new_confirm").val();
    var url = $(this).data("url");
    $.ajax({
      url: url,
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify(data),
      method: "put",
      success: function success(data) {
        $("#passwordNewConfirmError").text("");
        $("#passwordNewError").text("");
        $("#passwordOldError").text("");
        $("#id-change-password-backend-error").text("");
        $("#password_old").val("");
        $("#password_new").val("");
        $("#password_new_confirm").val("");
        $("#change-password-success").show();
      },
      error: function error(data) {
        $("#change-password-success").hide();
        $("#passwordNewConfirmError").text("");
        $("#passwordNewError").text("");
        $("#passwordOldError").text("");
        $("#password_old").val("");
        $("#password_new").val("");
        $("#password_new_confirm").val("");

        if (data.responseJSON.new_password_confirm) {
          $("#passwordNewConfirmError").text(data.responseJSON.new_password_confirm[0]);
        }

        if (data.responseJSON.new_password) {
          $("#passwordNewError").text(data.responseJSON.new_password[0]);
        }

        if (data.responseJSON.old_password) {
          $("#passwordOldError").text(data.responseJSON.old_password[0]);
        }

        if (data.responseJSON.error) {
          $("#id-change-password-backend-error").text(data.responseJSON.error[0]);
        }
      }
    });
  });
  $(document).on("click", "#ajaxCart2", function (e) {
    $(".wrapper-ajax-cart, .modal-overlay").addClass("active");
    $("html").css("overflow-y", "hidden");
    $("body").css("overflow-y", "hidden");
    window.modal_cart_vue.get_cart_items();
  });
  $(document).on("click", ".n-product__order-checkout", function (e) {
    $(".wrapper-ajax-cart, .modal-overlay").addClass("active");
    $("html").css("overflow-y", "hidden");
    $("body").css("overflow-y", "hidden");
    window.modal_cart_vue.get_cart_items();
  });
  $(document).on("click", ".n-product__add-basket", function (e) {
    var product_id = $(this).data("busket-id");
    var price = $(this).data("product-price");

    if (product_id) {
      window.search_vue.add_to_cart(product_id);
    }

    var _tmr = _tmr || [];

    _tmr.push({
      type: 'reachGoal',
      id: '3140222',
      value: price,
      goal: 'addToCart',
      params: {
        product_id: product_id
      }
    });

    $(".n-product__order-checkout").addClass("show");
    $(".n-product__fixed-size").removeClass("show");
    $(".n-product__fixed").removeClass("shadow");
    $("body").addClass("no-scroll");
  });
  $(document).on("click", "#addToBasket", function (e) {
    var product_id = $(this).data("busket-id");
    var price = $(this).data("product-price");
    window.add_to_cart_vue.add_to_cart(product_id);

    var _tmr = _tmr || [];

    _tmr.push({
      type: 'reachGoal',
      id: '3140222',
      value: price,
      goal: 'addToCart',
      params: {
        product_id: product_id
      }
    });
  });
  $(document).on("click", ".n-product__add-favorites", function (e) {
    var product_id = $(this).data("item-id");
    var price = $(this).data("price");
    window.add_to_cart_vue.togglefavorite(product_id);

    _tmr.push({
      type: 'reachGoal',
      id: 3140222,
      value: price,
      goal: 'addToWishlist',
      params: {
        product_id: product_id
      }
    });
  });
  $(document).on("click", ".like-good-favorite", function (e) {
    var product_id = $(this).data("item-id");
    var price = $(this).data("price");
    window.search_vue.togglefavorite(product_id);

    _tmr.push({
      type: 'reachGoal',
      id: 3140222,
      value: price,
      goal: 'addToWishlist',
      params: {
        product_id: product_id
      }
    });
  });
  $(document).on("click", "#promoCode", function (e) {
    $(this).css("display", "none");
    $("#promoCodeBtn").css("display", "block");
  });
  $(document).on("click", "#certificate", function (e) {
    $(this).css("display", "none");
    $("#certificateBtn").css("display", "block");
  });
  $(document).on("click", "#subscribeToSize", function (e) {
    var product_id = $(this).data("product-id");
    var size = $('#sizeAvailable').text();

    if ($(".n-product__fixed").length && $(".n-product__fixed").hasClass("shadow")) {
      $(".n-product__fixed").removeClass("shadow");
      $(".n-product__fixed-size").removeClass("show");
      $("body").removeClass("no-scroll");
    }

    if (!!window.search_vue) {
      window.search_vue.subscribe_to_size(product_id, size);
    } else if (!!window.cart) {
      window.new_cart.subscribe_to_size(product_id, size);
    }
  });
  $(document).on("click", "#deleteSizeSubscribe", function (e) {
    var subscribe_id = $(this).data("subscribe-id");
    window.search_vue.delete_subscribe_to_size(subscribe_id);
  });
  $(document).on("click", "#id-recover-password-button", function (e) {
    var url = $("#passwordRestore").data("restore-pasw");
    var email = $("#id-recover-password-email").val();
    var data = {
      "email": email
    };
    $.ajax({
      url: url,
      contentType: "application/json",
      data: JSON.stringify(data),
      method: "post",
      success: function success(data) {
        $("#passwordRestore").text(data.result);
      },
      error: function error(data) {
        var key;

        for (var k in data.responseJSON) {
          key = k;
          break;
        }

        $("#id-error-recover-password").text(data.responseJSON[key]);
      }
    });
  });
  $(document).on("click", "#notificationClose", function (e) {
    $("#notificationBackground").fadeOut();
  });
  $(document).on("click", "#notificationMainClose", function (e) {
    $("#notificationMainBackground").fadeOut();
  });
  $(".order__close").on("click", function () {
    $(".mslistorder-output").hide();
    $("#mslistorders").fadeIn(100);
  });
  $(document).on("click", "#feedbackSubmit", function (e) {
    var url = $("#mainContacts").data("feedbeck-create");
    $(".error_nam3_zv0n0k").text("");
    $(".error_ph0n3_zv0n0k").text("");
    $(".error_ma1l_zv0n0k").text("");
    $("#feedbackError").text("");
    $(".error_msg_zv0n0k").text("");
    var error_message = "";
    var success_message = "";

    if (url.includes("/en/")) {
      error_message = "Fill this field"; //success_message = "Message sent";
    } else {
      error_message = "Заполните поле"; //success_message = "Сообщение отправлено";
    }

    var erros = false;

    if (!$("#nam3_zv0n0k").val().length) {
      $(".error_nam3_zv0n0k").text(error_message);
      var errors = true;
    }

    if (!$("#ph0n3_zv0n0k").val().length) {
      $(".error_ph0n3_zv0n0k").text(error_message);
      var errors = true;
    }

    if (!$("#ma1l_zv0n0k").val().length) {
      $(".error_ma1l_zv0n0k").text(error_message);
      var errors = true;
    }

    if (!$("#msg_zv0n0k").val().length) {
      $(".error_msg_zv0n0k").text(error_message);
      var errors = true;
    }

    if (errors) {
      return;
    }

    var data = {
      "name": $("#nam3_zv0n0k").val(),
      "phone": $("#ph0n3_zv0n0k").val(),
      "email": $("#ma1l_zv0n0k").val(),
      "message": $("#msg_zv0n0k").val()
    };
    $.ajax({
      url: url,
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify(data),
      method: "post",
      success: function success(data) {
        dataLayer.push({
          'event': 'feedback'
        });
        $("#nam3_zv0n0k").val(null);
        $("#ph0n3_zv0n0k").val(null);
        $("#ma1l_zv0n0k").val(null);
        $("#msg_zv0n0k").val(null);
        /*
        $("#notificationMainBackground").css({"background-color": "green"}).fadeIn();
        $("#notificationMainMessage").text(success_message);
        $("#notificationMainClose").css({"color": "white"});
        $("#notificationMainMessage").css({"color": "white"});
        setTimeout(function () {
            $("#notificationMainBackground").fadeOut();
        }, 6000);
         */
      },
      error: function error(data) {
        var key;

        for (var k in data.responseJSON) {
          key = k;
          break;
        }

        $("#feedbackError").text(data.responseJSON[key]);
      }
    });
  });
  $(document).on("click", "#restore-password-done", function (e) {
    var url = $("#restorePasswordDone").data("restode-pswd-done");
    var password = $("#resetPasswordNew").val();
    var repeated_password = $("#resetPasswordConfirm").val();
    var urlParams = new URLSearchParams(window.location.search);
    var uid = urlParams.get("uid");
    var token = urlParams.get("restore_token");
    var data = {
      "password": password,
      "repeated_password": repeated_password,
      "uid": uid,
      "activation_token": token
    };
    $("#resetPasswordError").text("");
    $("#resetPasswordConfirmError").text("");
    $.ajax({
      url: url,
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify(data),
      method: "post",
      success: function success(data) {
        $("#formRestorePasw").hide();
        $("#restoreSuccess").show();
      },
      error: function error(data) {
        $("#resetPasswordError").text(data.responseJSON.password);
        $("#resetPasswordError").text(data.responseJSON.non_field_errors);
        $("#resetPasswordConfirmError").text(data.responseJSON.repeated_password);
      }
    });
  }); // $(document).ready(function () {
  //     $.datepicker.regional['ru'] = {
  //         closeText: 'Закрыть',
  //         prevText: 'Предыдущий',
  //         nextText: 'Следующий',
  //         currentText: 'Сегодня',
  //         monthNames: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
  //         monthNamesShort: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'],
  //         dayNames: ['воскресенье', 'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'],
  //         dayNamesShort: ['вск', 'пнд', 'втр', 'срд', 'чтв', 'птн', 'сбт'],
  //         dayNamesMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
  //         dateFormat: 'dd.mm.yy',
  //         showMonthAfterYear: false,
  //     };
  //     $.datepicker.regional["en-GB"] = {
  //         closeText: "Done",
  //         prevText: "Prev",
  //         nextText: "Next",
  //         currentText: "Today",
  //         monthNames: ["January", "February", "March", "April", "May", "June",
  //             "July", "August", "September", "October", "November", "December"],
  //         monthNamesShort: ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
  //             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
  //         dayNames: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
  //         dayNamesShort: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
  //         dayNamesMin: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
  //         weekHeader: "Wk",
  //         dateFormat: "dd/mm/yy",
  //         firstDay: 1,
  //         isRTL: false,
  //         showMonthAfterYear: false,
  //         yearSuffix: ""
  //     };
  //
  //     $("#datepicker").on("change", function () {
  //         let hVal = $(this).val();
  //         let tDate = (new Date(hVal)).getTime() / 1000;
  //         $("#dob").val(tDate);
  //     });
  //
  //     if (window.location.href.includes("/en/")) {
  //         $.datepicker.setDefaults($.datepicker.regional["en-GB"]);
  //     } else {
  //         $.datepicker.setDefaults($.datepicker.regional["ru"]);
  //     }
  //     $("#birthday_sign").datepicker({
  //         showAnim: "show",
  //         altFormat: "yy-mm-dd",
  //         dateFormat: "dd.mm.yy",
  //         changeMonth: true,
  //         changeYear: true,
  //         yearRange: "1950:2008",
  //         defaultDate: "-25y",
  //         onSelect: function (value) {
  //             const date = new Date(value).toLocaleDateString('en-ca')
  //             $(this).attr("data-val", date)
  //         },
  //     });
  // });

  $(document).ready(function () {
    $('#date_mask').mask("99.99.9999", {
      placeholder: "__.__.____"
    });
  });
  $(document).on("click", "#restorePasswordSubmit", function (e) {
    $("#restorePasswordSuccess").text("");
    $(".loginFPErrors").text("");
    var url = $("#passwordRestore").data("restore-pasw");
    var email = $("#emailForRestore").val();
    var data = {
      "email": email
    };
    $.ajax({
      url: url,
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify(data),
      method: "post",
      success: function success(data) {
        $("#restorePasswordSuccess").text(data.result);
      },
      error: function error(data) {
        $(".loginFPErrors").text(data.responseJSON.non_field_errors);
      }
    });
  });
  $(document).on("submit", '.welcome-ajax-form', function (e) {
    e.preventDefault();
    var data = $(this).serialize();
    var url = $(this).data('url');
    var parent = $(this).parent();
    $.ajax({
      url: url,
      data: data,
      method: 'post',
      success: function success(data) {
        dataLayer.push({
          'event': 'email_popup'
        });
        $(".modal-welcome").removeClass("active");
        $(".modal-overlay").removeClass("active big-z-index");
        $("body").removeClass("no-scroll");
      },
      error: function error(data) {
        parent.html(data);
      }
    });
  });
});
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