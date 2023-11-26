window.sr = ScrollReveal();

sr.reveal('.lookbook-card_animation', {
    duration: 1000,
    distance: '28px',
    opacity: 0,
    delay: 150
});

(function() {
    setTimeout(() => {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
        document.documentElement.style.setProperty('--vh_h', `${vh}px`);

        window.addEventListener('resize', () => {
            let vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        });
    }, 0);
})();

$(document).ready(function() {
    // Правильный показ доставок
    let old_city = $("*[name=\"city\"]").val();
    if (old_city !== undefined) {
        old_city = old_city.trim().toLowerCase();
        setInterval(function() {
            var city = $("*[name=\"city\"]").val().trim().toLowerCase();
            if (city != old_city && $("select[name=\"country\"]").val().trim() && $("input[name=\"index\"]").val().trim()) {
                $(".delivery-availible").hide();
                $(".delivery-not-availible").show();
            }
            old_city = city;
        }, 50);
    }

    // Lookbook
    $(".lookbook__goods").click(function() {
        $(".lookbook__goods.active").removeClass("active");
        var container = $(this).data("container");
        if ($(this).hasClass("active")) {
            $("#" + container).hide();
            $(this).removeClass("active");
        } else {
            if (container) {
                $(this).addClass("active");
                $("#" + container).show();
            }
        }
    });

    $(".lookbook__goods-close").click(function() {
        $(this).parent().hide();
        $(".lookbook__goods.active").removeClass("active");
    });

    // footer_border
    if ($(".footer_border").length && $(window).innerWidth() < 992 && (window.location.href.includes('/collection') || window.location.href.includes('/cart'))) {
        $(".footer").removeClass("footer_border");
    }
});

$(document).on('keyup change', '.custom_input', function(e) {
    this.setAttribute('data-val', this.value);
});

$("#nl_promo").on("change", function() {
    $("#change_subscription").submit();
});

$("#human_date").on("change", function() {
    let hVal = $(this).val();
    let tDate = (new Date(hVal)).getTime() / 1000;
    $("#dob").val(tDate);
});


$(document).ready(function() {
    let header = $(".header");
    let	scrollPrev = 0;
    let height = header.outerHeight();

    $(window).scroll(function() {
        let scrolled = $(window).scrollTop();

        if ($(window).width() < 992) {
            if ( scrolled > height && scrolled > scrollPrev ) {
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
                $("body").removeClass("show-topBar")
            }
        } else {
            header.removeClass("fixed");
            if ($("body").hasClass("has-topBar")) {
                $("body").addClass("show-topBar")
            }

            if ($(window).width() < 992) {
                $('.header_light').removeClass('dark');
            }
        }
    });
});

$(".footer__contacts").on("click", function() {
    $(".modal-contacts").fadeIn(200);
});

$(".modal-contacts__close").on("click", function() {
    $(".modal-contacts").fadeOut(200);
});

$(".search_open").on("click", function() {
    $(".search").addClass("active");
    setTimeout(function () {
        $("input#search-input").focus();
    }, 50);
    if ($(window).width() >= 992) {
        $(".modal-overlay").addClass("active");
        $("body").addClass("no-scroll");
    }
});

$(document).on("click", ".search__close-btn, .modal-overlay.active", function() {
    $(".search").removeClass("active");
    $(".modal-overlay").removeClass("active");
    if ($(window).width() >= 992) {
        $("body").removeClass("no-scroll");
    }
    $(".search__form")[0].reset();
});

$('.custom_input_select').click(function(){
    $(".custom_options_select").slideToggle(150);
});

$('.custom_input_select').blur(function(){
    $(".custom_options_select").hide(150);
});

$(".custom_option input").on("change", function() {
    let val = $(".custom_option input:checked").val();
    let id = $(".custom_option input:checked").attr("id");
    $("#size-input").val(val).attr("data-id", id);
    $("#size-input").val(val);
    $(".custom_label_select").addClass("top");
    $(".custom_options_select").hide(150);
});

$(".auth_open").click(function(e) {
    $(".modal-login").addClass("active");
    if (!$('.modal-overlay').hasClass('active') && $(window).innerWidth() > 991) {
        $('.modal-overlay').addClass('active');
    }
});

$(document).on("click", ".modal-login__close, .modal-overlay.active, .modal-login.active", function(e) {
    if ($(".modal-login__content").has(e.target).length === 0) {
        $(".modal-login").removeClass("active");

        $('.modal-login__title-box, .modal-login__link-box, .modal-login__group').show();
        $('.modal-login__title_recover, .modal-login__col_recover, .modal-login__col, .modal-login__title, .modal-login__link, .modal-overlay').removeClass('active');
        $('.modal-login__col[data-tab="login"], .modal-login__title[data-tab="login"], .modal-login__link[href="sign"]').addClass('active');
    }
});

$('.modal-login__tab-link').click(function(e) {
    e.preventDefault();
    if (!$('.modal-overlay').hasClass('active') && $(window).innerWidth() > 991) {
        $('.modal-overlay').addClass('active');
    }
    if (!$("body").hasClass("no-scroll")) {
        $("body").addClass("no-scroll");
    }
    const id = $(this).attr('href'),
          content = $('.modal-login__col[data-tab="'+ id +'"]'),
          title = $('.modal-login__title[data-tab="'+ id +'"]'),
          thisLink = $('.modal-login__link[href="'+ id +'"]');

    $('.modal-login__col').removeClass('active');
    $('.modal-login__title').removeClass('active');
    content.addClass('active');
    title.addClass('active');
    $('.modal-login__tab-link').addClass('active');
    if (thisLink.hasClass('active')) {
        thisLink.removeClass('active');
    }
});

$('.modal-login__link-recover').click(function(e) {
    e.preventDefault();
    $('.modal-login__title_recover, .modal-login__col_recover').addClass('active');
    $('.modal-login__title-box, .modal-login__link-box, .modal-login__group').hide();
});

$(document).on("click", ".close-form, .close-ajax-cart, .modal-overlay.active", function(e) {
    e.preventDefault();
    $(".wrapper-ajax-cart, .modal-overlay").removeClass("active");
    $("html").css("overflow-y", "");
    $("body").css("overflow-y", "");
});

$(".profile__change-password").click(function() {
    $(".modal-overlay").addClass("active");
    $(".change-password").addClass("active");
    $("body").addClass("no-scroll");
});

$(document).on("click", ".change-password__close, .modal-overlay.active, .change-password.active", function(e) {
    if (!$(".change-password__content").is(e.target) && $(".change-password__content").has(e.target).length === 0) {
      $(".change-password").removeClass("active");
      $(".modal-overlay").removeClass("active");
      $("body").removeClass("no-scroll");
    }
});

$(".lexicon-open").click(function () {
    $(".lexicon-modal").slideToggle(200);
    $(".burger__scroll").stop().animate({ scrollTop: 0 }, 400);

    if ($(".lexicon-modal").css("display") === "block") {
        $(".lexicon-close").show();

        if ($(window).width() < 992) {
            setTimeout(() => {
                const height = $(".lexicon-modal").outerHeight();
                let top = $(".burger__menu_last").css("marginTop");
                top = Number(top.substr(0, top.length-2));

                if (top > height) {
                    $(".burger__menu_last").css("marginTop", top - height + 'px');
                } else {
                    $(".burger__menu_last").css("marginTop", 0);
                }

            }, 200)
        }
    }

    setTimeout(() => {
        if ($(".lexicon-modal").css("display") !== "block" && $(window).width() < 992) {
            $(".lexicon-close").hide();
            $(".burger__menu_last").attr('style', '');
        }
    }, 230)
});

$(".lexicon-close").click(function () {
    $(".lexicon-modal").slideUp(200);
    $(".lexicon-close").hide();

    if ($(window).width() < 992) {
        setTimeout(() => {
            $(".burger__menu_last").attr('style', '');
        }, 200)
    }
});

function openModalWelcom() {
    localStorage.setItem("modal", "1");
    $(".modal-overlay").addClass("active big-z-index");
    $(".modal-welcome").addClass("active");
    $("body").addClass("no-scroll");
}

function closeModalWelcom() {
    $(".modal-welcome").removeClass("active");
    $(".modal-overlay").removeClass("active big-z-index");
    $("body").removeClass("no-scroll");
}

$(document).on("click", ".modal-welcome__close, .modal-overlay.active, .modal-welcome.active", function(e) {
    if ($(".modal-welcome__box").has(e.target).length === 0) {
        closeModalWelcom()
    }
});

$("#go_to_registration").on("click", function() {
    closeModalWelcom()
})

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

$(".radio-custom").on("click", function() {
    $(this).toggleClass("active").siblings("var-delivery_item ").toggleClass("active");
});


$(".order-row_item").on("click", function() {
    if (!($(this).hasClass("active"))) {
        $(this).addClass("active").siblings().removeClass("active");
    }
});

$(".photo-row_item").on("click", function() {
    if (!($(this).hasClass("active"))) {
        $(this).addClass("active").siblings().removeClass("active");
    }
});

$(".instastore-row_item").on("click", function() {
    $(".wrapper-card").addClass("active");
});

$(".wrapper-card").on("click", function() {
    $(this).removeClass("active");
});

$(".slideshow_pic").on("click", function(e) {
    e.preventDefault();
    var
        $this = $(this),
        item = $this.closest(".tovar-preview"),
        container = $this.closest(".row"),
        display = container.find(".slideshow_display"),
        path = item.find("img").attr("src"),
        link = item.find("a").attr("href"),

        duration = 300;
    if (!item.hasClass(".active")) {

        item.addClass("active").siblings().removeClass("active");

        display.find("img").fadeOut(duration, function() {
            $(this).attr("src", path).fadeIn(duration);
        });
        display.find("a").fadeOut(duration, function() {
            $(this).attr("href", link).fadeIn(duration);
        });
    }
});
function display_sizes(class_name) {
    const block = $(class_name);
    if(block) {
        $.post(block.data("url")).then(function(data) {
            block.html(data);
        })
    }
}
$(".n-product__order-block").click(function () {
    if($(".n-product__fixed").hasClass("show")) {
        display_sizes(".ajax-fixed-sizes");
        $(".n-product__fixed-size").addClass("show");
        $(".n-product__fixed").addClass("shadow");
        $("body").addClass("no-scroll");
    }
});

$(".n-product__fixed-close").click(function () {
    $(".n-product__fixed-size").removeClass("show");
    $(".n-product__fixed").removeClass("shadow");
    $("body").removeClass("no-scroll");
});

$(document).on("click", function(e) {
    if ($(".n-product__fixed-size").hasClass("show") && !$(".n-product__fixed").is(e.target) && $(".n-product__fixed").has(e.target).length === 0) {
        e.preventDefault();
        $(".n-product__fixed-size").removeClass("show");
        $(".n-product__fixed").removeClass("shadow");
        $("body").removeClass("no-scroll");
    }
});

$(document).on("scroll", function() {
    if($(window).width() < 992) {
        const scrollTop = $(document).scrollTop();
        const topSubscribe = $(".subscribe").offset().top - $(window).height();
        if ( scrollTop < 50 || scrollTop > topSubscribe) {
            $(".n-product__fixed").removeClass("show");
        } else {
            $(".n-product__fixed").addClass("show");
        }
    }
});

/* активный размер в карточке товара */
$(document).on("click", ".size-item-wrapper", function() {
    if (!($(this).hasClass("size-not-available"))) {
        $(".size-item.wrapper").removeClass("active");
        $(this).addClass("active").siblings().removeClass("active");
        $(".n-product__order-block").hide();
        $(".n-product__order-checkout").removeClass("show");
        $(".n-product__fixed").removeClass("active");
        $(".present__product-size").text($(this).find("input").attr("name"));
        $(".n-product__present-info").hide();
        window.new_present.get_product_size();
    }
});

/* раскрывает полный адрес в таблице наличия */
$(".avl-more, .avl-less").on("click", function(e) {
    e.preventDefault();
    if (!$(this).hasClass("avl-less")) {
        $(".avl-table .avl-address").removeClass("show");
    }
    $(this).parent().toggleClass("show");
});


/* передаем размер в модальное окно "Узнать о поступлении" */
$(document).on("click", ".size-link", function() {
    let size = $(this).data("size");
    $("#size_subscribe .regular .size-item").text(size);
    $(".size-thanks-wrapper").css("display", "none");
    $(".size-subscribe-wrapper").css("display", "block");
});


function initializeItiPhone(inputPhone, errorSelector) {
    let input = document.querySelector(inputPhone);
    const errorMsg = document.querySelector(errorSelector);
    const errorMap = ["Неверный номер", "Неверный код страны", "Слишком короткий", "Слишком длинный", "Неверный номер"];
    const errorEnMap = ["Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];
    if (input) {
        let iti = window.intlTelInput(input, {
            utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
            nationalMode: false,
            formatOnDisplay: true,
            autoHideDialCode: false,
            initialCountry: "ru",
            preferredCountries: ["ru", "by", "kz", "az", "uz", "am", "ge", "kg"],
            geoIpLookup: function(callback) {
                $.get("//ipinfo.io", function() {
                }, "jsonp").always(function(resp) {
                    let countryCode = (resp && resp.country) ? resp.country : "";
                    callback(countryCode);
                });
            }
        });
        const reset = function() {
            input.classList.remove("error");
            errorMsg.innerHTML = "";
            errorMsg.classList.add("hide");
        };
        const handleChange = function() {
            $(inputPhone).data("phone-number", iti.getNumber());
            reset();
        };

        input.addEventListener('blur', function() {
            reset();
            if (input.value.trim()) {
                const re = /^[\d\+][\d\(\)\ -]{4,14}\d$/
                const valid = re.test(input.value.trim());
                let errorCode = -1
                if (valid && !iti.isValidNumber()) {
                    errorCode = iti.getValidationError();
                }
                if (!valid || errorCode >= 0) {
                    input.classList.add("error");
                    const errorMsgText = window.location.href.includes("/en/") ?
                      errorEnMap[errorCode] ? errorEnMap[errorCode] : "Enter a valid number" :
                      errorMap[errorCode] ? errorMap[errorCode] : "Введите корректный номер"
                    errorMsg.innerHTML = errorMsgText;
                    errorMsg.classList.remove("hide");
                }
            }
        });
        input.addEventListener("change", handleChange);
        input.addEventListener("keyup", handleChange);
    }
}


$(document).on("click", ".n-product__present", function() {
    if ($("#present").css("display") === 'block') {
        setTimeout(() => {
            window.new_present.get_phone_input("#recipient_phone");
            window.new_present.initDadata();
        });
    }
});

$(document).ready(function() {
    setTimeout(() => {
        initializeItiPhone("#phone", "#phone-intl-error");
        initializeItiPhone("#loyalty-phone", "#loyalty-phone-intl-error");
    }, 2000)
});

$(document).on("click", "a.admission", function() {
    $("#size_subscribe input[name=size]").val("");
    $("#size_subscribe .regular").hide();
    $("#size_subscribe .admission").show();
});
$(document).on("click", "#size_subscribe .admission .size-item-wrapper", function() {
    var sz = $(this).find("input").val();
    $("#size_subscribe input[name=size]").val(sz);
});


/* accordions */
$(document).ready(function() {
    $(".accordion-title").click(function() {
        if ($(this).hasClass("active")) {
            $(this).removeClass("active");
            $(this).closest(".popup-list_item_border").removeClass("open");
            $(this).next("div").slideUp(200);
        } else {
            $(".accordion-title").next("div").slideUp(200);
            $(".accordion-title").removeClass("active");
            $(this).addClass("active");
            $(this).closest(".popup-list_item_border").addClass("open");
            $(this).next("div").slideDown(200);
        }
    });
});

/* submenu for burger */
$(document).ready(function() {
    $(".submenu-open").click(function() {
        $(this).next("div").fadeIn(200);
    });

    $(".submenu-close").click(function() {
        $(".burger__submenu").fadeOut(200);
    });
});

/* бестселлеры на главной */
if (document.querySelector('.home-bestsellers')) {
    const bestsellersCard = new Swiper('.home-bestsellers', {
        speed: 400,
        spaceBetween: 0,
        slidesPerView: 2,
        navigation: {
            nextEl: '.bestsellers-next',
            prevEl: '.bestsellers-prev',
        },
        breakpoints: {
            992: {
                slidesPerView: 4,
            }
        }
    });
}

/* галерея изображений магазина в контактах */
if ($(".contacts__shop-slides").length) {
    $(".contacts__shop-slides").slick({
            prevArrow: "<button type=\"button\" class=\"thumbs-prev\"><i class=\"slider-prev\"></i></button>",
            nextArrow: "<button type=\"button\" class=\"thumbs-next\"><i class=\"slider-next\"></i></button>",
            appendArrows: ".contacts__shop-arrows",
            arrows: true,
            infinite: false,
            slidesToShow: 1,
            slidesToScroll: 1,
            adaptiveHeight: true
        });
};

$(".video_play").click(function() {
    $(".video_player").trigger("play");
});

// слайдер Уход за одеждой
const swiperCare = new Swiper('.clothing-care__slider', {
  loop: false,
  speed: 500,
  slidesPerView: 1,
  spaceBetween: 0,
  pagination: {
    el: '.clothing-care__pagination',
    type: 'custom',
    renderCustom: function (swiper, current, total) {
        const formattedCurrent = current < 10 ? `0${current}` : current;
        const formattedTotal = total < 10 ? `0${total}` : total;
      return '<span>'+ formattedCurrent +'</span>' +
          '<div class="home-swiper-pagination-after"></div>' +
          '<span>'+ formattedTotal +'</span>';
      },
  },
  navigation: {
    nextEl: '.clothing-care__next',
    prevEl: '.clothing-care__prev',
  },
  breakpoints: {
      992: {
          speed: 1200,
      },
  }
});

/* таблица размеров в карточке товаров */
$("[data-fancybox=\"size_table\"]").fancybox({
    touch: false
});

/* купить сейчас
$('[data-fancybox="order_now"]').fancybox({
  touch: false
});*/

/* instastore */
$("[data-fancybox=\"instastore\"]").fancybox({
    loop: true,
    buttons: [
        "close"
    ]
});

/* video */
$("[data-fancybox=\"video\"]").fancybox({
    loop: true,
    buttons: [
        "close"
    ]
});

/* lookbook */
$("[data-fancybox=\"lookbook\"]").fancybox({
    loop: true,
    buttons: [
        "close"
    ]
});

/* фильтры в каталоге */
$(".filter_open").click(function() {
    $(this).toggleClass("active");		//делаем данный пункт активным/неактивным
    $(this).next("div").slideToggle(200);

    // top для sidebar при открытии фильтров
    if ($(this).hasClass("filter__title")) {
        setTimeout(function() {
            let theOffset = $(".catalog__list-box").outerHeight();
            let height = theOffset - $(window).height();

            if ($(window).innerWidth() >= 992 && theOffset > $(window).height()) {
                $(".catalog__list-box").css("top", -height + "px");
            }
        }, 100);
    }
});

function filterOpenMobile(btn, block) {
    btn.click(function() {
        if ($(window).innerWidth() < 992) {
            block.fadeIn(200);
            $(".home-body").css("overflow", "hidden");
        }
    });
}

filterOpenMobile($(".filters-open"), $(".filter"));

function closeModalFilter() {
    $(".filter-modal").fadeOut(200);
    $(".home-body").css("overflow", "");
}

$('.filter__sort').on("click", function() {
    $('.filter__sort').removeClass('active');
    $(this).addClass('active');
});

$(".filter-modal-close").on("click", function() {
    closeModalFilter();
});

$("#min_cost").on("change",function(){
    let value1 = $(this).val();
    let value2 = $("#max_cost").val();

    if (parseInt(value1) < MIN_COST) { value1 = MIN_COST; $("#min_cost").val(value1) }
    if(parseInt(value1) > parseInt(value2)){
        value1 = value2;
        $("#min_cost").val(value1);
    }
    $("#filter-range").slider("values", 0, parseInt(value1));
});

$("#max_cost").on("change",function(){
    let value1 = $("#min_cost").val();
    let value2 = $(this).val();

    if (parseInt(value2) > MAX_COST) { value2 = MAX_COST; $("#max_cost").val(value2) }
    if(parseInt(value1) > parseInt(value2)) {
        value2 = value1;
        $("#max_cost").val(value2);
    }
    $("#filter-range").slider("values", 1, parseInt(value2));
});

/* карты в контактах */
// $(".our_shop-onmap").click(function() {
//     $(".contacts__shop-map:visible").slideUp(10);
//     $(this).parent().next(".contacts__shop-map:hidden").slideDown(10);
// });

$(document).ready(function() {
    $(".minus").click(function() {
        var $input = $(this).parent().find("input");
        var count = parseInt($input.val()) - 1;
        count = count < 1 ? 1 : count;
        $input.val(count);
        $input.change();
        return false;
    });
    $(".plus").click(function() {
        var $input = $(this).parent().find("input");
        if ($input.val() < $input.attr("max")) {
            $input.val(parseInt($input.val()) + 1);
            $input.change();
        } else {
            // miniShop2.Message.error(mspr_not_enough);
        }
        return false;
    });
});

/* корзина */
function showAddres(status) {
    if (status == 1) {
        //  $(".cart_address").slideUp(300);
    } else if (status == 7) {
        // $(".cart_address").slideDown(300);
        // $(".cart_street").slideUp(300);
    } else {
        // $(".cart_address").slideDown(300);
        // $(".cart_street").slideDown(300);
    }
}

$(function() {
    if ($("*").is("#order_container")) {
        showAddres($("input[name=delivery]:checked").val());
        $("input[name='delivery']").click(function() {
            showAddres($("input[name=delivery]:checked").val());
        });
    }
});

$(".payment").click(function() {
    $(".payment").removeClass("payment_active");
    $(this).addClass("payment_active");
});

function payment_active() {
    if ($("input[name='payment']").is(":checked")) {
        $("input[name=payment]:checked").parent().addClass("payment_active");
    }
};

$(document).ready(payment_active);

$(".btn-avl-open").click(function() {
    $(".avl-modal").fadeIn(200);
    $("body").addClass("no-scroll");
    if ($(window).width() >= 768) {
        $(".modal-overlay").addClass("active");
    }
    const url = $(".n-product__availability").data("fb-stock-url");
    $.ajax({
        url: url,
        method: "post",
        contentType: "application/json",
        data: JSON.stringify()
    })
})

function closeModalForOverlayAndBtn(overlay, btn, modal, e) {
    if (e.target.className === overlay || $(btn).has(e.target).length) {
        $(modal).fadeOut(200);
        $(".modal-overlay").removeClass("active");
        $("body").removeClass("no-scroll");
    }
}

$(document).on("click", ".avl-modal__container, .avl-modal__close", function(e) {
    closeModalForOverlayAndBtn("avl-modal__container", ".avl-modal__close", ".avl-modal", e);
});

$(document).on("click", ".hint-modal__container, .hint-modal__close", function(e) {
    closeModalForOverlayAndBtn("hint-modal__container", ".hint-modal__close", ".hint-modal", e);
});

$(document).on("click", ".present__container, .present__close", function(e) {
    closeModalForOverlayAndBtn("present__container", ".present__close", ".present", e);
});

if (document.querySelector('.n-product__preview-slider')) {
    const productSlider = new Swiper('.n-product__slider', {
        direction: "vertical",
        spaceBetween: 4,
        slidesPerView: 5,
        freeMode: true,
        watchSlidesVisibility: true,
        watchSlidesProgress: true,
    });
    const productSliderPreview = new Swiper('.n-product__preview-slider', {
        speed: 400,
        loop: true,
        spaceBetween: 0,
        slidesPerView: 1,
        pagination: {
            el: '.n-product__pagination',
        },
        navigation: {
            nextEl: ".n-product__next",
            prevEl: ".n-product__prev",
        },
        thumbs: {
            swiper: productSlider,
        },
    });
}

if (document.querySelector('.n-product__zoom-preview-slider') && document.documentElement.clientWidth < 992) {
    const productZoomSliderPreview = new Swiper('.n-product__zoom-preview-slider', {
        speed: 400,
        loop: true,
        spaceBetween: 0,
        slidesPerView: 1,
        pagination: {
            el: '.n-product__zoom-pagination',
        }
    });
} else if (document.querySelector('.n-product__zoom-preview-slider')) {
    $('.n-product__zoom-preview-slider').removeClass('swiper-container');
    $('.n-product__zoom-preview-col').removeClass('swiper-wrapper');
    $('.n-product__zoom-preview-slide').removeClass('swiper-slide');
}

$(".n-zoom-open").click(function () {
    let target = $('.scroll-anchor-target[data-scroll-target="' + $(this).data('zoom') + '"]');

    $('.n-product__zoom-media').each(function () {
        $(this).attr('src', $(this).data('src'));
        $(this).removeAttr('data-src');
    });

    $(".n-product__zoom-modal").addClass("active");
    $("body").addClass("no-scroll");
    $('.scroll-anchor-trigger[data-scroll-anchor="' + $(this).data('zoom') + '"]').addClass("active");
    $('.n-product__zoom-preview-slider').stop().animate({ scrollTop: target.offset().top}, 0);
});

function closeZoomSlide() {
    $(".n-product__zoom-modal").removeClass("active");
    $("body").removeClass("no-scroll");
    setTimeout(() => {
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
});

// скролл к карточке на странице товара
function initSmoothScroll() {
    let anchors = $('.scroll-anchor-trigger');

    if(!anchors.length) return;
    anchors.on('click', function(){
        anchors.removeClass('active');
        $(this).addClass('active');
    });

    for (let i = 0; i < anchors.length; i++) {
        let anchor = anchors[i];

        $(anchor).on('click', function () {
            let target = $('.scroll-anchor-target[data-scroll-target="' + $(this).data('scroll-anchor') + '"]');
            let new_position = target[0].offsetTop;
            $('.n-product__zoom-preview-slider').stop().animate({ scrollTop: new_position }, 400);
        });
    }

    $('.n-product__zoom-preview-slider').scroll(function () {
        let anchorTargets = $('.scroll-anchor-target');

        for (let i = 0; i < anchorTargets.length; i++) {
            let anchorTarget = anchorTargets[i];

            let slidePosition = $(anchorTarget).offset().top - $(anchorTarget).height()*0.3;
            let windowScrollPosition = $(window).scrollTop();
            let anchorActive = $('.scroll-anchor-trigger[data-scroll-anchor="' + $(anchorTarget).data('scroll-target') + '"]');

            if( slidePosition < windowScrollPosition ) {
                $('.scroll-anchor-trigger').removeClass("active");
                anchorActive.addClass("active");
            }
        }
    });
}

initSmoothScroll();


//all colors на странице товара
$(".all-colors-open").on("click", function() {
    $(".all-colors").addClass("active");
    $("body").addClass("no-scroll");
    if ($(window).width() >= 768) {
        $(".modal-overlay").addClass("active");
    }
});

$(document).on("click", ".all-colors-close, .modal-overlay.active", function() {
    $(".all-colors").removeClass("active");
    $("body").removeClass("no-scroll");
    if ($(window).width() >= 768) {
        $(".modal-overlay").removeClass("active");
    }
});


// Collections
$(document).ready(function() {
    if ($('.collections').length && $(window).width() < 768) {
        $('.subscribe').addClass('border_none');
    }
});

function get_collection_products(vm) {
    $('.collection__products-row').addClass('loading');
    let url = vm.data('url');
    let col = vm.data('col');
    let row_id = vm.data('row');
    let class_obj = vm.data('class');
    let data = {
        col: col,
        row_id: row_id
    }
    $.ajax({
        url: url,
        data: data,
        method: 'post',
        success: function (data) {
            // console.log(data.tpl);
            // console.log(vm.closest('.collection__row').find('.collection__products'));
            const container = vm.closest('.collection__row').find(`.${class_obj}`).html(data.tpl);
        },
        error: function (error) {
            console.log('SOMETHING GOES WRONG')
        },
        complete: function (data) {
            $('body').removeClass('loading');
            $(".collection__products-row").removeClass('loading');
        }
    })
}

$(document).ready(function() {
    $('.collection__card').on('click', function () {
        if ($(this).find('.collection__btn').length) {
            let row = $(this).parents('.collection__row');
            let product = $(this).next('.collection__products');

            get_collection_products($(this));
            $(this).find('.collection__btn').toggleClass('open');
            product.slideToggle(180);

            if ($(window).width() >= 768) {
                if (row.find('.collection__btn').hasClass('open')) {
                    row.find('.collection__btn').not($(this).find('.collection__btn')).removeClass('open')
                    setTimeout(() => {
                        row.find('.collection__products').not(product).slideUp(180);
                    }, 80)
                }

            }
        }
    });
});

// subscribe
$('.subscribe__form input').focus(() => {
    $('.subscribe__submit').addClass('active');
    $('.subscribe__policy').addClass('active');
});

$('.subscribe__form input').blur(() => {
    $('.subscribe__submit').removeClass('active');
    $('.subscribe__policy').removeClass('active');
});


// animate emblem for product detail
function addLettersAnimation(el) {
    let indicator = el.children('.emblem-animate');
    setTimeout(function() {
        $(indicator).addClass('active');
    }, 0);
}

$(document).ready(function() {
    $('.emblem').mouseover(function() {
        addLettersAnimation($(this))
    });

    $(window).on('scroll', () => {
        if ($('.emblem') && $(window).width() < 992) {
            let blockPosition = $('.emblem').offset().top + $('.emblem').height();
            let windowScrollPosition = $(window).scrollTop() + $(window).height() - $('.n-product__fixed').height();

            if( blockPosition < windowScrollPosition ) {
                addLettersAnimation($('.emblem'))
            }
        }
    });
});

const getLoyaltyTimer = (resend_available) => {
    $("#loyalty-timer").fadeIn(200)
    $("#loyalty-phone-confirm").attr('disabled', true)

    const seconds = $("#loyalty-timer-seconds");
    let secVal = parseInt(seconds.text());

    let timer = setTimeout(function tick() {
        if (secVal > 0) {
            seconds.text(--secVal);
            timer = setTimeout(tick, 1000);
        } else {
            $("#loyalty-timer").fadeOut(200)
            seconds.text(resend_available)
            $("#loyalty-phone-confirm").attr('disabled', false)
        }
    }, 1000);
}

$(document).on("click", "#loyalty-phone-confirm", function(e) {
    e.preventDefault();
    let phone = $("#loyalty-phone").val().replace(/[^+\d]/g, '');
    let data = {phone_number: phone};
    const url = '/api/users/loyalty/phone/confirm/';
    $.ajax({
        url: url,
        method: "post",
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function (data) {
            $(".code-confirm-form").slideDown(200);
            $("#code-confirm").prop("required", true).focus();
            $(".submit_loyalty_registration").prop('disabled', false)
            $("#loyalty-phone-error").fadeOut(200).text()
            $(".error-registration-phone").text('')
            const dif = Math.round((new Date(data.resend_available).getTime() - new Date().getTime()) / 1000)
            getLoyaltyTimer(dif)
        },
        error: function (error) {
            console.error(error)
            $("#loyalty-phone-error").fadeIn(200).text(error.responseJSON.confirmation_code[0])
        },
    })
});

$(document).on("submit", ".users-loyalty-register", function (e) {
    e.preventDefault();
    let formData = new FormData(this);
    const url = $(this).data("url");
    const data = {
        ...Object.fromEntries(formData),
        phone: $("#loyalty-phone").val().replace(/[^+\d]/g, '')
    }
    if (!data.first_name.length || !data.last_name.length) {
        $("#loyalty-submit-error").fadeIn(200)
        return
    }
    $.ajax({
        url: url,
        method: "post",
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function (data) {
            if (data?.active) {
                location.reload();
            }
        },
        error: function (error) {
            console.error(error)
            const errorMsg = error.responseJSON?.error_messages?.confirmation_code?.[0] || error.responseJSON?.phone?.[0]
            if (errorMsg) {
                $("#loyalty-phone-error").fadeIn(200).text(errorMsg)
            }
        },
    })
});

$(document).on("keydown", "#loyalty-phone", function() {
    const value = $(this).val().replace(/[^+\d]/g, '');
    if (value.length > 9) {
        $("#loyalty-phone-confirm").attr("disabled", false)
    } else {
        $("#loyalty-phone-confirm").attr("disabled", true)
    }
});

$(document).ready(function() {
    if ($("#loyalty-phone") && $("#loyalty-phone").val() && $("#loyalty-phone").val().replace(/[^+\d]/g, '').length > 9) {
        $("#loyalty-phone-confirm").attr("disabled", false)
    }
});

const getNoun = (number, one, two, five) => {
    let n = Math.abs(number)
    n %= 100
    if (n >= 5 && n <= 20) {
        return five
    }
    n %= 10
    if (n === 1) {
        return one
    }
    if (n >= 2 && n <= 4) {
        return two
    }
    return five
}

const getDate = (value) => {
    const options = {
        day: 'numeric',
        month: 'numeric',
        year: 'numeric',
    }
    const date = new Date(value)
    return date.toLocaleString('ru', options)
}

if (document.querySelector(".loyalty-bonus-amount")) {
    const listBonusAmount = document.querySelectorAll(".loyalty-bonus-amount")

    listBonusAmount.forEach((bonus) => {
        const amountBons = bonus.getAttribute("data-bonus-amount")
        let value
        if (window.location.href.includes("/en/")) {
            value = getNoun(amountBons, 'point', 'points', 'points')
        } else {
            value = getNoun(amountBons, 'балл', 'балла', 'баллов')
        }
        bonus.nextElementSibling.innerHTML = value
    })
}

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

